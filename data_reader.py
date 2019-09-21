
class dataReader(object):
    def __init__(self):
        self.data = []

    def get_parsed_data(self) -> list:
        return []
    
    def get_data_of_week(self, week):
        if week >= len(self.data):
            print("week data out of index")
            return {}
        return self.data[week]
    
    def get_weeks(self):
        return len(self.data)