#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для отображения количества мак-адресов на одной ону
"""

__author__ = "Vadim Shemyatin"


import argparse
import telnetlib
import re
from collections import Counter


def check_ip(ip):
    return re.fullmatch(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)


def call_mac(ip, user, pas, tree):
    with telnetlib.Telnet(ip, 23, 5) as tel:
        tel.read_until(b'Username:')
        tel.write(user.encode('utf-8') + b'\n')

        tel.read_until(b'Password:')
        tel.write(pas.encode('utf-8') + b'\n')
        tel.read_until(b'>')
        tel.write(b'enable\n')
        tel.read_until(b'#')
        tel.write(b'terminal length 0\n')
        tel.read_until(b'#')
        tel.write(b'terminal width 0\n')
        tel.read_until(b'#')

        for index in range(1, tree+1):
            str = "show mac address-table interface epoN 0/{0}\n".format(index)
            tel.write(str.encode())
            parse = tel.read_until(b'#').decode('utf-8')

            search = re.findall(r"epon0/{0}".format(index)+r":(\d{1,2})", parse)
            onu = Counter(search)

            if len(search) == 0:
                print("interface epon0/{} not used\n".format(index))
                continue

            #mac_address = re.findall(r'((?:[0-9a-f]{4}\.){2}(?:[0-9a-f]{4}))', parse)

            if (len(onu) >= len(search)) & (len(search) > 0):
                print("Current interface epoN 0/{} is: {} onu".format(index, len(onu)))
                print("Used one onu per user: {}\n".format(len(onu)))
            elif len(onu) < len(search):
                print("Current interface epoN 0/{} is: {} onu".format(index, len(onu)))
                user_per_onu = 0
                for value in onu.values():
                    if value > 1:
                        user_per_onu += value
                print("Used one onu per user: {}".format(len(search)-user_per_onu))
                print("Copper users: {}\n".format(user_per_onu))


        # if len(search) == 0:
        #     print("Tree is empty...")
        #     return

        # print(parse)
        # tel.write(b'config\n')
        # tel.read_until(b'#')

        # for interface, mac_count in search:
        #     tel.write("interface epon0/{0}\n".format(interface).encode('utf-8'))
        #     print(tel.read_until(b'#').decode('utf-8'))
        #     for _ in range(int(mac_count)):
        #         str_mac = "no epon bind-onu mac {0}\n".format(mac_address[0])
        #         tel.write(str_mac.encode('utf-8'))
        #         tel.read_until(b'#')
        #         print(str_mac[:-1])
        #         mac_address.pop(0)

        # tel.write(b'exit\n')
        # tel.read_until(b'#')
        # tel.write(b'exit\n')
        # tel.read_until(b'#')
        # tel.write(b'write all\n')
        # print(tel.read_until(b'#', timeout=10).decode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip device")
    parser.add_argument("-user", help="login from user. default=admin")
    parser.add_argument("-pas", help="user password")
    parser.add_argument("-tree", help="default 4")
    args = parser.parse_args()
    user = "admin"
    pas = "MOLAdm2009"
    tree = 4

    if not args.ip:
        print("Need set ip address")
        exit()
    elif not check_ip(args.ip):
        print("Incorrect ip address")
        exit()

    if args.user:
        user = args.user

    if args.pas:
        pas = args.pas

    if args.tree:
        try:
            tree = int(args.tree)
            if (tree > 8 or tree < 0):
                print("Not correct tree value")
                exit()
        except ValueError:
            tree = 4

    call_mac(args.ip, user, pas, tree)
