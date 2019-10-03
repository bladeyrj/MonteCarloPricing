import pandas as pd
import numpy as np
import random
import math
import copy
import sys
import os
import datetime
from ast import literal_eval

def expand_tree(tree, node):
    if len(tree[node]["Child"]) == 0:
        # set the price no largert than the previous bid
        # for price in range(99, tree[node]["MaxPrice"]+1, 100):
        for price in range(99, 1000, 100):
            tree[len(tree)] = {"Week": tree[node]["Week"], "Child":[], "Parent": node, "Price": price, 
                                 "Type": "S", "n":0, "V": 0, "UCB": float('inf')}
            tree[node]["Child"].append(len(tree)-1)

def get_max_child_ucb(tree, node):
    if len(tree[node]["Child"]) == 0:
        expand_tree(tree, node) 
    max_UCB = float("-inf")
    max_node = None
    for child in tree[node]["Child"]:
        if tree[child]["UCB"] >= max_UCB:
            max_UCB = tree[child]["UCB"]
            max_node = child
    return max_node

def get_random_child_ucb(tree, node):
    if len(tree[node]["Child"]) == 0:
        expand_tree(tree, node) 
    return tree[node]["Child"][int(random.random() * len(tree[node]["Child"]))]

def do_back_prop(tree, node, pointer, revenue):
    rollout = revenue
    while pointer > node:
        pointer = tree[pointer]["Parent"]
        # Update V and n
        tree[pointer]["V"] = (tree[pointer]["V"] * tree[pointer]["n"] + rollout) / (tree[pointer]["n"] + 1)
        tree[pointer]["n"] += 1
        # Only update UCB for a state-of-nature node
        # Also update the N_i and UCB for options not chosen in this simulation
        if tree[pointer]["Type"] == "S":
            tree[pointer]["UCB"] = tree[pointer]["V"] + 2 * (
                math.log(tree[tree[pointer]["Parent"]]["n"] + 1) / tree[pointer]["n"]) ** 0.5
            peer_list = tree[tree[pointer]["Parent"]]["Child"]
            for no in peer_list:
                if pointer == no: # myself
                    continue
                if tree[no]["n"] > 0:
                    tree[no]["UCB"] = tree[no]["V"] + 2 * (math.log(tree[tree[no]["Parent"]]["n"] + 1)
                     / tree[no]["n"]) ** 0.5

def get_revenue(remain, price, data_week, last_week_price):
    revenue = 0
    remain_stock = copy.deepcopy(remain)
    for SKU in ["A", "B", "C"]:
        for i in range(7):
            value_i = data_week[data_week["SKU"] == SKU].iloc[:, 3+i].item()
            if value_i > price and remain_stock[SKU] > 0:
                remain_stock[SKU] -= 1
                revenue += price
            else:
                return_i = data_week[data_week["SKU"] == SKU].iloc[:, 10+i].item()
                if return_i > 0:
                    last_week_price[SKU].append(return_i)
    return revenue, remain_stock

def get_last_week_revenue(remain, price, data_week, last_week_price):
    revenue = 0
    remain_stock = copy.deepcopy(remain)
    for SKU in ["A", "B", "C"]:
        for i in range(7):
            value_i = data_week[data_week["SKU"] == SKU].iloc[:, 3+i].item()
            if value_i > price and remain_stock[SKU] > 0:
                remain_stock[SKU] -= 1
                revenue += price
        for value in last_week_price[SKU]:
            if value > price and remain_stock[SKU] > 0:
                remain_stock[SKU] -= 1
                revenue += price
    return revenue, remain_stock

def check_sold_out(remain_stock):
    if remain_stock["A"] == 0 and remain_stock["B"] == 0 and remain_stock["C"] == 0:
        return True
    return False

