#!/usr/bin/env python3
import socket 
import ssl
import sys
import re

types=['http', 'https'] 
header=""
content=""
hostname=""
codes=[301, 302, 303, 307, 308] 

URL=(sys.argv[1])

while True:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    headers={} 
    spl=re.match('[a-z]*',URL)
    typ=spl[0]
    URL=URL.replace(typ+"://","")
    spl=re.match('([\w\-\.]+)',URL)
    hostname=spl[0]
    path=URL.replace(hostname,"")
    if path=="":
        path="/"
    
    if typ=='https':
        s.connect((hostname,443))
        s=ssl.wrap_socket(s)
    else:
        s.connect((hostname,80))

    f=s.makefile("rwb")
    f.write(f'GET {path} HTTP/1.1\r\n'.encode("ASCII"))
    f.write(f'Host: {hostname}\r\n'.encode("ASCII"))
    f.write(f'Accept-charset: UTF-8\r\n\r\n'.encode("ASCII"))
    f.flush()

    #status
    line=f.readline().decode("ASCII")
    l=line.split(" ")
    status_code=l[1]
    status_message=l[2]
    
    #hlavicky - cyklus az po \r\n
    line=f.readline().decode("ASCII").strip()
    while line != '\r\n':
        l=line.split(':',1)
        if len(l)==2:
            header=l[0].lower()
            content=l[1].lower()
        headers[header]=content
        line=f.readline().decode('ASCII')
        
    if (status_code == '301' or status_code == '302' or status_code == '303' or status_code == '307' or status_code == '308'):
        URL=headers['location']
        f.close()
        s.close()
    elif (status_code=="200"):
        break
    else:
        sys.stderr.write(f'404 Not Found\n')
        f.close()
        sys.exit(0)
        break
#obsah
if status_code=="200":
    for h in headers:
        if h=="content-length":
            length=int(headers["content-length"])
            content=f.read(length).decode('ASCII')
            sys.stdout.buffer.write(content)
            break
                
        elif h=="transfer-encoding":
            while True:
                le=f.readline().decode('ASCII')
                length=int(le,16)
                content=f.read(length)
                sys.stdout.buffer.write(content)
                if lenght==0:
                    break
                f.readline()
else:
    print('Chybne URL')

f.flush()
f.close()
s.close()
sys.exit(0)

