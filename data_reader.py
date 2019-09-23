import pandas as pd
import numpy as np

data_file = "./data/SimulatedData.xlsx"

class dataReader(object):
    def __init__(self):
        self.data = []

    def read_file(self, file):
        file = "./data/SimulatedData.xlsx"
        data = pd.read_excel(file, sheet_name=0)
        data["NumOfWeek"] = (data["Season"]-1)*12 + data["Week"]
        self.data = data
        
    def get_parsed_data(self) -> list:
        return []
    
    def get_data_of_week(self, week):
        if week >= len(self.data):
            print("week data out of index")
            return {}
        return self.data[week]
    
    def get_weeks(self):
        return len(self.data)


if __name__ == "__main__":
    dr = dataReader()
    dr.read_file(data_file)