def build_tree(tree, node, k=500): 
    loop = 0 # total 600 weeks -> 50 loops in total
    sold_out_week = []
    time_stamp = datetime.datetime.now()
    for t in range(k):
        if t % 1000 == 0:
            print("Executed loops: "+ str(t) + ". Execution time: " + str(datetime.datetime.now()-time_stamp))
            time_stamp = datetime.datetime.now()
        loop %= 50
        loop += 1
        start_week = (loop - 1) * 12 + 1
        end_week = loop * 12
        
        week = start_week
        pointer = node
        revenue = 0
        remain_stock = {"A":10, "B":10, "C":10}
        last_week_price = {"A":[], "B":[], "C":[]}
        # simulate from the 1st week to 11th week
        while week <= end_week:
            # expanson
            if len(tree[pointer]["Child"]) == 0:
                expand_tree(tree, pointer)
            # pointer move to S type node
            #pointer = get_max_child_ucb(tree, pointer)
            pointer = get_random_child_ucb(tree, pointer)
            price = tree[pointer]["Price"]
            if week != end_week:
                r, remain_stock = get_revenue(remain_stock, price, data[data["NumOfWeek"] == week], last_week_price)
                revenue += r
            else:
                # simulate the final (12th) week
                r, remain_stock = get_last_week_revenue(remain_stock, price, data[data["NumOfWeek"] == week], last_week_price)
                revenue += r
            if check_sold_out(remain_stock):
                sold_out_week.append(week-start_week)
                break 
            week += 1
            # pointer move to D type node
            # Check if the state has been realized before
            exist_flag = 0
            for child_id in tree[pointer]["Child"]:
                if tree[child_id]["RemainStock"] == remain_stock:
                    exist_flag = 1
                    pointer = child_id
                    break
            # this state is not realized before
            if exist_flag == 0:
                tree[len(tree)]= {"Week": week, "Child": [], "Parent": pointer, "RemainStock":remain_stock, "Type": "D", "MaxPrice":price, "n":0, "V": 0}
                tree[pointer]["Child"].append(len(tree)-1)
                pointer = len(tree)-1
                
        # Start backpropagation; BSR is the total revenue going forward in the simulation
        do_back_prop(tree, node, pointer, revenue)
    print(float(sum(sold_out_week)) / len(sold_out_week))

def load_tree(tree_file):
    load_tree = pd.read_csv(tree_file, index_col=0)
    load_tree = load_tree.to_dict("index")
    for v in load_tree.values():
        try:
            v["Child"] = literal_eval(v["Child"])
            v["RemainStock"] = eval(v["RemainStock"])
        except:
            continue
    return load_tree

def inference(week_tree):
    pointer = 0
    remain_stock = {"A":10, "B":10, "C":10}
    for _ in range(12):
        pointer = get_max_child_ucb(week_tree, pointer)
        price = week_tree[pointer]["Price"]
        print("Sell price: %i" %price)
        str_in = input("A, B, C sold:")
        stock_delta = [int(n) for n in str_in.split()]
        remain_stock["A"] -= stock_delta[0]
        remain_stock["B"] -= stock_delta[1]
        remain_stock["C"] -= stock_delta[2]
        if check_sold_out(remain_stock):
            break
        exist_flag = 0
        for child_id in week_tree[pointer]["Child"]:
            if week_tree[child_id]["RemainStock"] == remain_stock:
                exist_flag = 1
                pointer = child_id
        if exist_flag == 0:
            print("Condition not covered...")
            break
    print("Inference ended...")

if __name__ == "__main__":
    iter_times = 1000
    iter_name = "_0"
    input_tree = "t"
    if len(sys.argv) > 1:
        iter_times = int(sys.argv[1])
    if len(sys.argv) > 2:
        iter_name = sys.argv[2]
    if len(sys.argv) > 3:
        input_tree = sys.argv[3]
    output_tree = "./output/tree_" + iter_name + ".csv"
    sim_data = "./data/SimulatedData.xlsx"
    data = pd.read_excel(sim_data, sheet_name=0)
    data["NumOfWeek"] = (data["Season"]-1)*12 + data["Week"]

    remain_stock = {"A":10, "B":10, "C":10}
    week_tree = {0:{"Week":0, "Child": [], "RemainStock":remain_stock, "Type": "D", "MaxPrice":999, "n":0, "V": 0}}
    if os.path.exists("./output/"+input_tree):
        week_tree = load_tree("./output/"+input_tree)
        print("loaded tree from " + input_tree)
    build_tree(week_tree, 0, iter_times)
    pd.DataFrame(week_tree).T.to_csv(output_tree)