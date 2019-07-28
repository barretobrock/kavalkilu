#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify

app = Flask(__name__)
api = Api(app)


class Hosts(Resource):
    """Hosts"""
    def get(self):
        """Collect the hosts"""
        with open('/etc/hosts', 'r') as f:
            hostlines = f.readlines()
        hostlines = [line.strip().split(' ') for line in hostlines if line.startswith('192.168.0')]
        hosts = [{'ip': ip, 'name': name} for ip, name in hostlines]
        result = {'data': hosts}
        return jsonify(result)


api.add_resource(Hosts, '/hosts')

if __name__ == '__main__':
    app.run(port='5002')
