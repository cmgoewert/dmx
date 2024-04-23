from dataclasses import dataclass
from DMXEnttecPro import Controller
import time
import random
import multiprocessing
from threading import Event, Thread
from threading import Timer

continue_thread = False

# class RepeatedTimer(object):
#     def __init__(self, interval, function, *args, **kwargs):
#         self._timer     = None
#         self.interval   = interval
#         self.function   = function
#         self.args       = args
#         self.kwargs     = kwargs
#         self.is_running = False
#         self.start()

#     def _run(self):
#         self.is_running = False
#         self.start()
#         self.function(*self.args, **self.kwargs)

#     def start(self):
#         if not self.is_running:
#             self._timer = Timer(self.interval, self._run)
#             self._timer.start()
#             self.is_running = True

#     def stop(self):
#         self._timer.cancel()
#         self.is_running = False

def loop(interval, func, *args):
    while True: # the first call is in `interval` secs
        func(*args)
        time.sleep(interval)
        if continue_thread is False:
            return

def call_repeatedly(interval, func, *args):
    global continue_thread
    continue_thread = True
    process = Thread(target=loop, args=(interval, func, *args))
    process.start()

def end_repeated_call():
    print('\tending repeating call')
    global continue_thread
    continue_thread = False

@dataclass
class Color:
    name: str
    red: int
    green: int
    blue: int
    spotlight_num: int

def generate_led_bar_channels(starting_channel):
    channels = [] 
    
    for i in range(0, 145):
        channels.append(Channel(starting_channel,0,"green",""))
        starting_channel = starting_channel + 1

        channels.append(Channel(starting_channel,0,"red",""))
        starting_channel = starting_channel + 1
        
        channels.append(Channel(starting_channel,0,"blue",""))
        starting_channel = starting_channel + 1

    return channels

@dataclass
class Channel:
    index: int
    value: int
    type: str
    description: str

    def update_index(self, new_index):
        self.index = new_index

    def update_value(self, new_value):
        self.value = new_value

@dataclass
class Fixture:
    name: str
    channel_count: int
    channels: list[Channel]
    color_max: int = 255
    strobe_range: tuple = (0,255)

    def set_strobe(self, percent):
        diff = self.strobe_range[1] - self.strobe_range[0]
        percent_from_diff = round((diff * percent) / 100)
        #custom rules, theres gotta be a better way!
        value = self.strobe_range[0] + percent_from_diff
        if percent == 0:
            value = 0
        for channel in self.channels:
            if channel.type == "strobe":
                channel.update_value(value)

        # if self.name=="strobe":
        #     strobe_fixture_percent_val = 128 + round((122 * percent) / 100) if percent > 0 else 0
        #     for channel in self.channels:
        #         if channel.type == "strobe":
        #             channel.update_value(strobe_fixture_percent_val)
        #     return

        # for channel in self.channels:
        #     if channel.type == "strobe":
        #         channel.update_value(percent_from_255)

    def set_color(self, color):
        for channel in self.channels:
            if channel.type == "red":
                channel.update_value(int((color.red) / (255 / self.color_max)))
            if channel.type == "green":
                channel.update_value(int((color.green) / (255 / self.color_max)))
            if channel.type == "blue":
                channel.update_value(int((color.blue) / (255 / self.color_max)))
