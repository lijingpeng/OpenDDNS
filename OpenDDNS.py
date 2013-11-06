#!/usr/bin/env python
#-*- coding:UTF-8 -*-
import time
import urllib
import urllib2
import json
import fcntl
import socket
import struct
from Daemon import daemonize

workdir = '/var/log/'                                       #LOG dir

UserInfo = {}
UserInfo[ 'login_email' ] = 'email@example.com'             # your login email, you need to change this
UserInfo[ 'login_password' ] = 'passwd'                     # your login password, you need to change this
UserInfo[ 'format' ] = 'json'

domain = 'youdomain.com'                                    # your domain 
record = 'subdomain'                                        # subdomain

headers = {}
headers['User-Agent'] = 'OpenDDNS'
RemoteIPAddr = ''

def Log(msg):
    fp = open(workdir + 'OpenDDNS.log', 'a')
    fp.write(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
            + "] " + msg + '\n')
    fp.close()

def GetDomainID():
    URL = 'https://dnsapi.cn/Domain.Info'
    params = UserInfo.copy()
    params[ 'domain' ] = domain
    
    request = urllib2.Request( URL,
            headers = headers,
            data = urllib.urlencode( params ))

    response = urllib2.urlopen( request )
    JsonData = json.load( response )

    if JsonData[ 'status' ][ 'code' ] != '1':
        Log("GetDomainID error:" + JsonData['status']['code'] + ":"+ JsonData['status']['message'])
        return 0
    else:
        return JsonData['domain']['id']

def GetRecordID(domain):
    URL = 'https://dnsapi.cn/Record.List'
    params = UserInfo.copy()
    params[ 'domain_id' ] = domain
    params[ 'sub_domain' ] = record

    request = urllib2.Request(URL, headers = headers,
            data = urllib.urlencode( params ))

    response = urllib2.urlopen(request)
    JsonData = json.load(response)

    if JsonData[ 'status' ][ 'code' ] != '1':
        Log("GetRecordID error:" + JsonData['status']['code'] + ":"+ JsonData['status']['message'])
        return 0
    else:
        global RemoteIPAddr 
        RemoteIPAddr = JsonData['records'][0]['value']
        return JsonData['records'][0]['id']

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

def SetDDNS(domain_id, record_id, ip):
    URL = 'https://dnsapi.cn/Record.Ddns'
    params = UserInfo.copy()
    params[ 'domain_id' ] = domain_id
    params[ 'record_id' ] = record_id
    params[ 'sub_domain'] = record
    params[ 'record_line'] = "默认"
    params[ 'value' ] = ip

    request = urllib2.Request(URL, headers = headers, data = urllib.urlencode( params ))

    response = urllib2.urlopen( request )

    JsonData = json.load(response)
    print JsonData
    if JsonData[ 'status' ][ 'code' ] != '1':
        Log("Set DDNS error:" + JsonData['status']['code'] + ":"+ JsonData['status']['message'])
    pass


if __name__ == '__main__':

    daemonize(stdout = '/var/log/OpenDDNSOut.log', stderr = '/var/log/OpenDDNSErr.log', workdir = workdir)
    
    while True:
        Log("-------------------------------")
        Log("Begin running...")
        domain_id = GetDomainID()
        Log("domain_id = " + domain_id)
        record_id = GetRecordID( domain_id )
        Log("record_id = " + record_id)
        Log("Remote IP address = " + RemoteIPAddr)
        LocalIP = get_ip_address('eth0')
        Log('Local IP address:' + LocalIP)

        if RemoteIPAddr != LocalIP:
            SetDDNS(domain_id, record_id, LocalIP)
            RemoteIPAddr = LocalIP
            Log('Set new DNS successfully.')
        else:
            Log('No need to change DNS')

        time.sleep(3600)


