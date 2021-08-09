##!/usr/bin/env python3
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
        tel.write(b'interface epon 0/0\n')
        tel.read_until(b'#')

        start = 1

        if tree == 0:
            tree = 16
        else:
            start = tree

        for index in range(start, tree+1):
            print("\tInterface epon 0/{}".format(index))
            tel.write("show ont info {} all\n".format(index).encode('utf-8'))
            parse = tel.read_until(b'#').decode('utf-8')
            #search = re.findall(r'(\d.{2}\s(?:[0-9a-fA-F]{2}:?){6}.*(offline|powerdown))', parse)
            search = parse.split('\n')[5:-4]
            search_count = 0

            for x in search:
                tmp = re.split(r'[ ]+', x)
                if (tmp[6] == 'offline') | (tmp[6] == 'powerdown'):
                    tel.write("ont delete {} {}\n".format(index, tmp[3]).encode('utf-8'))
                    tel.read_until(b'#')
                    print("delete onu: {}  mac: {}".format(tmp[3], tmp[4]))
                    search_count += 1

            if (search_count > 0):
                print("Total delete: {}.\n".format(search_count))
            else:
                print("Tree is empty...\n")
        
        tel.write(b'exit\n')
        tel.read_until(b'#')

        if start != 1:
            print('Current active-onu')
            search2 = re.findall(r'online (\d{1,2})', parse)
            print(search2[0])

        tel.write(b'save\n')
        print(tel.read_until(b'#', timeout=10).decode('utf-8'))


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
