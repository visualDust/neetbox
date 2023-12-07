from random import random
from threading import Thread
from time import sleep

import neetbox
from neetbox import logger

EMPTY = " "
BODY = "o"
HEAD = "O"
FOOD = "x"

MAP_WIDTH, MAP_HEIGHT = 20, 10

game_running = False

# logger.info("starting")


@neetbox.action(blocking=False)
def snake_game():
    global game_running
    if game_running:
        logger.err("game already running")
        return
    game_running = True
    try:
        game()
    except Exception as e:
        logger.err(e)
    game_running = False


def game():
    cur_direction = (1, 0)
    gamemap = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    bodies = []
    cur_head = 3, 3
    cur_direction = (1, 0)

    @neetbox.action()
    def left():
        nonlocal cur_direction
        cur_direction = (-1, 0)

    @neetbox.action()
    def down():
        nonlocal cur_direction
        cur_direction = (0, 1)

    @neetbox.action()
    def up():
        nonlocal cur_direction
        cur_direction = (0, -1)

    @neetbox.action()
    def right():
        nonlocal cur_direction
        cur_direction = (1, 0)

    def main():
        logger.info("===================snake game===================")
        put_head((3, 3))
        put_head((4, 3))
        put_head((5, 3))
        place_food()
        while True:
            print_map()
            logger.info(f"head = {cur_head}, direction = {cur_direction}")
            sleep(1)
            next_pos = (cur_head[0] + cur_direction[0], cur_head[1] + cur_direction[1])
            next_thing = get_map(next_pos)
            if next_thing in [BODY, None]:
                logger.err("GAME OVER")
                logger.info(f"SCORE = {len(bodies)}")
                break

            put_head(next_pos)
            if next_thing == FOOD:
                place_food()
            else:
                remove_tail()

    def put_head(pos):
        nonlocal cur_head
        set_map(cur_head, BODY)
        set_map(pos, HEAD)
        cur_head = pos
        bodies.append(pos)

    def remove_tail():
        set_map(bodies[0], EMPTY)
        bodies.remove(bodies[0])

    def place_food():
        while True:
            x, y = int(random() * MAP_WIDTH), int(random() * MAP_HEIGHT)
            if get_map((x, y)) != EMPTY:
                continue
            set_map((x, y), FOOD)
            break

    def get_map(pos):
        x, y = pos
        return gamemap[y][x] if (0 <= x < MAP_WIDTH) and (0 <= y < MAP_HEIGHT) else None

    def set_map(pos, val):
        x, y = pos
        gamemap[y][x] = val

    def print_map():
        logger.info("+ " + " ".join("-" * MAP_WIDTH) + " +")
        for y in range(MAP_HEIGHT):
            logger.info("| " + " ".join(gamemap[y]) + " |")
        logger.info("+ " + " ".join("-" * MAP_WIDTH) + " +")

    main()


if __name__ == "__main__":
    while True:
        sleep(1000)
