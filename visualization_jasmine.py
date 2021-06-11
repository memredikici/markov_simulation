import numpy as np
import pandas as pd
import cv2
import random
from datetime import datetime
import time
from classes import Supermarket

from pandas.io.parsers import read_csv

TILE_SIZE = 32
OFS = 50

MARKET = """
##################
##..............##
#D..Dd..ds..sb..b#
#D..Dd..ds..sb..b#
#D..Dd..ds..sb..b#
#D..Dd..ds..sb..b#
#D..Dd..ds..sb..b#
##...............#
##..C#..C#..C#...#
##..##..##..##...#
##...............#
##############GG##
""".strip()


class SupermarketMap:
    """Visualizes the supermarket background"""

    def __init__(self, layout, tiles, opening, closing):
        """
        layout : a string with each character representing a tile
        tile   : a numpy array containing the tile image
        """
        self.tiles = tiles
        self.contents = [list(row) for row in layout.split("\n")]
        self.xsize = len(self.contents[0])
        self.ysize = len(self.contents)
        self.image = np.zeros(
            (self.ysize * TILE_SIZE, self.xsize * TILE_SIZE, 3), dtype=np.uint8
        )
        self.prepare_map()
        self.opening = 0
        self.closing = 0

    def extract_tile(self, row, col):
        y = (row - 1) * 32
        x = (col - 1) * 32
        return self.tiles[y:y + 32, x:x + 32]

    def get_tile(self, char):
        """returns the array for a given tile character"""
        if char == "#":
            return self.extract_tile(1, 1)
            # return self.tiles[0:32, 0:32]
        elif char == "G":
            return self.extract_tile(8, 4)
            # return self.tiles[7 * 32: 8 * 32, 3 * 32: 4 * 32]
        elif char == "C":
            return self.extract_tile(3, 9)
            # return self.tiles[2 * 32: 3 * 32, 8 * 32: 9 * 32]
        elif char == "b":
            return self.extract_tile(1, 5)
            # return self.tiles[0: 32, 4 * 32: 5 * 32]
        elif char == "s":
            return self.extract_tile(5, 10)
        elif char == "d":  # dairy
            return self.extract_tile(6, 7)
        elif char == "D":  # drinks
            return self.extract_tile(7, 14)
        else:
            return self.extract_tile(2, 3)
            # return self.tiles[32:64, 64:96]

    def prepare_map(self):
        """prepares the entire image as a big numpy array"""
        for y, row in enumerate(self.contents):
            for x, tile in enumerate(row):
                bm = self.get_tile(tile)
                self.image[
                y * TILE_SIZE: (y + 1) * TILE_SIZE,
                x * TILE_SIZE: (x + 1) * TILE_SIZE,
                ] = bm

    def draw(self, frame, offset=OFS):
        """
        draws the image into a frame
        offset pixels from the top left corner
        """
        frame[
        OFS: OFS + self.image.shape[0], OFS: OFS + self.image.shape[1]
        ] = self.image

    def write_image(self, filename):
        """writes the image into a file"""
        cv2.imwrite(filename, self.image)


class Customer:

    def __init__(self, terrain_map, image):

        self.terrain_map = terrain_map
        self.location = 0
        self.image = image
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f'Customer'

    def draw(self, frame, location):
        if location == 'dairy':
            self.x = random.choice([6, 7])
            self.y = random.choice([2, 6])  # 2,6

        elif location == 'drinks':
            self.x = random.choice([2, 3])  # 2,3
            self.y = random.choice([2, 6])  # 2,6
            print(self.x, self.y)

        elif location == 'fruit':
            self.x = random.choice([14, 15])  # 14,15
            self.y = random.choice([2, 6])  # 2,6
        elif location == 'spices':
            self.x = random.choice([10, 11])  # 10,11
            self.y = random.choice([2, 6])  # 2,6
        elif location == 'checkout':
            self.x = 5  # 10,11
            # self.x = random.choice([4,5])# 10,11
            self.y = random.choice([8, 10])  # 2,6
        print(self.x, self.y, location)
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE
        # frame[ypos: ypos+32, xpos: xpos+ 32] = self.image
        frame[ypos: ypos + self.image.shape[0], xpos: xpos + self.image.shape[1]] = self.image
        # overlay the Customer image / sprite onto the frame

    def move(self, direction):
        newx = self.x
        newy = self.y
        if direction == 'up':
            newy -= 1

        if self.terrain_map.contents[newy][newx] == '.':
            self.x = newx
            self.y = newy


if __name__ == "__main__":

    background = np.zeros((484, 676, 3), np.uint8)
    tiles = cv2.imread("tiles.png")
    simulated_table = read_csv('./data/Simulated_Market_Table/simulated_market_table_average.csv',
                               parse_dates=['timestamp'])
    # print(simulated_table)
    opening = simulated_table['timestamp'].iloc[0]
    closing = simulated_table['timestamp'].iloc[-1]
    #print(opening)
    section = simulated_table.loc[simulated_table['customer_no'] == 1]['location']


    # print(type(section), section)

    def extract(row, col, tiles):
        y = (row - 1) * 32
        x = (col - 1) * 32
        return tiles[y:y + 32, x:x + 32]


    customer_figure = extract(8, 2, tiles)
    market = SupermarketMap(MARKET, tiles, opening, closing)
    customer = Customer(market, customer_figure)
    # customer2 = Customer(market,customer_figure,15,8)
    minute = simulated_table['timestamp'].loc[simulated_table['timestamp'] == '07:00:00']
    # minute = minute.to_timestamp()
    # print('before', (minute.iloc[0]))
    #
    # print('opening', type(opening))
    # print('minute', type(minute))
    # print('closing', type(closing))
    #
    # print(simulated_table['timestamp'].iloc[1])
    # print(len(simulated_table['timestamp']))

    # minute = datetime.strptime(minute, '%H:%M:%S')
    # print('after', type(minute))
    # opening = datetime.strptime(opening, '%H:%M:%S')
    # closing = datetime.strptime(closing, '%H:%M:%S')
    for i in range(0, len(simulated_table['timestamp'])):
        time_current = simulated_table['timestamp'].iloc[i]
        frame = background.copy()
        market.draw(frame)

        for customer_index in simulated_table.loc[simulated_table['timestamp'] == time_current]['customer_no']:
            section = simulated_table.loc[simulated_table['customer_no'] == customer_index]['location']
            for i in section:
                print(i)
                customer.draw(frame, i)
                cv2.imshow("frame", frame)
                time.sleep(0.05)

        key = chr(cv2.waitKey(1) & 0xFF)

        if key == "q":
            break
        if key == "w":
            customer.move('up')
        # customer2.move('up')
        #minute = minute + datetime.timedelta(minutes=1)
        #market.write_image("supermarket.png")

    cv2.destroyAllWindows()