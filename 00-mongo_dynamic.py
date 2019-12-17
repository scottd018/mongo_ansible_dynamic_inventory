#!/usr/bin/python

import os
import argparse
import pymongo
from pymongo import MongoClient

try:
    import json
except ImportError:
    import simplejson as json

MONGO_HOST = os.environ.get("MONGO_HOST")
MONGO_PORT = int(os.environ.get("MONGO_PORT"))
MONGO_DATABASE = os.environ.get("MONGO_DATABASE")
MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")


def get_group_hosts(host_objects):
    ret_list = []
    for host in host_objects:
        ret_list.append(host['server-name'])
    return sorted(ret_list)


def get_host_vars(host):
    host = db.hosts.find_one({"server-name": host})
    return host['citi']

parser = argparse.ArgumentParser()
parser.add_argument('--list', action="store_true")
parser.add_argument('-H', action="store_true", help="Human readable format")
args = parser.parse_args()

mongoclient = MongoClient(MONGO_HOST, MONGO_PORT, username = MONGO_USERNAME, password = MONGO_PASSWORD, authSource = MONGO_DATABASE)
db = mongoclient[MONGO_DATABASE]
json_docs = dict()
json_docs['_meta'] = dict()
json_docs['_meta']['hostvars'] = dict()
scanned_groups = []

if args.list:
    groups = [{"name": "all","vars":{}}]

    for group in groups:
        if group['name'] not in scanned_groups:
            group_hosts = get_group_hosts(db.hosts.find())

            json_docs.update({
                group['name']: {
                    "hosts": group_hosts,
                    "vars": group['vars']
                }
            })

            for host in group_hosts:
                host_vars = get_host_vars(host)
                json_docs['_meta']['hostvars'][host] = dict(
                    list(host_vars.items() + group['vars'].items()))
            scanned_groups.append(group['name'])
    if args.H:
        print json.dumps(json_docs, sort_keys=False, indent=4, separators=(',', ': '))
    else:
        print json.dumps(json_docs)

mongoclient.close()
