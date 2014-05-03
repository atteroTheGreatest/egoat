from flask import Flask
import json
import redis
from flask import render_template, request

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

REDIS_LIST = 'egoat::sharers::'
TIMEOUT = 3


def load_data():
    rclient = redis.Redis()
    announcements = {}
    announcement_keys = rclient.keys(REDIS_LIST + '*')
    for key in announcement_keys:
        json_announcement = rclient.get(key)
        address = key.split(b'::')[-1]
        announcements[address] = json.loads(json_announcement)
    return announcements


def get_peers(check_sum):
    all_peers = load_data()
    peers_with_file = [address for address, values in all_peers.items()
                       if check_sum in values.keys()]
    return peers_with_file


def add_announcement(address, checksum_files):
    announcement = checksum_files
    json_announcement = json.dumps(announcement)
    rclient = redis.Redis()
    rclient.setex(REDIS_LIST + address, json_announcement, TIMEOUT)


@app.route('/')
def hello_world():
    data = load_data()
    return render_template('index.html', announcements=data)


@app.route('/file/<file_hash>', methods=['GET'])
def get_file(file_hash=None):
    if file_hash:
        peers = get_peers(file_hash)
        return json.dumps(peers)
    else:
        return 400


@app.route('/hello/', methods=['POST'])
def announce_files():
    checksum_files = json.loads(request.args['checksum_files'])
    address = request.args['address']
    add_announcement(address, checksum_files)

    return "OK"


if __name__ == '__main__':
    app.run()
