import argparse
import os
import numpy as np
import twmap
import curses
from curses import wrapper
from collections import defaultdict

# Supported layers atm: game, front, tele
# Supported tiles are defined below
game_dict = defaultdict(lambda: "unk", {
    0: "air",
    1: "hook",
    2: "kill",
    3: "unhook",
    9: "freeze",
    11: "unfreeze",
    12: "deep",
    12: "undeep",
})

front_dict = defaultdict(lambda: "unk", {
    2: "kill",
    4: "kill",
    5: "hookthrough",
    9: "freeze",
    11: "unfreeze",
    12: "deep",
    12: "undeep",
    98: "yellow_telegun",
    99: "blue_telegun",
})

tele_dict = defaultdict(lambda: "unk", {
    10: "red_from",
    26: "blue_from",
    27: "to",
    29: "checkpoint",
    30: "cto",
    31: "blue_cfrm",
    63: "red_cfrm",
})


def load_map(map_path):
    if not os.path.exists(map_path):
        raise FileNotFoundError(f"The map file at {map_path} does not exist.")
    with open(map_path, 'r') as file:
        map_data = twmap.Map(map_path)
    return map_data

def parse_map(map_data):
    game_layer = map_data.game_layer().tiles
    if map_data.front_layer() is not None:
        front_layer = map_data.front_layer().tiles
    else:
        front_layer = np.zeros(game_layer.shape, dtype=np.uint8)
    if map_data.tele_layer() is not None:
        tele_layer = map_data.tele_layer().tiles
    else:
        tele_layer = np.zeros(game_layer.shape, dtype=np.uint8)

    game_tiles = game_layer[:,:,0]
    game_ids = game_layer[:,:,1]
    front_tiles = front_layer[:,:,0]
    front_ids = front_layer[:,:,1]
    tele_tiles = tele_layer[:,:,0]
    tele_ids = tele_layer[:,:,1]

    height = game_layer.shape[0]
    width = game_layer.shape[1]
    tiles = [["uk" for _ in range(width)] for _ in range(height)]
    colors = [[2 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            game_tile = game_dict[game_tiles[y, x]]
            game_id = game_ids[y, x]
            front_tile = front_dict[front_tiles[y, x]]
            front_id = front_ids[y, x]
            tele_tile = tele_dict[tele_tiles[y, x]]
            tele_id = tele_ids[y, x]

            game_str, game_color = tile(game_tile, game_id)
            if tele_tile != "unk":
                tele_str, tele_color = tile(tele_tile, tele_id)
                tiles[y][x] = tele_str
                colors[y][x] = tele_color
            elif front_tile != "unk":
                front_str, front_color = tile(front_tile, front_id)
                tiles[y][x] = front_str
                colors[y][x] = front_color
            else:
                tiles[y][x] = game_str
                colors[y][x] = game_color

    return tiles, colors, height, width

def info_str(info: int):
    info_str = str(info)
    if len(info_str) == 1:
        info_str = " " + info_str
    elif len(info_str) > 2:
        info_str = info_str[-2:]
    return info_str

def sc(color: int): # scale color (sc)
    return int(color * 3.92)

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    if curses.can_change_color():
        curses.init_color(24, sc(157), sc(141), sc(102)) # hook
        curses.init_color(25, sc(125), sc(126), sc(134)) # unhook
        curses.init_color(26, sc(160), sc(160), sc(150)) # air
        curses.init_color(27, sc(67), sc(67), sc(67)) # freeze
        curses.init_pair(1, 26, 26) # air
        curses.init_pair(2, 24, -1) # hook
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) # kill
        curses.init_pair(4, 25, -1) # unhook
        curses.init_pair(5, 27, 27) # freeze
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW) # unfreeze
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # deep
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_YELLOW) # undeep
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE) # unused
        curses.init_pair(10, curses.COLOR_BLUE, curses.COLOR_RED) # red_from
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLUE) # blue_from
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE) # checkpoint
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW) # cto
    else:
        curses.init_pair(1, curses.COLOR_BLUE, -1) # air
        curses.init_pair(2, curses.COLOR_YELLOW, -1) # hook
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) # kill
        curses.init_pair(4, curses.COLOR_WHITE, -1) # unhook
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK) # freeze
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW) # unfreeze
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # deep
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_YELLOW) # undeep
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE) # unused
        curses.init_pair(10, curses.COLOR_BLUE, curses.COLOR_RED) # red_from
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLUE) # blue_from
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE) # checkpoint
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW) # cto

