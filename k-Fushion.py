import pandas as pd
import numpy as np
import math
import random


def expand_tree(tree, node):
    if len(tree[node]["Child"]) == 0:
        # set the price no largert than the previous bid
        for price in range(99, tree[node]["MaxPrice"]+1, 100):
            tree[len(tree)] = {"Week": tree[node]["Week"], "Child":[], "Parent": node, "Price": price, 
                                 "Type": "S", "n":0, "V": 0, "UCB": float('inf')}
            tree[node]["Child"].append(len(tree)-1)

def get_max_child_ucb(tree, node):
    if len(tree[node]["Child"]) == 0:
        expand_tree(tree, node) 
    max_UCB = float("-inf")
    max_node = None
    for child in tree[node]["Child"]:
        if tree[child]["UCB"] > max_UCB:
            max_UCB = tree[child]["UCB"]
            max_node = child
    return max_node

def do_back_prop(tree, node, pointer, revenue):
    BSR = 0
    while pointer > node:
        pointer = tree[pointer]["Parent"]
        # Only update BSR if the node is a state-of-nature node (representing an option)
        if tree[pointer]["Type"] == "S":
            BSR = BSR + revenue
        # Update V and n
        tree[pointer]["V"] = (tree[pointer]["V"] * tree[pointer]["n"] + BSR) / (tree[pointer]["n"] + 1)
        tree[pointer]["n"] = tree[pointer]["n"] + 1
        # Only update UCB for a state-of-nature node
        # Also update the N_i and UCB for options not chosen in this simulation
        if tree[pointer]["Type"] == "S":
            tree[pointer]["UCB"]=tree[pointer]["V"] + 2 * (
                math.log(tree[tree[pointer]["Parent"]]["n"] + 1) / tree[pointer]["n"]) ** 0.5
            peer_list = tree[tree[pointer]["Parent"]]["Child"]
            for no in peer_list:
                if pointer == no: # myself
                    continue
                if tree[no]["n"] > 0:
                    tree[no]["UCB"] = tree[no]["V"] + 2 * (math.log(tree[tree[no]["Parent"]]["n"] + 1)
                     / tree[no]["n"]) ** 0.5

def get_revenue(remain_stock, price, data_week, last_week_price):
    revenue = 0
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
    return revenue

def get_last_week_revenue(remain_stock, price, data_week, last_week_price):
    revenue = 0
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
    return revenue

def check_sold_out(remain_stock):
    if remain_stock["A"] == 0 and remain_stock["B"] == 0 and remain_stock["C"] == 0:
        return True
    return False

def build_tree(tree, node, k=500): 
    loop = 0 # total 600 weeks -> 50 loops in total
    for _ in range(k):
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
            # selection (two ways of choosing child node)
            # pointer move to S type node
            pointer = get_max_child_ucb(tree, pointer)
            # pointer = get_random_child_ucb(tree, pointer)
            price = tree[pointer]["Price"]
            if week != end_week:
                revenue += get_revenue(remain_stock, price, data[data["NumOfWeek"] == week], last_week_price)
            else:
                # simulate the final (12th) week
                revenue += get_last_week_revenue(remain_stock, price, data[data["NumOfWeek"] == week], last_week_price)
            if check_sold_out(remain_stock):
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
                tree[len(tree)]= {"Week": week, "Child": [], "RemainStock":remain_stock, "Type": "D", "MaxPrice":price, "n":0, "V": 0}
                tree[pointer]["Child"].append(len(tree)-1)
                pointer = len(tree)-1
                
        # Start backpropagation; BSR is the total revenue going forward in the simulation
        do_back_prop(tree, node, pointer, revenue)



if __name__ == "__main__":
    file = "./data/SimulatedData.xlsx"
    data = pd.read_excel(file, sheet_name=0)
    data["NumOfWeek"] = (data["Season"]-1)*12 + data["Week"]

    remain_stock = {"A":10, "B":10, "C":10}
    week_tree = {0:{"Week":0, "Child": [], "RemainStock":remain_stock, "Type": "D", "MaxPrice":999, "n":0, "V": 0}}
    build_tree(week_tree, 0, 10)
    pd.DataFrame(week_tree).T.to_csv("./data/tree.csv")