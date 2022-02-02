#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 13:36:48 2022

@author: alakiza
"""


import argparse
import telnetlib
import os.path
import re
import sys
import datetime

ONU_STATUS_ONLINE    = 0
ONU_STATUS_OFFLINE   = 1
ONU_STATUS_POWERDOWN = 2

is_debug = False
def debug_print(str):
    if is_debug:
        print("debug: ", str)
    return

class VlanFixer:
    def __init__(self, ip, user, password, tree, onuid):
        self._ip = ip
        self._username = user
        self._password = password
        self._tree     = int(tree)
        self._onuid    = int(onuid)
        
    def _connect(self, ip, port):
        return telnetlib.Telnet(ip, port, 5)
    
    def _read_telnet(self, expected_str):
        raw = self._connection.read_until(bytes(expected_str.encode('utf-8')))
        debug_print(raw.decode('utf-8'))
        
        return raw.decode('utf-8')
    
    def _write_telnet(self, write_str):
        self._connection.write(write_str.encode('utf-8') + b'\n')
        
        return
    
    def _login(self):
        raw = self._read_telnet("User name:")
        self._write_telnet(self._username)
        
        raw = self._read_telnet('User password:')
        self._write_telnet(self._password)
        
        raw = self._read_telnet('>')
        self._write_telnet('enable')
        
        raw = self._read_telnet('#')
        self._write_telnet('config')
        
        raw = self._read_telnet('#')
        self._write_telnet('vty output show-all')
        
        raw = self._read_telnet('#')
        
        return True
    
    def _get_onu_status(self):
        self._write_telnet('show ont info 0/0 %d all' % (self._tree))
        decoded = self._read_telnet('#')
        
        lines = decoded.split("\r\n")[5:-4]
        
        # print("\n".join(lines))
        
        for line in lines:
            cols = line.split()
            # print(cols)
            
            tree_num = int(cols[1])
            onu_num = int(cols[2])
            
            # print(tree_num, onu_num, self._tree, self._onuid)
            
            if (self._tree == tree_num) & (self._onuid == onu_num): 
                # print(cols)
                onu_status = cols[5]
                # print(onu_status)
                if onu_status == "online":
                    return 0
                elif onu_status == "offline":
                    return 1
                elif onu_status == "powerdown":
                    return 2
        
        return -1
    
    def _save_up_down_log_csv(self, log):
        filename = "up_down_log.csv"
        if not os.path.exists(filename):
            with open (filename, 'w') as f:
                f.write("poll_time;ip;tree;onuid;seq;date_up;date_down;time_up;time_down;reason\n")
                
        with open(filename, 'a') as f:
            poll_time = datetime.datetime.now()
            for i, onu_session in enumerate(log):
                line = ""
                if i == 0:
                    line = "%s;%s;%d;%d" % (poll_time, self._ip, self._tree, self._onuid)
                else:
                    line = ";;;"
                # print(line)
                for field in onu_session:
                    line = line + ";%s" % (onu_session[field])
                    # print(field, onu_session[field])
                    
                f.write("%s\n" % (line))

    def _get_onu_up_down_log(self):
        self._write_telnet('interface epon 0/0')
        decoded = self._read_telnet('#')
        
        self._write_telnet('show ont up-down-log %d %d' % (self._tree, self._onuid))
        decoded = self._read_telnet('#')
        
        lines = decoded.split("\r\n")[4:-2]
        
        records = []
        for line in lines:
            cols = line.split()
            # print(cols)
            
            if len(cols) > 3:
                seq       = cols[0]
                date_up   = cols[1]
                time_up   = cols[2]
                
                date_down = cols[3]
                time_down = cols[4]
                
                reason    = cols[5]
            
                record = {"seq"       : seq, 
                          "date_up"   : date_up, 
                          "time_up"   : time_up,
                          "date_down" : date_down,
                          "time_down" : time_down,
                          "reason"    : reason}
                
                records.append(record)
            else:
                seq       = cols[0]
                date_up   = cols[1]
                time_up   = cols[2]
                
                record = {"seq"       : seq, 
                          "date_up"   : date_up, 
                          "time_up"   : time_up}
                
                records.append(record)
            
        # print(records)
        
        self._write_telnet('exit')
        decoded = self._read_telnet('#')
            
        return records
    
    def _save_ont_info(self, info):
        filename = "ont_info.csv"
        
        param_names = ["Vendor-ID", "OUI Version", "ONT model", 
                       "Extended model", "ONT mac address", "ONT hardware version", 
                       "ONT software version", "ONT chipset vendor ID", "ONT chipset model", 
                       "ONT chipset revision", "ONT chipset version/date", "ONT firmware version"]
        
        if not os.path.exists(filename):
            with open (filename, 'w') as f:
                st = "poll_time;ip;tree;onuid"
                for param in param_names:
                    st = st + ";" + param
                    
                st = st + "\n"
                
                f.write(st)
                
        with open(filename, 'a') as f:
            poll_time = datetime.datetime.now()
            
            line = "%s;%s;%d;%d" % (poll_time, self._ip, self._tree, self._onuid)
            for param in param_names:
                line = line + ";" + info[param]
            
            f.write("%s\n" % (line))
            
    def _get_onu_info(self):
        self._write_telnet("interface epon 0/0")
        self._read_telnet("#")
        self._write_telnet("show ont version %s %s" % (self._tree, self._onuid))
        decoded = self._read_telnet("#")
        
        lines = decoded.split("\r\n")[2:-4]
        # print("\n".join(lines))
        
        param_names = ["Vendor-ID", "OUI Version", "ONT model", 
                       "Extended model", "ONT mac address", "ONT hardware version", 
                       "ONT software version", "ONT chipset vendor ID", "ONT chipset model", 
                       "ONT chipset revision", "ONT chipset version/date", "ONT firmware version"]
        
        param_dict = {}
        for param in param_names:
            param_dict[param] = ""
        
        for line in lines:
            cols = line.split(":")
            
            param_name = cols[0].strip()
            for row in param_names:
                if param_name == row:
                    param_dict[row] = ":".join(cols[1:])
                    break
                
        debug_print(param_dict)
                    
        return param_dict
        
    def _show_mac_address_ont(self):
        self._write_telnet('show mac-address ont 0/0/%d %d' % (self._tree, self._onuid))
        decoded = self._read_telnet('#')
        
        res = []
        
        if decoded.find("There is not any MAC address record") > -1:
           return  res
       
        lines = decoded.split("\r\n")[6:-3]
        # print("\n".join(lines)) 
        
        for line in lines:
            cols = line.split()
            mac = cols[0]
            vlan = cols[1]
        
            res.append((mac, vlan))
            
        return res
    
    def _re_register_onu(self):
        self._write_telnet('interface epon 0/0')
        decoded = self._read_telnet('#')
        
        self._write_telnet('ont re-register %d %d' %  (self._tree, self._onuid))
        decoded = self._read_telnet('#')
        
        print(decoded)
        print("onu epon0/%s/%s re-registered" % (self._tree, self._onuid))
        
        self._write_telnet('exit')
        decoded = self._read_telnet('#')
        
        return
    
            
    def run(self):
        self._connection = self._connect(self._ip, 23)
        login_res = self._login()
    
        if login_res:
            onu_status = self._get_onu_status()
            if onu_status == ONU_STATUS_OFFLINE:
                print("Onu epon0/%d:%d is offline" % (self._tree, self._onuid))
            elif onu_status == ONU_STATUS_POWERDOWN:
                print("Onu epon0/%d:%d is powerdown" % (self._tree, self._onuid))
            elif onu_status == ONU_STATUS_ONLINE:
                print("Onu epon0/%d:%d is online" % (self._tree, self._onuid))
                
                mac_vlan = self._show_mac_address_ont()
                
                for (mac, vlan) in mac_vlan:
                    print("MAC %s vlan %s" % (mac, vlan))
                    
                for (mac, vlan) in mac_vlan:
                    if int(vlan) == 1:
                        print("Found mac %s in vlan %s" % (mac, vlan))
                
                up_down_log = self._get_onu_up_down_log()
                self._save_up_down_log_csv(up_down_log)
                
                ont_info = self._get_onu_info()
                self._save_ont_info(ont_info)
                
                self._re_register_onu()
                
        self._connection.close()
    

def check_ip(ip):
    return re.fullmatch(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip)

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

    # fix_vlan1(args.ip, user, pas, tree, onu)
    fixer = VlanFixer(args.ip, user, pas, tree, onu)
    fixer.run()