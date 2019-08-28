from datetime import datetime
import pymongo
from flask_cors import CORS, cross_origin
from flask import Flask, render_template, url_for, request, session, redirect,jsonify  # For flask implementation
import random
from redis import Redis, RedisError
import socket
import os

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


connection = pymongo.MongoClient('localhost', 27017)
database = connection['Carwash']
app = Flask(__name__)
collection = database['Users']
collection_admin = database['Admin']
collection_scheduleservice = database['Scheduleservice']


# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)


@app.route('/api/users/register', methods=['POST'])
@cross_origin()
def register():
    users = collection

    primary_key = str(random.getrandbits(32))
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password =request.get_json()['password']
    created = datetime.utcnow()


    user_id = users.insert({
        'primary_key': primary_key,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'created': created,


    })

    return "Successfully Inserted"
    return jsonify({'result': result})


@app.route('/api/users/login', methods=['POST'])
@cross_origin()
def login():
    users = collection
    email = request.get_json()['email']
    password = request.get_json()['password']
    result = ""

    response = users.find_one({'email': email})

    if response:
        if response['password'] == password:
            result = jsonify({"token": "Success"})

        else:
            result = jsonify({"error": "Invalid username and password"})
    else:
        result = jsonify({"result": "No results found"})
    return result

@app.route('/api/admin/login', methods=['POST'])
@cross_origin()
def admin_login():
    users = collection_admin
    name = request.get_json()['name']
    password = request.get_json()['password']
    result = ""

    response = users.find_one({'name': name})

    if response:
        if response['password'] == password:
            result = jsonify({"token": "Success"})

        else:
            result = jsonify({"error": "Invalid username and password"})
    else:
        result = jsonify({"result": "No results found"})
    return result

@app.route('/api/users/allusers', methods=['GET'])
@cross_origin()
def alluser():

    output= []
    users = collection
    alluser = users.find()
    # result = jsonify({"result": alluser})

    for item in alluser:
        output.append({'primary_key':item['primary_key'],'first_name': item['first_name'], 'last_name': item['last_name'], 'email': item['email'],
                       'password': item['password'], 'created': item['created'],
                       })


    result =  jsonify({'result' : output})
    return result;

# ------------- Update Service ----------
@app.route('/api/users/update', methods=['POST'])
@cross_origin()
def userupdate():
    users = collection
    primary_key = request.get_json()['primary_key']
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password = request.get_json()['password']
    created = datetime.utcnow()

    update = users.find_one({'primary_key': primary_key})
    update['first_name'] = first_name
    update['last_name'] = last_name
    update['email'] = email
    update['password'] = password
    users.save(update)


    result = "Successfully Update"

    return jsonify({'result': result})

# ------------- Delete Service ----------
@app.route('/api/users/delete', methods=['POST'])
@cross_origin()
def userdelete():
    users = collection
    primary_key = request.get_json()['primary_key']
    delete = users.find_one({'primary_key': primary_key})
    users.remove(delete)
    result = "Successfully delete"

    return jsonify({'result': result})


# ------------- Schedule Service ----------

@app.route('/api/users/scheduleservice', methods=['POST'])
@cross_origin()
def scheduleservice():
    users = collection_scheduleservice
    date_time = request.get_json()['date_time']
    service_type = request.get_json()['service_type']
    created = datetime.utcnow()

    user_id = users.insert({
        'date_time': date_time,
        'service_type': service_type,
        'created': created,
    })

    result = "Successfully Scheduled"

    return jsonify({'result': result})

# ------------- Schedule Service ----------

@app.route('/api/users/userdetailbyid', methods=['POST'])
@cross_origin()
def userdetailbyid():
    users = collection
    primary_key = request.get_json()['primary_key']

    userdetail = users.find_one({'primary_key': primary_key})

    output = ({'primary_key': userdetail['primary_key'] , 'first_name': userdetail['first_name'] , 'last_name': userdetail['last_name'],
                   'email': userdetail['email'],'password': userdetail['password'], 'created': userdetail['created'],
                   })
    return jsonify({'result': output})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)