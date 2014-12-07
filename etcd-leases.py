#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014 Jose Riguera
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import sys
import os
import etcd


DNSMASQ_DOMAIN = "ipmi"
ETCD_CONF = "config.py"
ETCD_HOST = "localhost"
ETCD_PORT = 4001
ETCD_PROTO = "http"



class EtcdLeases:
    """Maps dnsmasq leases"""
    etcd_keyroot = "/ipmi"
    etcd_devices = "/devices"
    etcd_host    = "/host"
    etcd_id      = "/id"
    etcd_ip      = "/ip"
    etcd_expires = "/expires"
    etcd_keylock = "/ipmi.lock"
    # infinite leases
    default_expires = 0


    def __init__(self, host, port, 
        client_protocol="http", client_timeout=60, client_reconnect=False, client_redirect=True):
        self.host = host
        self.port = port
        self.client_timeout = client_timeout
        self.client_reconnect = client_reconnect
        self.client_redirect = client_redirect
        self.client_protocol = client_protocol
        self.client = etcd.Client(host, port, 
            protocol=client_protocol, 
            read_timeout=client_timeout, 
            allow_reconnect=client_reconnect, 
            allow_redirect=client_redirect)
        try:
            root = self.client.get(self.etcd_keyroot)
        except KeyError:
            #lock = self.client.get_lock(self.etcd_keyroot + self.etcd_keylock, ttl=self.client_timeout)
            #lock.acquire()
            self.client.write(self.etcd_keyroot, dir=True)
            #lock.release()

    def _get_(self, key, default):
        try:
            return self.client.get(key).value
        except:
            return default

    def init(self, expires=None):
        value = []
        try:
            leases = self.client.get(self.etcd_keyroot + self.etcd_devices)
        except KeyError:
            self.client.write(self.etcd_keyroot + self.etcd_devices, dir=True)
        for l in leases.leaves:
            try:
                ip = self.client.get(l.key + self.etcd_ip)
            except:
                continue
            mac = l.key.rsplit('/', 1)[1]
            lease = dict(mac=mac)
            lease['ip'] = ip.value
            lease['host'] = self._get_(l.key + self.etcd_host, '*')
            if expires == None:
                expires = self.default_expires
            lease['expires'] = self._get_(l.key + self.etcd_expires, expires)
            lease['id'] = self._get_(l.key + self.etcd_id, '*')
            value.append(lease)
        return value

    def add(self, mac, ip, host, expires=None, id='*'):
        key = self.etcd_keyroot + self.etcd_devices + '/' + mac
        self.client.write(key + self.etcd_host, host)
        self.client.write(key + self.etcd_ip, ip)
        if expires == None:
            expires = self.default_expires
        self.client.write(key + self.etcd_expires, expires)
        self.client.write(key + self.etcd_id, id)

    def delete(self, mac, ip=None, host=None):
        key = self.etcd_keyroot + self.etcd_devices + '/' + mac
        self.client.delete(key, recursive=True)

    def old(self, mac, ip, host='*', expires=None, id='*'):
        key = self.etcd_keyroot + self.etcd_devices + '/' + mac
        self.client.write(key + self.etcd_ip, ip)
        self.client.write(key + self.etcd_host, host)
        if expires == None:
            expires = self.default_expires
        self.client.write(key + self.etcd_expires, expires)
        self.client.write(key + self.etcd_id, id)


def init(args):
    envconfig = args.configuration
    try:
        client = EtcdLeases(args.etcd_host, args.etcd_port, args.etcd_proto)
        for lease in client.init():
            print('{expires} {mac} {ip} {host} {id}'.format(**lease))
    except:
        return 1
    return 0


def add(args):
    envconfig = args.configuration
    try:
        client = EtcdLeases(args.etcd_host, args.etcd_port, args.etcd_proto)
        client.add(args.mac, args.ip, args.host)
    except:
        return 1
    return 0


def delete(args):
    envconfig = args.configuration
    try:
        client = EtcdLeases(args.etcd_host, args.etcd_port, args.etcd_proto)
        client.delete(args.mac)
    except:
        return 1
    return 0


def old(args):
    envconfig = args.configuration
    try:
        client = EtcdLeases(args.etcd_host, args.etcd_port, args.etcd_proto)
        client.old(args.mac, args.ip, args.host)
    except:
        return 1
    return 0


def main():
    """Parse environment and arguments and call the appropriate action."""
    config = {}
    # env
    configfile = os.environ.get('ETCD_CONF', ETCD_CONF)
    #execfile(configfile, config)
    # python 3: exec(open(configfile).read(), config)
    config['DNSMASQ_DOMAIN'] = os.environ.get('DNSMASQ_DOMAIN', DNSMASQ_DOMAIN)
    config['DNSMASQ_OLD_HOSTNAME'] = os.environ.get('DNSMASQ_OLD_HOSTNAME')
    config['DNSMASQ_LEASE_EXPIRES'] = os.environ.get('DNSMASQ_LEASE_EXPIRES')
    config['DNSMASQ_TIME_REMAINING'] = os.environ.get('DNSMASQ_TIME_REMAINING')
    config['DNSMASQ_SUPPLIED_HOSTNAME'] = os.environ.get('DNSMASQ_SUPPLIED_HOSTNAME')
    config['DNSMASQ_CLIENT_ID'] = os.environ.get('DNSMASQ_CLIENT_ID')
    config['DNSMASQ_TAGS'] = os.environ.get('DNSMASQ_TAGS')
    etcd_host = os.environ.get('ETCD_HOST', ETCD_HOST)
    etcd_port = os.environ.get('ETCD_PORT', ETCD_PORT)
    etcd_proto = os.environ.get('ETCD_PROTOCOL', ETCD_PROTO)
    # arg parser
    parser = argparse.ArgumentParser(
        description='Program to manage dnsmasq leases with etcd',
        epilog="(c) 2014 Jose Riguera, <jriguera@gmail.com>")
    parser.add_argument('--etcd-host', action='store', default=etcd_host, help='Etcd server')
    parser.add_argument('--etcd-port', action='store', type=int, default=etcd_port, help='Etcd port')
    parser.add_argument('--etcd-proto', action='store', default=etcd_proto, help='Etcd protocol')
    subparsers = parser.add_subparsers(help='commands')
    # Init command
    init_parser = subparsers.add_parser('init', help='List contents')
    init_parser.set_defaults(func=init, configuration=config)
    # Add lease
    add_parser = subparsers.add_parser('add', help='Add a new lease')
    add_parser.add_argument('mac', action='store', help='MAC address')
    add_parser.add_argument('ip', action='store', help='IP address')
    add_parser.add_argument('host', nargs='?', default='*', action='store', help='DNS host')
    add_parser.set_defaults(func=add, configuration=config)
    # Del lease
    del_parser = subparsers.add_parser('del', help='Delete a lease')
    del_parser.add_argument('mac', action='store', help='MAC address')
    del_parser.add_argument('ip', action='store', help='IP address')
    del_parser.add_argument('host', nargs='?', default='*', action='store', help='DNS host')
    del_parser.set_defaults(func=delete, configuration=config)
    # Old lease
    old_parser = subparsers.add_parser('old', help='Renew a lease')
    old_parser.add_argument('mac', action='store', help='MAC address')
    old_parser.add_argument('ip', action='store', help='IP address')
    old_parser.add_argument('host', nargs='?', default='*', action='store', help='DNS host')
    old_parser.set_defaults(func=old, configuration=config)
    # parse args
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
