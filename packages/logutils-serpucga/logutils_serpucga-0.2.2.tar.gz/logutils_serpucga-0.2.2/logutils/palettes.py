# Escape codes for terminal colors
# Reset color
reset = "\x1b[0m"

bold_blue = "\x1b[38;2;25;128;255;1m"  # rgb(25, 128, 255)
bold_dirty_water = "\x1b[38;2;95;135;135;1m"  # rgb(95, 135, 135)
bold_sand = "\x1b[38;2;246;239;236;1m"  # rgb(246,239,236)
bold_grey = "\x1b[38;2;124;124;124;1m"  # rgb(124, 124, 124)
bold_dark_grey = "\x1b[38;2;74;74;74;1m"  # rgb(74, 74, 74)
bold_lime_green = "\x1b[38;2;100;226;46m;1m"  # rgb(100, 226, 46)
bold_leaf_green = "\x1b[38;2;0;87;0;1m"  # rgb(0, 87, 0)
bold_lila = "\x1b[38;2;174;129;255m;1m"  # rgb(174, 129, 255)
bold_purple = "\x1b[38;2;135;0;175;1m"  # rgb(135, 0, 175)
bold_yellow = "\x1b[38;2;200;200;0;1m"  # rgb(200, 200, 0)
bold_dark_yellow = "\x1b[38;2;140;140;0;1m"  # rgb(140, 140, 0)
bold_cream = "\x1b[38;2;215;135;95;1m"  # rgb(215, 135, 95)
bold_dark_cream = "\x1b[38;2;160;105;55;1m"  # rgb(160, 105, 55)
bold_red = "\x1b[38;2;255;0;0;1m"  # rgb(255, 0, 0)
bold_dark_red = "\x1b[38;2;128;0;0;1m"  # rgb(128, 0, 0)

blue = "\x1b[38;2;25;128;255m"  # rgb(25, 128, 255)
dirty_water = "\x1b[38;2;95;135;135m"  # rgb(95, 135, 135)
sand = "\x1b[38;2;246;239;236m"  # rgb(246,239,236)
grey = "\x1b[38;2;124;124;124m"  # rgb(124, 124, 124)
dark_grey = "\x1b[38;2;74;74;74m"  # rgb(74, 74, 74)
lime_green = "\x1b[38;2;100;226;46m"  # rgb(100, 226, 46)
leaf_green = "\x1b[38;2;0;87;0m"  # rgb(0, 87, 0)
lila = "\x1b[38;2;174;129;255m"  # rgb(174, 129, 255)
purple = "\x1b[38;2;135;0;175m"  # rgb(135, 0, 175)
yellow = "\x1b[38;2;200;200;0m"  # rgb(200, 200, 0)
dark_yellow = "\x1b[38;2;140;140;0m"  # rgb(140, 140, 0)
cream = "\x1b[38;2;215;135;95m"  # rgb(215, 135, 95)
dark_cream = "\x1b[38;2;160;105;55m"  # rgb(160, 105, 55)
red = "\x1b[38;2;255;0;0m"  # rgb(255, 0, 0)
dark_red = "\x1b[38;2;128;0;0m"  # rgb(128, 0, 0)

background_red = "\x1b[48;2;255;0;0m"  # rgb(255, 0, 0)
background_dark_red = "\x1b[48;2;128;0;0m"  # rgb(128, 0, 0)


def get_palette(palette_name: str):
    if palette_name == "light":
        return {
            "time": leaf_green,  # rgb(0, 87, 0)
            "location": purple,  # rgb(135, 0, 175)
            "debug": bold_dark_grey,  # rgb(74, 74, 74)
            "info": bold_blue,  # rgb(25, 128, 255)
            "warning": bold_dark_yellow,  # rgb(140, 140, 0)
            "error": dark_red,  # rgb(128, 0, 0)
            "critical": background_dark_red,  # rgb(128, 0, 0)
            "text": bold_dark_cream,  # rgb(160, 105, 55)
        }
    else:
        return {
            "time": lime_green,  # rgb(100, 226, 46)
            "location": lila,  # rgb(174, 129, 255)
            "debug": grey,  # rgb(124, 124, 124)
            "info": blue,  # rgb(25, 128, 255)
            "warning": yellow,  # rgb(200, 200, 0)
            "error": red,  # rgb(255, 0, 0)
            "critical": background_red,  # rgb(255, 0, 0)
            "text": sand,  # rgb(246,239,236)
        }
