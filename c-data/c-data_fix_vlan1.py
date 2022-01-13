#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 13:36:48 2022

@author: alakiza
"""


import argparse
import telnetlib
import re
import sys

ONU_STATUS_ONLINE    = 0
ONU_STATUS_OFFLINE   = 1
ONU_STATUS_POWERDOWN = 2

is_debug = False
def debug_print(str):
    if is_debug:
        print("debug: ", str)
    return

def check_ip(ip):
    return re.fullmatch(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)

def connect(ip, port):
    return telnetlib.Telnet(ip, 23, 5)

def login(tel, user, password):
    raw = tel.read_until(b'User name:')
    debug_print(raw.decode('utf-8'))
    tel.write(user.encode('utf-8') + b'\n')
    
    raw = tel.read_until(b'User password:')
    debug_print(raw.decode('utf-8'))
    tel.write(password.encode('utf-8') + b'\n')
    
    raw = tel.read_until(b'>')
    debug_print(raw.decode('utf-8'))
    tel.write(b'enable\n')
    
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    tel.write(b'config\n')
    
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    tel.write(b'vty output show-all\n')
    
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    
    return 1

def get_onu_status(tel, tree, onuid):
    tel.write(b'show ont info 0/0 %d all\n' % (tree))
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    
    lines = raw.decode('utf-8').split("\r\n")[5:-4]
    
    # print("\n".join(lines))
    
    for line in lines:
        cols = line.split()
        # print(cols)
        
        tree_num = int(cols[1])
        onu_num = int(cols[2])
        
        if tree == tree_num & onuid == onu_num: 
            # print(cols)
            onu_status = cols[5]
            if onu_status == "online":
                return 0
            elif onu_status == "offline":
                return 1
            elif onu_status == "powerdown":
                return 2
    
    return -1

def get_onu_up_down_log(tel, tree, onuid):
    tel.write(b'interface epon 0/0\n')
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    
    tel.write(b'show ont up-down-log %d %d\n' % (tree, onuid))
    raw = tel.read_until(b'#')
    debug_print(raw.decode('utf-8'))
    
    lines = raw.decode('utf-8').split("\r\n")[4:-2]
    
    records = []
    for line in lines:
        cols = line.split()
        # print(cols)
        
        if len(cols) > 3:
            date_up   = cols[1]
            time_up   = cols[2]
            
            date_down = cols[3]
            time_down = cols[4]
            
            reason    = cols[5]
        
            record = {"date_up"   : date_up, 
                      "time_up"   : time_up,
                      "date_down" : date_down,
                      "time_down" : time_down,
                      "reason"    : reason}
            
            records.append(record)
        else:
            date_up   = cols[1]
            time_up   = cols[2]
            
            record = {"date_up"   : date_up, 
                      "time_up"   : time_up}
            
            records.append(record)
        
        print(records)
        
    return -1

def fix_vlan1(ip, user, password, tree, onuid):
    tel = connect(ip, 23)
    res = login(tel, user, password)
    
    if res == 1:
        onu_status = get_onu_status(tel, tree, onuid)
        if onu_status == ONU_STATUS_OFFLINE:
            print("Onu epon0/%d:%d is offline" % (tree, onuid))
        elif onu_status == ONU_STATUS_POWERDOWN:
            print("Onu epon0/%d:%d is powerdown" % (tree, onuid))
        elif onu_status == ONU_STATUS_ONLINE:
            print("Onu epon0/%d:%d is online" % (tree, onuid))
            get_onu_up_down_log(tel, tree, onuid)
        
    tel.close()
        
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip device")
    # parser.add_argument("-user", help="login from user. default=admin")
    # parser.add_argument("-pas", help="user password")
    parser.add_argument("-tree", help="Onu tree")
    parser.add_argument("-onu", help="Onu num")
    parser.add_argument("-debug", help="debug mode", action='store_true')
    args = parser.parse_args()
    user = "admin"
    pas = "MOLAdm2009"
    tree = 0
    onu = 0

    if not args.ip:
        print("Need set ip address")
        sys.exit(1)
    elif not check_ip(args.ip):
        print("Incorrect ip address")
        sys.exit(2)
        
    is_debug = args.debug
    
    # if args.user:
    #     user = args.user

    # if args.pas:
    #     pas = args.pas

    try:
        tree = int(args.tree)
        if (tree < 1 or tree > 16):
            print("Incorrect tree range (1-16)")
            sys.exit(3)
    except ValueError:
        print("tree not a number")
        sys.exit(3)
    
    try:
        onu = int(args.onu)
        if (onu < 1 or onu > 64):
            print("Incorrect onu range (1-64)")
            sys.exit(4)
    except ValueError:
        print("onu not a number")
        sys.exit(4)

    fix_vlan1(args.ip, user, pas, tree, onu)
