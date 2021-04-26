import json
import pytz
from datetime import datetime
from statistics import mean, stdev


class Transform():

    def __init__(self):
        pass

    def convert_time(self, time):
        # method to convert time from US/Eastern to UTC
        # takes an input, validates if it is a string and tries to convert to UTC
        # returns time in UTC format on success returns and None on failure
        return_data = None
        time_format = "%Y-%m-%dT%H:%M:%S%z"
        if isinstance(time, str):
            try:
                date_time_obj = datetime.strptime(time, time_format)
                tz = pytz.timezone('UTC')
                return_data = date_time_obj.astimezone(tz)
            except:    
                return_data = None

        return return_data

    def calculate_stats(self, data):
        # method to calculate required statistics for the input data
        # takes an input, validates certain criteria such as datatype consistency, length etc.,
        # calls two internal methods to calculate stats
        # returns stats or None based on validation

        def isinstance_check(data):
            # method checks if the data is numerical
            # returns True or False based on the datatype
            return_data = False
            return_data = isinstance(data, float) or isinstance(data, int)
            return return_data

        def calculate_average(data):
            # method calculates and returns the average of the given data list
            return_data = mean(data)
            return return_data

        def calculate_stdev(data):
            # method calculates and returns the standard deviation of the given data list
            return_data = stdev(data)
            return return_data

        return_data = dict()
        if isinstance(data, list) and len(data) > 1 and all(isinstance_check(i) for i in data):
            return_data['mean'] = calculate_average(data)
            return_data['stdev'] = calculate_stdev(data)
        else:
            return_data = None
        
        return return_data