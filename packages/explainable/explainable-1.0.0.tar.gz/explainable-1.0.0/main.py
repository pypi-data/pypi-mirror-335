import time

import explainable

from visualisation import draw

explainable.init(draw)


def main():
    explainable.add_context("main")

    initial_cells = list(range(10))

    for _ in range(1000):
        initial_cells[0] += 1
        time.sleep(1)


if __name__ == "__main__":
    main()