def tile(type: str, info: int = None):
    match type:
        case "air":
            return "  ", 1
            #return colored("  ", "light_blue")1
        case "hook":
            return "██", 2
            #return colored("██", "yellow")2
        case "kill":
            return "><", 3
            #return colored("><", "white", "on_red")3
        case "unhook":
            return "██", 4
            # return colored("██", "white")4
        case "freeze":
            return "  ", 5
            # return colored("☀ ", "white", "on_dark_grey")5
        case "unfreeze":
            return "☀ ", 6
            # return colored("☀ ", "black", "on_yellow")6
        case "deep":
            return "☀ ", 7
            # return colored("☀ ", "red", "on_dark_grey")7
        case "undeep":
            return "☀ ", 8
            # return colored("☀ ", "red", "on_yellow")8
        case "hookthrough":
            return "▀▄", 4
            # return colored("▀▄", "white", "on_blue")9
        case "red_from":
            info = info_str(info)
            return info, 10
            # return colored(info, "blue", "on_red")10
        case "blue_from":
            info = info_str(info)
            return info, 11
            # return colored(info, "red", "on_blue")11
        case "red_cfrm":
            return "cf", 10
            # return colored("cf", "blue", "on_red")10
        case "blue_cfrm":
            return "cf", 11
            # return colored("cf", "red", "on_blue")11
        case "checkpoint":
            info = info_str(info)
            return info, 12
            # return colored(info, "black", "on_white")12
        case "to":
            info = info_str(info)
            return info, 13
            # return colored(info, "white", "on_yellow")13
        case "cto":
            info = info_str(info)
            return info, 13
            # return colored(info, "white", "on_yellow")13
        case _:
            return "??", 2
            # return colored("??", "yellow")2
        
def display_map(stdscr, map_content, args):
    height = args.height
    width = args.width
    border = args.border
    map_name = args.map

    max_y, max_x = stdscr.getmaxyx()
    tiles, colors, map_height, map_width = map_content
    # tiles is a string of things to render

    if width == -1:
        width = max_x // 2
    if height == -1:
        height = max_y // 2

    init_colors()

    start_row = map_height // 2
    start_col = map_width // 2

    while True:
        stdscr.clear()
        if border:
            border_line = '+' + '-' * (width * 2) + '+'
            stdscr.addstr(0, 0, border_line)
            stdscr.addstr(0, 3, map_name)
        for row in range(height):
            if start_row + row >= map_height:
                break
            for col in range(width):
                if start_col + col >= map_width:
                    break
                tile = tiles[start_row + row][start_col + col]
                color = colors[start_row + row][start_col + col]
                stdscr.addstr(row+1, col * 2, tile, curses.color_pair(color))
        if border:
            stdscr.addstr(height+2, 0, border_line)

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('w') and start_row > 0 + args.step:
            start_row -= args.step
        elif key == ord('s') and start_row < map_height - height - args.step:
            start_row += args.step
        elif key == ord('a') and start_col > 0 + args.step:
            start_col -= args.step
        elif key == ord('d') and start_col < map_width - width - args.step:
            start_col += args.step
        elif key == 3:  # Ctrl+C
            raise SystemExit

def wrapped_main(stdscr):
    args = parse_args()
    map_content = parse_map(load_map(args.map))
    display_map(stdscr, map_content, args)

def parse_args():
    parser = argparse.ArgumentParser(description="Load a tw map file.")
    parser.add_argument('--map', type=str, required=True, help='Path to the map file')
    parser.add_argument('--step', type=int, default=3, help='Step size of the view window')
    parser.add_argument('--width', type=int, default=-1, help='Width of the view window')
    parser.add_argument('--height', type=int, default=-1, help='Height of the view window')
    parser.add_argument('--border', type=bool, default=True, help='Enable or disable border of view window')
    return parser.parse_args()

def run():
    curses.wrapper(wrapped_main)

if __name__ == "__main__":
    curses.wrapper(wrapped_main)

