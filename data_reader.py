import xlrd
data_file = "./data/Simulated Data.xlsx"

class dataReader(object):
    def __init__(self):
        self.data = []

    def read_file(self, file):
        with xlrd.open_workbook(file) as workbook:
            sheet = workbook.sheet_by_index(0)
            print("Sheet Name:", sheet.name)
            print("Rows: :", sheet.nrows)
            print("Columns: :", sheet.ncols)
            dic_sample = {"A":[0.0 for _ in range(7)],
                          "B":[0.0 for _ in range(7)],
                          "C":[0.0 for _ in range(7)],
            }
            total_weeks = int(sheet.cell(-1, 0)) * int(sheet.cell(-1, 1))
            data = [dic_sample for _ in range(total_weeks)]

            for i in range(1, sheet.nrows): # skip the index line
                # trun month into week
                week = int(sheet.cell(i, 0)) * int(sheet.cell(i, 1))
                values = []
                for j in range(3, 10): # value of buyer 1-7
                    values.append(float(sheet.cell(i, j)))
                if sheet.cell(i, 2) == "A":
                    data[-1]["A"] = values
                    for j in range(0, 8): #record the return value
                        if float(sheet.cell(i, j+10)) > 0.0:
                            returnsA.append(float(sheet.cell(i, j+10)))
                elif sheet.cell(i, 2) == "B":
                    data[-1]["A"] = values
                    for j in range(0, 8): #record the return value
                        if float(sheet.cell(i, j+10)) > 0.0:
                            returnsB.append(float(sheet.cell(i, j+10)))
                elif sheet.cell(i, 2) == "C":
                    data[-1]["A"] = values
                    for j in range(0, 8): #record the return value
                        if float(sheet.cell(i, j+10)) > 0.0:
                            returnsC.append(float(sheet.cell(i, j+10)))
                else:
                    print("Wrong SKU")
                    break
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