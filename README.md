# utc-cuip-purple-air-json-server

The purpose of this application is to retrieve data from a Kafka server and serve it as a JSON endpoint with callbacks.

## Requirements:

Python 3.6.x

- flask
- confluent-kafka

You can install these dependencies manually or use Pipenv [+PyEnv]

## Running

To run, just call `python run.py` (or `pipenv run python run.py` if using PIpenv). Once running, data is visible at [http://localhost:3100/api](http://localhost:3100/api) as raw JSON. You can also use JQuery to query this address and retrieve this JSON as a callback.

Kafka topic names and servers are contained within the `config.ini` file.



