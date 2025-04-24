import mido
import numpy as np
from collections.abc import Callable
from DMXEnttecPro import Controller
from fixtures import *
from globals import *

@dataclass
class MidiButton:
    note: int
    function_name: str
    function: Callable
    state: bool



def all_off():
    pass

def main():
    mido.set_backend('mido.backends.pygame')
    names = mido.get_input_names()
    korg_idx = names.index('nanoPAD2')
    mode = "color"

    all_lights = Universe([], Controller('COM6'))
    
    all_lights.add_fixture(strobe)
    all_lights.add_fixture(disco_ball)
    all_lights.add_fixture(fog_machine)
    # all_lights.add_fixture(par_lights)
    # all_lights.add_fixture(led_bars)

    FOG_CHANNEL = 19

    print(all_lights.fixtures)
    all_lights.current_color = colors[2]
    all_lights.set_all_colors(all_lights.current_color)

    pad_x = 0
    pad_y = 0

    buttons = []
    buttons.append(MidiButton(note=36, function_name="blue", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=37, function_name="red", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=39, function_name="color_swap", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=38, function_name="blackout", function=all_lights.blackout, state=False))
    buttons.append(MidiButton(note=41, function_name="color_drift", function=all_lights.color_fade, state=False))
    buttons.append(MidiButton(note=40, function_name="color_strobe", function=all_lights.cyle_thru_colors, state=False))
    buttons.append(MidiButton(note=42, function_name="chase_to_color", function=all_lights.led_chase_to2, state=False))
    buttons.append(MidiButton(note=43, function_name="strobe_percent", function=all_lights.set_strobe_percent, state=False))
    buttons.append(MidiButton(note=44, function_name="fog_on", function=all_lights.set_channel_value, state=False))
    buttons.append(MidiButton(note=45, function_name="fog_off", function=all_lights.set_channel_value, state=False))
    buttons.append(MidiButton(note=46, function_name="sparkle", function=all_lights.sparkle_in_led_bars, state=False))
    buttons.append(MidiButton(note=47, function_name="rainbow_leds", function=all_lights.rainbow_sparkle_led_bars, state=False))
    buttons.append(MidiButton(note=48, function_name="waves_led", function=all_lights.waves_led_bars, state=False))

    #TURN STROBE ON OR OFF
    buttons.append(MidiButton(note=50, function_name="toggle_strobe", function=all_lights.toggle_strobe, state=False))



    with mido.open_input(names[korg_idx]) as inport:
        for msg in inport:            
            message = msg.dict()

            if message['type'] == 'note_on':
                # all_lights.blackout()
                if message['note'] not in [44, 45]:
                    end_repeated_call()
                all_lights.set_strobe_percent(0)
                #FIND WHICH BUTTON WAS PRESSED
                button = next((i for i in buttons if i.note == message['note']), None)
            
                try:
                    print(f"Executing {button.function_name}, pad note {str(button.note)}")
                    # print(f"\t{message['note']}")
                    #IF BUTTON IS COLOR, SET COLORS
                    if any(search.name == button.function_name for search in colors):
                        button.function(color=next((i for i in colors if i.name == button.function_name), None))

                    #RANDOMLY SWAP BETWEEN COLORS
                    elif button.function_name == "color_swap":
                        button.function(color=colors[np.random.randint(0, len(colors))])

                    #COLOR DRIFT
                    elif button.function_name == "color_drift":
                        #GET BPM SOMEHOW
                        #FIX THE DOUBLING UP WITH THE BOOL (press twice quick)
                        drift_duration = input("How long to fade? (seconds): ")
                        drift_duration = float(drift_duration)
                        pause_duration = input("How long to pause at color? (seconds): ")
                        pause_duration = float(pause_duration)
                        call_repeatedly(drift_duration + pause_duration, all_lights.color_fade, colors, drift_duration, True)           

                    elif button.function_name == "color_strobe":
                        bpm = input("Input BPM: ")
                        bpm = int(bpm)
                        call_repeatedly(1/(bpm/60), all_lights.cyle_thru_colors, colors, 1)

                    elif button.function_name == "chase_to_color":
                        duration = input("How long to chase to color? (seconds): ")
                        duration = float(duration)
                        all_lights.led_chase_to2(colors[np.random.randint(0, len(colors))], duration)

                    elif button.function_name == "sparkle":
                        duration = input("How long to sparkle to color? (seconds): ")
                        duration = float(duration)
                        all_lights.sparkle_in_led_bars(colors[np.random.randint(0, len(colors))], duration)

                    elif button.function_name == "rainbow_leds":
                        pixel_width = input("How wide of pixels? (1-~72): ")
                        pixel_width = int(pixel_width)
                        pause_duration = input("How long to pause between? (seconds): ")
                        pause_duration = float(pause_duration)
                        call_repeatedly(pause_duration, all_lights.rainbow_sparkle_led_bars, pixel_width, pause_duration, colors) 

                    elif button.function_name == "waves_led":
                        pixel_width = input("How wide of waves? (1-~72): ")
                        pixel_width = int(pixel_width)
                        pixel_gap = input("How wide of gap_between? (1-~72): ")
                        pixel_gap = int(pixel_gap)
                        pause_duration = input("Any delay? (seconds): ")
                        pause_duration = float(pause_duration)
                        color=random.choice(colors)
                        call_repeatedly(pause_duration, all_lights.waves_led_bars, pixel_width, pixel_gap, pause_duration, color)       

                    elif button.function_name == "strobe_percent":
                        percent = input("What percentage strobe speed?: ")
                        button.function(int(percent))

                    elif button.function_name == "fog_on":
                        button.function(FOG_CHANNEL, 255)

                    elif button.function_name == "fog_off":
                        button.function(FOG_CHANNEL, 0)

                    #CALL ANY BUTTON FUNCTION THAT TAKES NO ARGS
                    else:
                        button.function()
                except AttributeError as e:
                    print("button has no function")
                    print(e)
                    pass
                except ValueError as e:
                    print("invalid input, try again")
                    print(e)
                    pass

            #XY PAD        
            elif message['type'] == 'control_change':
                if message['control'] == 2:
                    pad_y = message['value']
                elif message['control'] == 1:
                    pad_x = message['value']
                # print(message)
                if mode=="color":
                    all_lights.xy_pad(pad_x, pad_y)
                elif mode=="spin":
                    all_lights.xy_pad_spin(pad_x, pad_y)

            elif message['type'] == 'sysex':
                if message['data'][-1] == 0:
                    print("XY pad in color mode")
                    mode="color"
                if message['data'][-1] == 1:
                    print("XY pad in spin mode")
                    mode="spin"

            print(message)



if __name__ == "__main__":
    main()


