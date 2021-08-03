#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для очистки неактивных ону
"""

__author__ = "Vadim Shemyatin"

import argparse
import telnetlib
import re


def check_ip(ip):
    return re.fullmatch(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)


def clear_tree(ip, user, pas, tree):
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
        if tree == 0:
            tel.write(b'show epon inactive-onu\n')
        else:
            tel.write("show epon inactive-onu interface ePON 0/{0}\n".format(tree).encode('utf-8'))
        parse = tel.read_until(b'#').decode('utf-8')
        search = re.findall(r'Interface EPON0/(\d{1,2}) has bound (\d{1,2})', parse)
        mac_address = re.findall(r'((?:[0-9a-f]{4}\.){2}(?:[0-9a-f]{4}))', parse)

        if len(search) == 0:
            print("Tree is empty...")
            return

        print(parse)
        tel.write(b'config\n')
        tel.read_until(b'#')

        for interface, mac_count in search:
            tel.write("interface epon0/{0}\n".format(interface).encode('utf-8'))
            print(tel.read_until(b'#').decode('utf-8'))
            for _ in range(int(mac_count)):
                str_mac = "no epon bind-onu mac {0}\n".format(mac_address[0])
                tel.write(str_mac.encode('utf-8'))
                tel.read_until(b'#')
                print(str_mac[:-1])
                mac_address.pop(0)

        tel.write(b'exit\n')
        tel.read_until(b'#')
        tel.write(b'exit\n')
        tel.read_until(b'#')
        tel.write(b'write all\n')
        print(tel.read_until(b'#', timeout=10).decode('utf-8'))

        if tree != 0:
            print('Current active-onu')
            tel.write("show epon active-onu interface ePON 0/{0}\n".format(tree).encode('utf-8'))
            parse = tel.read_until(b'#').decode('utf-8')
            search = re.findall(r'Interface EPON0/(\d{1,2}) has bound (\d{1,2})', parse)
            print(search[0][1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip device")
    parser.add_argument("-user", help="login from user. default=admin")
    parser.add_argument("-pas", help="user password")
    parser.add_argument("-tree", help="If not set, remove onu from all tree")
    args = parser.parse_args()
    user = "admin"
    pas = "MOLAdm2009"
    tree = 0

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
            if (tree < 1 or tree > 16):
                print("Incorrect tree range (1-16)")
                exit()
        except ValueError:
            tree = 0

    clear_tree(args.ip, user, pas, tree)
