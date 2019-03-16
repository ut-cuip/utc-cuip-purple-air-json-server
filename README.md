# Overview

This application retrieves data from a Kafka server and serves it as a JSON endpoint with callbacks.

## Dependencies:

Python 3.6.x

- flask
- confluent-kafka

You can install these dependencies manually or use Pipenv [+PyEnv]

## Running

`python run.py` (or `pipenv run python run.py` if using PIpenv) starts the Flask server and Kafka consumer on separate threads. 

Once running, data is visible at [http://localhost:3100/api](http://localhost:3100/api) as raw JSON. You can also use JQuery to query this address and retrieve this JSON as a callback.

Kafka topic names and servers are contained within the `config.ini` file.



