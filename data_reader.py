import pandas as pd
import numpy as np

data_file = "./data/SimulatedData.xlsx"

class dataReader(object):
    def __init__(self):
        self.data = []
        self.read_file()

    def read_file(self, file=data_file):
        data = pd.read_excel(file, sheet_name=0)
        data["NumOfWeek"] = (data["Season"]-1)*12 + data["Week"]
        self.data = data
        print("Finished loading data...")
        print("Total of %i weeks for simulation." %(self.get_total_weeks()))
    
    def get_data_of_week(self, week):
        return self.data[self.data["NumsOfWeek"] == week]
    
    def get_price_of_weekSKU(self, week, SKU):
        week_data = self.data[self.data["NumOfWeek"] == week]
        return week_data[week_data["SKU"] == SKU].iloc[:, 3:10]

    def get_total_weeks(self):
        return self.data["NumOfWeek"].max()


if __name__ == "__main__":
    dr = dataReader()
    dr.read_file()