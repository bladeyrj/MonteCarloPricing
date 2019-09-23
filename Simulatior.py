from data_reader import dataReader
from mcts import MCTSSeller as MCTS_Pure
from mcts_alphaZero import MCTSSeller as MCTS_Alpha
import numpy as np

dr = dataReader()

class State(object):
    def __init__(self):
        self.piecesA = 10
        self.piecesB = 10
        self.piecesC = 10
        self.revenue = 0
        self.availables = [999, 899, 799, 699, 599, 499, 399, 299, 199, 99]
        self.price = 999
        self.price_list = []
        self.week = 0

    def end_sim(self):
        if self.piecesA + self.piecesB + self.piecesC == 0:
            return True, self.revenue
        else:
            return False, -1
        
    def update_stock(self, price):
        pass

    def update_week(self, week):
        self.week = week

    def add_one_week(self):
        self.week += 1

class Simulator(object):
    def __init__(self, state):
        self.state = state
    
    def start_sim(self, data_reader, mcts_seller):
        self.data_reader = data_reader
        price_list = []
        for week in data_reader.get_weeks():
            self.state.update_week(week)
            price = mcts_seller.get_price()
            price_list.append(price)
            self.state.update_stock(price)
            end, revenue = self.state.end_sim()
            if end:
                print("Price list: " + price_list)
                print("Total revenue: " + revenue)


def run():
    state = State()
    simulator = Simulator(state)
    # load data
    data_reader = dataReader()
    mcts_seller = MCTS_Pure(c_puct=5, n_playout=1000)

    simulator.start_sim(data_reader, mcts_seller)

if __name__ == "__main__":
    print(dr.get_price_of_weekSKU(5, "A"))
    #run()