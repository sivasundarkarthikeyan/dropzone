#Imports
import os
import base64
import datetime
from flask_api import status
from flask_cors import CORS, cross_origin
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, jsonify, make_response, send_from_directory


from Transform import Transform
from Datastore import Datastore

#Class Flask
app = Flask(__name__)
CORS(app, expose_headers='Authorization', resources={r"/store": {"origins": "*"}, 
                                                     r"/fetchAll": {"origins": "*"},
                                                     r"/fetchKeys": {"origins": "*"},
                                                     r"/fetchMany": {"origins": "*"},
                                                     r"/deleteMany": {"origins": "*"},
                                                     r"/filter": {"origins": "*"},
                                                     })
@app.route('/static/<path:path>', methods=['POST'])
@cross_origin()

def openSwagger(path):
    return send_from_directory('static', path)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL, 
    config = {
        'app-name': "Data Dropzone Challenge"        
    })

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

transform = Transform()
datastore = Datastore()

@app.route('/store', methods=['POST'])
@cross_origin()

def storeData():
    #method receiving request from service datazonestore with timestamp and data
    #directs the transformed data to storage
    # endpoint to receive the new Data
    #          to call transfromations methods internally to transform data
    #          to call store methods internally to store data in Datastore
    # Receives: an object or a list of objects as input
    # Returns: List of stored record(s) 
    return_msg = None

    if verifyAuth(request.headers):
        #return_msg = list()
        key_error_count = 0
        payload_received = request.get_json() 
        
        if not isinstance(payload_received, list):
            payload = list()
            payload.append(payload_received)
            payload_received = payload

        for current_payload in payload_received:
            if 'time_stamp' in current_payload and 'data' in current_payload:
                time = current_payload['time_stamp']
                data = current_payload['data']
                converted_time = transform.convert_time(time)
                calculated_stats = transform.calculate_stats(data)
                
                if isinstance(calculated_stats, dict) and isinstance(converted_time, datetime.date):
                    _id = datastore.storeData(converted_time, calculated_stats, time, data)
                    record = datastore.retrieveMany(strToList(_id))
                    return_msg = formatRecords(record, None)
                    status_message = 200
                else:
                    status_message = 204
            else:
                key_error_count = key_error_count + 1
        if len(return_msg) == 0 and key_error_count > 0:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)

@app.route('/fetchMany', methods=['GET'])
@cross_origin()

def returnMany():
    # endpoint to return records for a given set of id_or_name 
    # Receives: strings of id_or_name to retrieve
    # Returns: List of records formatted according to the request
    
    return_msg = None

    if verifyAuth(request.headers):
        payload_received = request.args
        
        if '_id' in payload_received:
            ids = strToList(payload_received['_id'])
            record = datastore.retrieveMany(ids)

            if record:
                original = payload_received['original'] if 'original' in payload_received else False
                original = True if original == 'true' else False
                return_msg = formatRecords(record, original)
                status_message = 200
            else:
                return_msg = list()
                status_message = 204
        
        else:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)


@app.route('/fetchAll', methods=['GET'])
@cross_origin()

def returnAll():
    # endpoint to return records 
    # Receives: an integer to limit total records to return and original flag
    # Returns: List of records formatted according to the request
    
    return_msg = None
    
    if verifyAuth(request.headers):
        payload_received = request.args

        if 'limit' in payload_received:
            records = datastore.retrieveAll(int(payload_received['limit']))

            if records:
                original = payload_received['original'] if 'original' in payload_received else False
                original = True if original == 'true' else False
                return_msg = formatRecords(records, original)
                status_message = 200
            else:
                return_msg = list()
                status_message = 204
        
        else:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)


@app.route('/fetchKeys', methods=['GET'])
@cross_origin()

def returnKeys():
    # endpoint to return id_or_name 
    # Receives: an integer to limit total id_or_name to return
    # Returns: List of id_or_name

    return_msg = None

    if verifyAuth(request.headers):
        payload_received = request.args
        
        if 'limit' in payload_received:
            records = datastore.fetchKeys(int(payload_received['limit']))

            if records:
                return_msg = records
                status_message = 200
            else:
                return_msg = list()
                status_message = 204
        
        else:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)

@app.route('/deleteMany', methods=['DELETE'])
@cross_origin()

def removeMany():
    # endpoint to delete matching records
    # Receives: strings of id_or_name to delete
    # Returns: Number of records deleted
    return_msg = None

    if verifyAuth(request.headers):
        payload_received = request.args

        if '_id' in payload_received:
            ids = strToList(payload_received['_id'])
            records = datastore.deleteMany(ids)
            return_msg = dict()

            if records:
                return_msg['deletedRecords'] = records
                status_message = 200
            else:
                return_msg = list()
                status_message = 204
        
        else:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)

@app.route('/filter', methods=['POST'])
@cross_origin()

def filterMany():
    # endpoint for filter and retrieve data
    # Receives: 'field', 'operator', 'value' and original flag
    # Returns: List of records formatted according to the request
    return_msg = None
    keys = ['field', 'operator', 'value']

    if verifyAuth(request.headers):
        payload_received = request.get_json()
        
        if all(key in payload_received for key in keys):
            field = payload_received['field']
            operator = payload_received['operator']
            value = payload_received['value']
            records = datastore.filter(field, operator, value)

            if records:
                original = payload_received['original'] if 'original' in payload_received else False
                return_msg = formatRecords(records, original)
                status_message = 200
            else:
                return_msg = list()
                status_message = 204
        else:
            return_msg = None
            status_message = 400
    else:
        return_msg = None
        status_message = 401

    return make_response(jsonify(return_msg), status_message)

def formatRecords(data, original = None):
    # method formats the data
    # includes id_or_name
    # includes original data if user requests
    # Receives: List of records with all fields
    # Returns: List of records either with all fields or 
    #           excluding original data
    return_data = list()
    for record in data:
        temp_dict = dict()
        temp_dict['_id'] = record.key.id_or_name
        temp_dict['timeUTC'] = record['timeUTC']
        temp_dict['mean'] = record['mean']
        temp_dict['stdev'] = record['stdev']
        if original is True:
            temp_dict['time_stamp'] = record['time_stamp']
            temp_dict['data'] = record['data']
        return_data.append(temp_dict)

    return return_data

def strToList(data):
    # method converts string to list of string 
    # by spliting them using comma (,) 
    # Receives: string
    # Returns: List of strings
    return_data = list()
    if data:
        if ',' in data:
            return_data = [i for i in  data.split(',') if i ]
        else:
            return_data.append(data)
    
    return return_data

def verifyAuth(data):
    # method verifies the header information for authentication
    # extracts username & password from the headers 
    # and validates against ENV variables
    # Receives: header information from request
    # Returns: True or False based on validation
    if "Authorization" in data:
        credentials = data["Authorization"]
        credentials = credentials.split()[-1]
        env_credentials = os.environ.get('USERNAME') + ":" + os.environ.get('PASSWORD')
        env_credentials_bytes = env_credentials.encode('ascii')
        env_credentials_base64_bytes = base64.b64encode(env_credentials_bytes)
        env_credentials_base64 = env_credentials_base64_bytes.decode('ascii')
        if credentials == env_credentials_base64:
            return True
        else:
            return False
    else:
        return False

#if __name__ == "__main__":
    #app.secret_key = os.urandom(24)
    #app.run(host="localhost",use_reloader=False)
#    app.run(host='127.0.0.1', port=8080, debug=True)