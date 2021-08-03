##!/usr/bin/env python3
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


def clear_tree(ip, user, pas, tree):
    with telnetlib.Telnet(ip, 23, 10) as tel:
        tel.read_until(b'User name:')
        tel.write(user.encode('utf-8') + b'\n')
        tel.read_until(b'User password:')
        tel.write(pas.encode('utf-8') + b'\n')
        tel.read_until(b'>')
        tel.write(b'enable\n')
        tel.read_until(b'#')
        tel.write(b'config\n')
        tel.read_until(b'#')
        tel.write(b'vty output show-all\n')
        tel.read_until(b'#')
        #tel.write(b'interface epon 0/0\n')
        #tel.read_until(b'#')

        for index in range(1, tree+1):
            #print("\tInterface epon 0/{}".format(index))
            tel.write("show mac-address port epon 0/0/{}\n".format(index).encode('utf-8'))
            parse = tel.read_until(b'#').decode('utf-8')
            search = re.findall(r'(\d{3})', parse)
            onu = Counter(search)
            
            if (len(onu) >= len(search)) & (len(search) > 0):
                print("Current interface epoN 0/{} is: {} onu".format(index, len(onu)))
                print("Use one onu per user\n")
            elif len(onu) < len(search):
                print("Current interface epoN 0/{} is: {} onu".format(index, len(onu)))
                user_per_onu = 0
                for value in onu.values():
                    if value > 1:
                        user_per_onu += value
                print("Used one onu per user: {}".format(len(search)-user_per_onu))
                print("Copper users: {}\n".format(user_per_onu))

            # if (len(onu) >= len(search)) & (len(search) > 0):
            #     print("Current interface epoN 0/{} is: {} users".format(index, len(onu)))
            #     print("Use one onu per user\n")
            # elif len(onu) < len(search):
            #     print("Current interface epoN 0/{} is: {} users".format(index, len(search)))
            #     print("Use one onu per user {}".format(len(onu)))
            #     print("User other: {}\n".format(len(search) - len(onu)))
        
        # tel.write(b'exit\n')
        # tel.read_until(b'#')
        # tel.write(b'save\n')
        # print(tel.read_until(b'#', timeout=10).decode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip device")
    parser.add_argument("-user", help="login from user. default=admin")
    parser.add_argument("-pas", help="user password")
    parser.add_argument("-tree", help="If not set, show all tree")
    args = parser.parse_args()
    user = "admin"
    pas = "MOLAdm2009"
    tree = 8

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
            tree = 8

    clear_tree(args.ip, user, pas, tree)
