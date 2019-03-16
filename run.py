"""Creates a Flask server to read from KAFKA and produce a JSON endpoint"""
import configparser
import json
import logging
import time
from datetime import datetime
from functools import wraps
from threading import Thread

from confluent_kafka import Consumer
from flask import Flask, current_app, jsonify, request


class JSON_Server:
    """A JSON Flask Server for passing PA Kafka data"""

    def __init__(self, port, metric):
        self.port = port
        self.flask = Flask("{}:{}".format(__name__, self.port))
        self.thread = Thread(daemon=True, target=self.flask.run, kwargs={
            'host': '0.0.0.0',
            'port': self.port,
            'debug': False,
            'threaded': True
        })
        # The local arrays we want to update
        self.peeples = []
        self.central = []
        self.douglas = []
        self.magnolia = []
        self.pa_metric = metric
        # Disable logging as the webpage hits the site once a second
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def start(self):
        """Starts up the JSON server thread"""
        @self.flask.route('/api', methods=['GET', 'HEAD'])
        @self.support_jsonp
        def json_api():
            """JSON endpoint of all sensors"""
            ret = {
                "peeples": self.peeples,
                "central": self.central,
                "douglas": self.douglas,
                "magnolia": self.magnolia
            }
            return jsonify(ret)
        self.thread.start()

    def support_jsonp(self, f):
        """Wraps JSONified output for JSONP"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            callback = request.args.get('callback', False)
            if callback:
                content = str(callback) + '(' + str(f().data.decode()) + ')'
                return current_app.response_class(content, mimetype='application/json')
            else:
                return f(*args, **kwargs)
        return decorated_function

    def update(self, sensor_id, json_msg):
        """Updates the sensor_id's array with the new info"""
        if sensor_id == "84:f3:eb:44:d8:24":
            to_modify = self.central
        elif sensor_id == "84:f3:eb:91:44:60":
            to_modify = self.douglas
        elif sensor_id == "84:f3:eb:91:44:38":
            to_modify = self.peeples
        elif sensor_id == "84:f3:eb:45:1a:53":
            to_modify = self.magnolia

        to_modify.append((json_msg[self.pa_metric], str(
            datetime.fromtimestamp(time.time()))))

        # keep only a day's worth of memory messages for memory purposes
        if len(to_modify) > 1440:
            del to_modify[0]


def main():
    """A loop which reads from kafka and appends to local arrays"""
    config = configparser.ConfigParser()
    config.read('config.ini')

    consumer = Consumer({
        'bootstrap.servers': config['KAFKA']['bootstrap_servers'],
        'group.id': 'flask_pa_consumer',
        'auto.offset.reset': 'latest'
    })

    consumer.subscribe([
        config['KAFKA']['peeples_topic'],
        config['KAFKA']['central_topic'],
        config['KAFKA']['douglas_topic'],
        config['KAFKA']['magnolia_topic']
    ])

    json_server = JSON_Server(3100, "pm2_5_atm")
    json_server.start()

    while True:
        try:
            msg = consumer.poll(1.0)
            if (not msg) or msg.error():
                continue
            try:
                json_msg = json.loads(msg.value().decode('utf-8'))
                json_server.update(json_msg["SensorId"], json_msg)
            except json.decoder.JSONDecodeError:
                # In the odd chance that the JSON can't be decoded...
                continue
        except KeyboardInterrupt:

            break
    consumer.close()


if __name__ == "__main__":
    main()
