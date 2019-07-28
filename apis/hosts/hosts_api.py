#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_jsonpify import jsonify

app = Flask(__name__)


@app.route('/hosts', methods=['GET'])
def hosts():
    """Simple GET all hosts with static IPs"""
    with open('/etc/hosts', 'r') as f:
        hostlines = f.readlines()
    hostlines = [line.strip().split(' ') for line in hostlines if line.startswith('192.168.0')]
    hosts = [{'ip': ip, 'name': name} for ip, name in hostlines]
    result = {'data': hosts}
    return jsonify(result)

