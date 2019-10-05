import pandas as pd
import os
import sys

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

if __name__ == "__main__":
    input_tree = sys.argv[1]
    if os.path.exists("./output/"+input_tree+".csv"):
        week_tree = load_tree("./output/"+input_tree+".csv")
        print("loaded tree from " + input_tree)
    else:
        exit("Tree not exist.")

    inference(week_tree)