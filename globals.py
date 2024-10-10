from fixtures import *

colors = [
    Color("white", red=255, green=255, blue=255, spotlight_num=1),
    Color("green", red=0, green=255, blue=0, spotlight_num=10),
    Color("red", red=255, green=0, blue=0, spotlight_num=18),
    Color("blue", red=0, green=0, blue=255, spotlight_num=26),
    Color("yellow", red=255, green=255, blue=0, spotlight_num=34),
    Color("pink", red=255, green=105, blue=181, spotlight_num=42),
    Color("dark aqua", red=0, green=255, blue=255, spotlight_num=50),
    Color("light magenta", red=237, green=8, blue=237, spotlight_num=58),
    Color("sky blue", red=135, green=206, blue=250, spotlight_num=68),
    Color("magenta", red=204, green=0, blue=204, spotlight_num=74),
    Color("violet", red=237, green=130, blue=237, spotlight_num=82),
    Color("purple", red=160, green=48, blue=255, spotlight_num=90),
    Color("canary yellow", red=255, green=204, blue=17, spotlight_num=98),
    Color("lime green", red=0, green=205, blue=50, spotlight_num=106),
    Color("orange", red=255, green=165, blue=0, spotlight_num=114),
    Color("light aqua", red=0, green=219, blue=255, spotlight_num=122),
]

par_lights = Fixture (
    name="par",
    channel_count=7,
    channels=[
        Channel(1, 255, "brightness", ""),
        Channel(2, 0, "red", ""),
        Channel(3, 0, "green", ""),
        Channel(4, 0, "blue", ""),
        Channel(5, 0, "rgb", ""),
        Channel(6, 0, "strobe", ""),
        Channel(7, 0, "mode", "")
    ]
)

strobe = Fixture(
    name="strobe", 
    channel_count=6, 
    channels=[
        Channel(1, 255, "brightness", ""),
        Channel(2, 0, "strobe", "0-5 open, rest are effects, 128-250 is standard range"),
        Channel(3, 0, "red", ""),
        Channel(4, 0, "green", ""),
        Channel(5, 0, "blue", ""),
        Channel(6, 0, "auto_sound", "")
    ],
    strobe_range=(128,250)
)

fog_machine = Fixture(
    name="fog machine",
    channel_count=7,
    channels=[
        Channel(1, 0, "fog", ""),
        Channel(2, 0, "red", ""),
        Channel(3, 0, "green", ""),
        Channel(4, 0, "blue", ""),
        Channel(5, 0, "strobe", ""),
        Channel(6, 0, "stupid", "NO THIS IS A LIE, its some color changing value: 0-9 is off, can be adjusted 10-250, 250+ is music"),
        Channel(7, 0, "auto_sound", "")
    ]
)

led_bars = Fixture(
    name="led_bar",
    channel_count=432,
    channels = generate_led_bar_channels(1),
    color_max = 100
)

mirror_spotlights = Fixture(
    name="spotlights",
    channel_count=9,
    channels = [
        Channel(1, 0, "pan", ""),
        Channel(2, 0, "tilt", ""),
        Channel(3, 0, "rgb", ""),
        Channel(4, 0, "gobo", "this is a pattern, 254 is sound active slow, 255 sound active fast"),
        Channel(5, 0, "strobe", "soundactive 32-47, slow-fast is 48-239"),
        Channel(6, 0, "mirror_speed", "slow->fast"),
        Channel(7, 0, "mirror_movement", ""),
        Channel(8, 0, "laser", ""),
        Channel(9, 0, "special", "")
    ],
    strobe_range=(48,239)
)