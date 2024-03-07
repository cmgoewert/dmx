import mido
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

    all_lights = Universe([], Controller('COM6'))
    all_lights.add_fixture(strobe)

    buttons = []
    buttons.append(MidiButton(note=36, function_name="blue", function=all_lights.set_all_colors, state=False))
    buttons.append(MidiButton(note=37, function_name="red", function=all_lights.set_all_colors, state=False))

    with mido.open_input(names[korg_idx]) as inport:
        for msg in inport:
            message = msg.dict()
            if message['type'] == 'note_on':
                all_lights.blackout()
                button = next((i for i in buttons if i.note == message['note']), None)
                button.function(color=next((i for i in colors if i.name == button.function_name), None))
                print(button)
            elif message['type'] == 'control_change':
                pass

if __name__ == "__main__":
    main()


