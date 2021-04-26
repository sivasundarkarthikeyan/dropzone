import os
import shortuuid
from google.cloud import datastore

class Datastore():
    
    datastoreClient = None
    kind = None
    
    def __init__(self):
        # constructor to initialize the class instance variables 
        self.datastoreClient = datastore.Client()
        self.kind = os.environ.get('KIND')
    
    def storeData(self, timeUTC, dataConverted, time_stamp, dataActual):
        # method to create an entity in Datastore under 
        # given Kind to store the original and transformed data
        # Receives: original and transformed data
        # Returns: _id_or_name to the Flask App
        return_data = None
        key = self.generateKey(shortuuid.uuid())
        entity = datastore.Entity(key=key)
        entity.update({
            'timeUTC': timeUTC,
            'time_stamp':time_stamp,
            'mean': dataConverted['mean'],
            'stdev': dataConverted['stdev'],
            'data':dataActual
        })
        self.datastoreClient.put(entity)
        return_data = key.id_or_name

        return return_data   
    
    def retrieveAll(self, limit):
        # method retrieves a certain number of records from 
        # Datastore under given Kind limiting to <limit>
        # Receives: number of records to return
        # Returns: records limited to <limit> with all fields 
        return_data = None
        query = self.datastoreClient.query(kind=self.kind)
        return_data = list(query.fetch(limit=limit))
        return return_data

    def retrieveMany(self, key):
        # method retrieves a certain number of records from 
        # Datastore under given Kind limiting number of <keys>
        # Receives: a list of id_or_name as string
        # Returns: records limited to number of <key> with all fields 
        return_data = None
        keys = self.generateKey(key)
        return_data = self.datastoreClient.get_multi(keys)
        return return_data

    def deleteMany(self, key):
        # method deletes a certain number of records from 
        # Datastore under given Kind limiting number of <keys>
        # Receives: a list of id_or_name as string
        # Returns: number of records deleted
        return_data = None
        keys = self.generateKey(key)
        before_delete_count = len(self.datastoreClient.get_multi(keys))
        self.datastoreClient.delete_multi(keys)
        after_delete_count = len(self.datastoreClient.get_multi(keys))
        if before_delete_count != 0 and after_delete_count == 0:
            return_data = before_delete_count
            
        return return_data

    def fetchKeys(self, limit):
        # method retrieves a certain number of id_or_name of records  
        # from Datastore under given Kind limiting to <limit>
        # Receives: number of keys to return
        # Returns: id_or_name limited to <limit>
        return_data = None
        data = self.retrieveAll(limit)
        if data:
            return_data = list()
            for i in data:
                return_data.append(i.key.id_or_name)
        return return_data

    def filter(self, field, operator, value):
        # method retrieves a certain number of records from
        # Datastore under given Kind that matches the filter
        # Receives: field, value and condition type to use for filter
        # Returns: records matching the filter criterion
        return_data = None
        query = self.datastoreClient.query(kind=self.kind)
        query = query.add_filter(field, operator, value)
        return_data = list(query.fetch())
        return return_data

    def generateKey(self, data):
        # method construcs Key for Datastore using Kind
        # Receives: id_or_name
        # Returns: a list of Datastore Key
        return_data = None
        if isinstance(data, list):
            return_data = list()
            for i in data:
                return_data.append(self.datastoreClient.key(self.kind, i))
        elif isinstance(data, str):
            if ',' in data:
                data = data.split(',')
                return_data = self.generateKey(data)
            else:
                return_data = self.datastoreClient.key(self.kind, data)
        else:
            return_data = self.datastoreClient.key(self.kind, "failsafedummyvalue")
        return return_data