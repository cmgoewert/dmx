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

    all_lights = Universe([], Controller('COM3'))
    all_lights.add_fixture(fog_machine)
    all_lights.add_fixture(strobe)
    all_lights.add_fixture(par_lights)
    all_lights.add_fixture(led_bars)

    pad_x = 0
    pad_y = 0

    buttons = []
    buttons.append(MidiButton(note=36, function_name="blue", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=37, function_name="red", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=39, function_name="color_swap", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=38, function_name="blackout", function=all_lights.blackout, state=False))
    buttons.append(MidiButton(note=41, function_name="color_drift", function=all_lights.color_fade, state=False))
    buttons.append(MidiButton(note=40, function_name="color_strobe", function=all_lights.cyle_thru_colors, state=False))
    buttons.append(MidiButton(note=42, function_name="chase_to_color", function=all_lights.led_chase_to, state=False))
    buttons.append(MidiButton(note=43, function_name="strobe_percent", function=all_lights.set_strobe_percent, state=False))
    buttons.append(MidiButton(note=44, function_name="fog_on", function=all_lights.set_channel_value, state=False))
    buttons.append(MidiButton(note=45, function_name="fog_off", function=all_lights.set_channel_value, state=False))

    FOG_CHANNEL = 1

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
                print(f"Executing {button.function_name}")
                print(f"\t{message['note']}")
            
                try:
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
                        all_lights.led_chase_to(colors[np.random.randint(0, len(colors))], duration)

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
                print(message)
                all_lights.xy_pad(pad_x, pad_y)

if __name__ == "__main__":
    main()


