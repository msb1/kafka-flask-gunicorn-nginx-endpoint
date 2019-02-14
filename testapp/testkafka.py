'''
Created on Feb 11, 2019

@author: Barnwaldo

-- Below script generates simulated analytics data for sending to Kafka, Kafka Connect and Kafka Streams applications
-- This is a Flask application with a generic bootstrap web page 
-- The application connects to javascript through socket.io using flask-socketio
-- A Kafka Producer and Consumer are started using kafka-python in separate threads 
-- The test data is sent as a json string with the producer to a topic and then received/consumed with the consumer
-- The sent/received messages are displayed in separate cards on the web page
-- Start/stop for the threads is performed with menu buttons on left menu bar of the web page
'''
import numpy as np
import random
import json
import threading
import time
from flask_socketio import SocketIO
from flask import Flask, render_template
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# app.config['DEBUG'] = True

socketio = SocketIO(app)
stop = threading.Event()
close = threading.Event()

pthreads = []
cthreads = []

# with n_class=2 --> classes are 1 = good/success and 0 = bad/failure
n_class = 2  
# provide labels for each numeric feature -- here include 5 simulated sensors in numerics list
numerics = ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5']
# Define numeric features with following list of lists:
# -- First sublist entry (case)
#       0 = two means correlated with n_class (normal distributions)
#       1 = two means anti-correlated with n_class (normal distributions)
#       2 = one mean -- no correlation (normal distribution)
#       3 = uniformly distributed [0, 1] with no correlation
# Second and third sublist entry --> means in interval [0, 1] corresponding to 0 and 1 in first entry
# Fourth and fifth sublist entry --> standard devs in interval [0, 1] corresponding to 0 and 1 in first entry
# For first sublist entry = 2, use only second and fourth sublist entries (others set to zero)
numeric_defs = [[0, 0.3, 0.7, 0.1, 0.1], [0, 0.25, 0.65, 0.15, 0.2], [1, 0.4, 0.6, 0.1, 0.1], [2, 0.4, 0.0, 0.2,0.0], [3, 0, 0, 0, 0]]

# provide labels for each category feature -- here include 4 category features in categorics list
categorics = ['cat1', 'cat2', 'cat3', 'cat4']
# define number of levels in each category
cat_levels = [2, 5, 4, 3]
# define category ranges for class = 0 and class = 1
# uniform rv is used to select category
cat_ranges_1 = [[0.05, 1.0], [0.2, 0.21, 0.5, 0.51, 1.0], [0.2, 0.5, 0.7, 1.0], [0.02, 0.98, 1.0]]
cat_ranges_0 = [[0.9, 1.0], [0.05, 0.4, 0.41, 0.95, 1.0], [0.2, 0.5, 0.7, 1.0], [0.4, 0.41, 1.0]]
# error rate in category feature selection
cat_error_rate = 0.1

# success rate when n_class output = 1
success = 0.65

# topic for kafka producer and consumer 
topic = 'sim-test'

'''
Method to create simulated analytics data records to be sent with Kafka Producer thread
'''
def makeRecord():
    
    # generate numerics (sensor) simulated data
    jsonDict = {}
    y = 1 if np.random.random_sample() < success else 0 
    jsonDict['class'] = y
    for i in range(len(numerics)):
        case = numeric_defs[i][0]
        # print("--> ", numeric_defs[i])
        value = 0
        if case == 0:
            if y == 1:
                value =  np.random.normal(numeric_defs[i][2], numeric_defs[i][4])
                # print(numeric_defs[i][2], numeric_defs[i][4])
            else:
                value =  np.random.normal(numeric_defs[i][1], numeric_defs[i][3])
        elif case == 1:
            if y == 1:
                value =  np.random.normal(numeric_defs[i][1], numeric_defs[i][3])
            else:
                value =  np.random.normal(numeric_defs[i][2], numeric_defs[i][4])
        elif case == 2:
            value =  np.random.normal(numeric_defs[i][1], numeric_defs[i][3])
        elif case == 3:
            value =  np.random.random_sample()
        jsonDict[numerics[i]] = value

    # generate categorics simulated data
    for i in range(len(categorics)):
        value = 0
        n_levels = cat_levels[i]
        rnd = np.random.random_sample()
        if y == 1:
            for j in range(n_levels):
                if(rnd < cat_ranges_1[i][j]):
                    value = j + 1
                    break
        else:
            for j in range(n_levels):
                if(rnd < cat_ranges_0[i][j]):
                    value = j + 1
                    break
        if np.random.random_sample() < cat_error_rate:
            value = np.random.randint(1, n_levels + 1)
        jsonDict[categorics[i]] = value

    jsonString = json.dumps(jsonDict)
    # return jsonDict, jsonString
    return jsonString


class Consumer(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        # To consume latest messages and auto-commit offsets
        self.consumer = KafkaConsumer(topic, bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.isSet():
            for message in self.consumer:
                # key = message.key.decode()
                value = message.value.decode()
                socketio.emit('newMessage', {'message': value}, namespace='/consumer')
                print ("-> consumer recv: ", value)
                # thread is stopped by setting event
                # if self.stop_event.isSet():
                #    break

    def stop(self):
        print("-> consumer stop called")
        self.stop_event.set()
        self.join()
        print("-> consumer join complete")


class Producer(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        # To consume latest messages and auto-commit offsets
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.stop_event = threading.Event()
        self.index = 0

    def run(self):
        time.sleep(1)
        # thread is stopped by setting close event
        while not self.stop_event.isSet():
            # get simulated
            self.index += 1
            # jd, js = makeRecord()
            js = makeRecord()
            self.producer.send(topic, key=str(self.index % 10).encode(), value=js.encode())
            socketio.emit('newMessage', {'message': js}, namespace='/producer')
            print("-> producer sent: ", js)
            # add some random time delay between sent messages 
            delay = 0.5 + 2 * random.random()
            time.sleep(delay)

    def stop(self):
        time.sleep(1)
        self.producer.send(topic, key=str(0).encode(), value=">>> stop message <<<".encode())
        print("-> producer stop called")
        self.stop_event.set()
        self.producer.flush(timeout=0.5)
        self.producer.close(timeout=0.5)
        self.join()
        print("-> producer join complete")
  

@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/producer')
def producer_connect():
    print('>> producer socketIO connected')
        
@socketio.on('message', namespace='/producer')
def producer_message(msg):
    print(">> message received on producer socketIO: ", msg)    
    if msg == 'start' or msg == 'stop':
        for p in pthreads:
            p.stop()
        pthreads.clear()
        if msg == 'start':
            p = Producer()
            pthreads.append(p)
            p.start()                         
    else:
        print('>> producer socketIO message not recognized...')

@socketio.on('disconnect', namespace='/producer')
def producer_disconnect():
    producer_message('stop')
    print('>> producer socketIO disconnected')

@socketio.on('connect', namespace='/consumer')
def consumer_connect():
    print('>> consumer socketIO connected')

@socketio.on('message', namespace='/consumer')
def consumer_message(msg):
    print(">> message received on consumer socketIO: ", msg)  
    if msg == 'start' or msg == 'stop':
        for c in cthreads:
            c.stop()
        cthreads.clear()
        if msg == 'start':
            c = Consumer()
            cthreads.append(c)
            c.start()  
    else:
        print('>> consumer socketIO message not recognized...')

@socketio.on('disconnect', namespace='/consumer')
def consumer_disconnect():
    consumer_message('stop')
    print('>> consumer socketIO disconnected')


# if __name__ == '__main__':
#     socketio.run(app)