@dataclass
class Universe:
    fixtures: list[Fixture]
    controller: Controller
    filled_channels: int = 1
    random_prior_index = 0
    current_color = None

    def add_fixture(self, fixture):
        for channel in fixture.channels:
            channel.update_index(self.filled_channels)
            self.filled_channels =  self.filled_channels + 1
        self.fixtures.append(fixture)

    def __update_and_submit(self):
        for fixture in self.fixtures:
            for channel in fixture.channels:
                # print(f"{fixture.name}: setting channel {channel.index} to {channel.value}")
                self.controller.set_channel(channel.index, channel.value)
        
        self.controller.submit()

    def set_all_colors(self, color):
        for fixture in self.fixtures:
            fixture.set_color(color)

        self.current_color = color

        self.__update_and_submit()

    def blackout(self):
        #sets all values to 0
        self.controller.clear_channels()
        self.controller.submit()

    def set_strobe_percent(self, percent):
        for fixture in self.fixtures:
            fixture.set_strobe(percent)

        self.__update_and_submit()

    def cyle_thru_colors(self, colors, bpm):
        hz = 1 / (bpm / 60)
        color_index = random.randint(0,len(colors)-1)
        while color_index == self.random_prior_index:
            color_index = random.randint(0,len(colors)-1)
        self.random_prior_index = color_index
        self.set_all_colors(colors[color_index])

    def color_fade(self, colors, seconds, random_color=False):
        if random_color:
            color_index = random.randint(0,len(colors)-1)
            while color_index == self.random_prior_index:
                color_index = random.randint(0,len(colors)-1)
            self.random_prior_index = color_index
            new_color = colors[color_index]
        else:
            new_color = colors[0]

        iterations = seconds * 20
        count = 0

        if self.current_color is None:
            self.current_color = colors[0]
         
        current_red = self.current_color.red
        current_blue = self.current_color.blue
        current_green = self.current_color.green

        red_diff = new_color.red - current_red
        blue_diff = new_color.blue - current_blue
        green_diff = new_color.green - current_green

        red_jump = int(red_diff / iterations)
        blue_jump = int(blue_diff / iterations)
        green_jump = int(green_diff / iterations)

        while count < iterations:
            for fixture in self.fixtures:
                if fixture.name != "spotlights":
                    fixture.set_color(Color(
                        "temp",
                        current_red + red_jump,
                        current_green + green_jump,
                        current_blue + blue_jump,
                        0
                    ))

            current_red = current_red + red_jump
            current_blue = current_blue + blue_jump
            current_green = current_green + green_jump
            count = count + 1

            if count < iterations:
                red_jump = int((new_color.red - current_red) / (iterations - count))    
                green_jump = int((new_color.green - current_green) / (iterations - count))    
                blue_jump = int((new_color.blue - current_blue) / (iterations - count))    

            self.__update_and_submit()
            time.sleep(0.05)
        self.set_all_colors(new_color)

    def led_chase_to(self, color, duration):
        increment = duration / 144
        i = 1
        while i < 430:
            found_leds = False
            for fixture in self.fixtures:
                if fixture.name == "led_bar":
                    fixture.channels[i].value=color.green
                    i = i + 1
                    fixture.channels[i].value=color.blue
                    i = i + 1
                    fixture.channels[i].value=color.red
                    i = i + 1
                    found_leds = True
            if not found_leds:
                i = i + 3
            self.__update_and_submit()
            time.sleep(increment)
        self.set_all_colors(color)

    def xy_pad(self, x, y):

        x_blue_color = x*2
        y_red_color = y*2

        for fixture in self.fixtures:
            if fixture.name != "spotlights":
                fixture.set_color(Color(
                    "temp",
                    x_blue_color,
                    self.current_color.green,
                    y_red_color,
                    0
                ))
        self.__update_and_submit()

    def set_channel_value(self, channel_num, value):
        for fixture in self.fixtures:
            for channel in fixture.channels:
                if channel.index == channel_num:
                    channel.value = value
        self.__update_and_submit()






        

    def set_random_color_cycle(self, bpm):
        #i guess interupt the kernel?
        #update this with start stop control, : https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
        cycle_in_sec = (bpm / 60)
        while True:
            random_blue = random.randint(0,255)
            random_red = random.randint(0,255)
            random_green = random.randint(0,255)

            for fixture in self.fixtures:
                if fixture.name == "led_bar":
                    fixture.find_rgb("blue", int(random_blue / 2.55))
                    fixture.find_rgb("red", int(random_red / 2.55))
                    fixture.find_rgb("green", int(random_green / 2.55))
                else:
                    fixture.find_rgb("blue", random_blue)
                    fixture.find_rgb("red", random_red)
                    fixture.find_rgb("green", random_green)                    

            self.__update_and_submit()
            time.sleep(1 / cycle_in_sec)


        
    def set_strobe_percent(self, percent):
        for fixture in self.fixtures:
            fixture.set_strobe(percent)

        self.__update_and_submit()

    def chase_to_blue(self, duration):
        increment = duration / 144
        i = 1
        while i < 430:
            for fixture in self.fixtures:
                if fixture.name == "led_bar":
                    fixture.channels[i].value=0
                    i = i + 1
                    fixture.channels[i].value=255
                    i = i + 1
                    fixture.channels[i].value=0
                    i = i + 1
            self.__update_and_submit()
            time.sleep(increment)
        for fixture in self.fixtures:
            if fixture.name != "led_bar":
                fixture.find_rgb("blue", 255)
                fixture.find_rgb("red", 0)
                fixture.find_rgb("green", 0)
        self.__update_and_submit()

    def strobe_led_bar(self, duration):
        cycle_in_sec = (duration / 60)
        i = 0
        while True:
            for fixture in self.fixtures:
                if fixture.name == "led_bar":
                    if i % 2 == 0:
                        fixture.find_rgb("blue", 100)
                        fixture.find_rgb("red", 100)
                        fixture.find_rgb("green", 100) 
                    else:
                        fixture.find_rgb("blue", 0)
                        fixture.find_rgb("red", 0)
                        fixture.find_rgb("green", 0) 

            i = i+1
            self.__update_and_submit()
            time.sleep(1 / cycle_in_sec)
            
            










