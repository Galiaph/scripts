#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для очистки не активных ону
"""

__author__ = "Vadim Shemyatin"

import argparse
import telnetlib
import re


def check_ip(ip):
    return re.fullmatch(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)


def clear_tree(ip, user, pas):
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
        tel.write(b'show epon onu-information\n')
        parse = tel.read_until(b'#').decode('utf-8')
        search = re.findall(r'Interface EPON0/(\d) has registered (\d{1,2}) ONUs:', parse)

        if len(search) == 0:
            print("Tree is empty...")
            return

        for interface, onu_count in search:
            print("Interface EPON0/{0} has registered {1} ONUs".format(interface, onu_count))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip device")
    parser.add_argument("-user", help="login from user. default=admin")
    parser.add_argument("-pas", help="user password")
    #parser.add_argument("-tree", help="If not set, remove onu from all tree")
    args = parser.parse_args()
    user = "admin"
    pas = "MOLAdm2009"

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

    clear_tree(args.ip, user, pas)
