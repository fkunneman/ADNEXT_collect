
from collections import defaultdict

class DateIndexer:

    def __init__(self,collection):
        self.collection = collectiondict
        self.date_objects = defaultdict(list)
        
    def index_dates(self,datekey):
        for object in self.collection:
            self.date_objects[object[datekey]].append(object)
    
    def return_indexed(self):
        return self.date_objects
