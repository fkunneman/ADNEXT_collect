

from pymongo import Connection
from pymongo.errors import ConnectionFailure

import datetime
import time_functions
from collections import OrderedDict

class DBReader:

    def __init__(self,dbname):
        connection = Connection()
        self.db = connection[dbname]
        self.retrievedict = {}
        self.sort_dict = OrderedDict()
        self.sort_dict['_id.year'] = 1
        self.sort_dict['_id.month'] = 1
        self.sort_dict['_id.day'] = 1
        self.collection = False
        self.subset = False

    def return_collection(self,collection_name):
        return self.db[collection_name]

    def return_collection_names(self):
        return [name for name in self.db.collection_names() if name != 'system.indexes']

    def set_collection(self,collection_name):
        self.collection = self.db[collection_name]

    def set_date_range(self,startdate,enddate):
        sdt = time_functions.return_datetime(startdate)
        edt = time_functions.return_datetime(enddate)
        self.update_retrievedict('date',{'$gte':sdt,'$lt':edt})

    def set_perspective(self,perspective):
        pass

    def set_keyterms(self,keyterms):
        pass

    def update_retrievedict(self, key, value):
        self.retrievedict[key] = value

    def retrieve_items(self):
        retrieved = list(self.collection.aggregate([{'$match' : self.retrievedict}, { '$group': { '_id': { 'year' : { '$year': '$date' }, 'month' : { '$month': '$date' }, 'day' : { '$dayOfMonth': '$date' }}, 'count' : {'$sum':1}}}, {'$sort':self.sort_dict}]).values())
        items = retrieved[0] if type(retrieved[0]) == list else retrieved[1]
        print(items[:10])
        datesequence = [str(x['_id']['day']) + '-' + str(x['_id']['month']) + '-' + str(x['_id']['year']) for x in items]    
        counts = [x['count'] for x in items]
        plot_items = [{'date':datesequence[i], 'count':counts[i]} for i,d in enumerate(datesequence)]
        return plot_items



#        subset = self.collection.find(self.retrievedict)
#        self.subset = subset

#    def retrieve_datecount(self,begin_date,end_date):
#        datecount = self.subset.aggregate([{ "$group": { "_id": { "year" : { "$year": "$date" }, "month" : { "$month": "$date" }, : { "$dayOfMonth": "$date" }}, "count" : {"$sum":1}}}, {"$sort":sort_dict}])
