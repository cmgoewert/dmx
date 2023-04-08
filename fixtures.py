from dataclasses import dataclass
from DMXEnttecPro import Controller
import time
import random

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

    def set_strobe(self, percent):
        percent_from_255 = round((255 * percent) / 100)
        #custom rules, theres gotta be a better way!
        if self.name=="strobe":
            strobe_fixture_percent_val = 128 + round((122 * percent) / 100) if percent > 0 else 0
            for channel in self.channels:
                if channel.type == "strobe":
                    channel.update_value(strobe_fixture_percent_val)
            return

        for channel in self.channels:
            if channel.type == "strobe":
                channel.update_value(percent_from_255)

    def find_rgb(self, rgb_str, value):
        for channel in self.channels:
            if channel.type == rgb_str:
                channel.update_value(value)

@dataclass
class Universe:
    fixtures: list[Fixture]
    controller: Controller = Controller('COM4')
    filled_channels: int = 0

    def __update_and_submit(self):
        for fixture in self.fixtures:
            for channel in fixture.channels:
                print(f"{fixture.name}: setting channel {channel.index} to {channel.value}")
                self.controller.set_channel(channel.index, channel.value)
        
        self.controller.submit()

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

    def set_blue(self):
        for fixture in self.fixtures:
            if fixture.name is "led_bar":
                fixture.find_rgb("blue", 100)
                fixture.find_rgb("red", 0)
                fixture.find_rgb("green", 0)
            else:
                fixture.find_rgb("blue", 255)
                fixture.find_rgb("red", 0)
                fixture.find_rgb("green", 0)

        self.__update_and_submit()

    def set_purple(self):
        for fixture in self.fixtures:
            if fixture.name is "led_bar":
                fixture.find_rgb("blue", 100)
                fixture.find_rgb("red", 100)
                fixture.find_rgb("green", 0)
            else:
                fixture.find_rgb("blue", 255)
                fixture.find_rgb("red", 255)
                fixture.find_rgb("green", 0)

        self.__update_and_submit()

    def set_red(self):
        for fixture in self.fixtures:
            if fixture.name is "led_bar":
                fixture.find_rgb("blue", 0)
                fixture.find_rgb("red", 100)
                fixture.find_rgb("green", 0)
            else:
                fixture.find_rgb("blue", 0)
                fixture.find_rgb("red", 255)
                fixture.find_rgb("green", 0)

        self.__update_and_submit()

    def set_green(self):
        for fixture in self.fixtures:
            fixture.find_rgb("blue", 0)
            fixture.find_rgb("red", 0)
            fixture.find_rgb("green", 255)

        self.__update_and_submit()
        
    def set_strobe_percent(self, percent):
        for fixture in self.fixtures:
            fixture.set_strobe(percent)

        self.__update_and_submit()

    def blackout(self):
        #sets all values to 0
        self.controller.clear_channels()

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
            
            










