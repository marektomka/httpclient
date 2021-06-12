#!/usr/bin/env python3
import socket 
import ssl
import sys
import re

types=['http', 'https'] 
header=""
content=""
codes=[301, 302, 303, 307, 308]

URL=str(sys.argv[1])
spl=re.match('[a-z]*',URL)
typ=spl[0]
URL=URL.replace(typ+"://","")
spl=re.match('([\w\-\.]+)',URL)
hostname=spl[0]
path=URL.replace(hostname,"")
if path=="":
    path="/"

if (typ in types):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if typ == types[1]:
        s.connect((hostname,443))
        s=ssl.wrap_socket(s)
    else:
        s.connect((hostname,80))
    while True:
        f=s.makefile("rwb")
        f.write(f'GET {path} HTTP/1.1\r\n'.encode("ASCII"))
        f.write(f'Host: {hostname}\r\n'.encode("ASCII"))
        f.write(f'Accept-charset: UTF-8\r\n\r\n'.encode("ASCII"))
        f.flush()
        line=f.readline().decode("ASCII")
        l=line.split(" ")
        status_code=l[1]
        status_message=l[2]
        headers={}
        l=f.readline().decode("ASCII").strip()
        while l != "":
            header=l.strip().split(':',1)
            if len(l)==2:
                header=l[0].lower()
                content=d[1].lower()
                headers[header]=content
            l=f.readline().decode('ASCII')
            if (status_code in codes):
                URL=headers['location']

                f.close()
                s.close()
            elif (status_code=="200"):
                break
            else:
                sys.stderr.write(f'{status_code} {status_message}')
                f.close()
                sys.exit(1)
                break
        if status_code=="200":
            for h in headers:
                if h=="content-length":
                    length=int(headers["content-length"])
                    content=f.read(length).decode("ASCII")
                    sys.stdout.buffer.write(content)
                    break
                elif h=="transfer-encoding":
                    while True:
                        le=f.readline()
                        length=int(le,16)
                        content=f.read(length)
                        sys.stdout.buffer.write(content)
                        if length==0:
                            break
                        f.readline()

    f.flush()
    f.close()
    sys.exit(0)
