import pandas as pd
import os
import sys
from ast import literal_eval

def choose_max_ucb(tree, node):
    max_UCB = float("-inf")
    max_node = None
    for child in tree[node]["Child"]:
        if tree[child]["UCB"] < float("inf") and tree[child]["UCB"] >= max_UCB:
            max_UCB = tree[child]["UCB"]
            max_node = child
    return max_node

def check_sold_out(remain_stock):
    if remain_stock["A"] == 0 and remain_stock["B"] == 0 and remain_stock["C"] == 0:
        return True
    return False

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
        pointer = choose_max_ucb(week_tree, pointer)
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

def search(week_tree):
    pointer = 0
    remain_stock = {"A":10, "B":10, "C":10}
    for i in range(12):
        str_in = input("A, B, C sold: ")
        stock_delta = [int(n) for n in str_in.split()]
        remain_stock["A"] -= stock_delta[0]
        remain_stock["B"] -= stock_delta[1]
        remain_stock["C"] -= stock_delta[2]
        if check_sold_out(remain_stock):
            break
        stock_str = str(remain_stock)
        week_tree["NumOfWeek"] = week_tree["Week"] % 12
        search_week = week_tree[week_tree["NumOfWeek"] == 2]
        search_type = search_week[search_week["Type"] == "D"]
        search_stock = search_type[search_type["RemainStock"] == stock_str]
        output = []
        for se in search_stock["Child"]:
            child_list = literal_eval(se)
            output.append(week_tree[week_tree.index.isin(child_list)])
        result = pd.concat(output)
        print(result[result["UCB"] != float(inf)])

if __name__ == "__main__":
    input_tree = "ucb12"
    if len(sys.argv) > 1:
        input_tree = sys.argv[1]
    input_file = "./output/"+input_tree+".csv"
    search(pd.read_csv(input_file, index_col=0))
    # if os.path.exists("./output/"+input_tree+".csv"):
    #     print("Loading tree from " + input_tree)
    #     week_tree = load_tree("./output/"+input_tree+".csv")
    # else:
    #     exit("Tree not exist.")

    # inference(week_tree)
    