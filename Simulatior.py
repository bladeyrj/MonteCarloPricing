from data_reader import dataReader
from mcts import MCTS
import numpy as np

def policy_value_fn(state):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    action_probs = np.ones(len(state.availables))/len(state.availables)
    return zip(state.availables, action_probs), 0

class State(object):
    def __init__(self):
        self.piecesA = 10
        self.piecesB = 10
        self.piecesC = 10
        self.income = 0
        self.availables = [999, 899, 799, 699, 599, 499, 399, 299, 199, 99]
        self.price_list = []

    def simulation_end(self):
        if self.piecesA + self.piecesB + self.piecesC == 0:
            return True, self.income
        else:
            return False, -1
        

class Simulator(object):
    def __init__(self, state, c_puct=5, n_weeks=2000):
        self.state = state
        self.c_puct = c_puct
        self.n_weeks = n_weeks
    
    def get_result(self, data):
        self.n_weeks = len(data)
        self.mcts = MCTS(policy_value_fn, self.c_puct, self.n_weeks)
        price = self.mcts.get_move(self.state)
        self.mcts.update_with_move(-1)
        return price



def run():
    state = State()
    simulator = Simulator(state)
    # load data
    data_reader = dataReader()
    data = data_reader.get_parsed_data()

    simulator.get_result(data)

if __name__ == "__main__":
    run()