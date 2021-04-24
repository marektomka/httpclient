#!/usr/bin/env python3
import socket
import os
import sys
import signal
import hashlib

def header_check(header):   # kontrola hlavicky
    status_code=100
    status_message="OK"

    for h in header:
        if h=="" or header[h]=="":
            status_code,status_message(200,' Bad request')
            return(status_code,status_message)
    return(status_code,status_message)

def header_split(line):  # kontrola riadku v hlavicke
    line = line.strip() # odstranime medzery
    line = line.split(':') # rozdelenie na dve casti
    identif = ""
    value = ""

    if not line[0].isascii(): # kontrola ci je identif ASCII
        return identif,value
    
    if (line[0].find(':') != -1): # kontrola ci je identif bez ':'
        return identif,value

    for string in line[0]: # kontrola ci identif obsahuje biely znak
        if(string.isspace()):
            return identif,value

    if (len(line) != 2):  # kontrola ci hlavicka pozostava iba z identif a value
        return identif,value
    
    if(line[0].find('/') != -1): # kontrola ci identif obsahuje '/'
        return identif,value

    identif = line[0] # ak preslo vsetkymi kontrolami, tak naplnime nase premenne
    value = line[1]
    
    return identif,value

def method_write(headers,inpFile):
    status_code=100
    status_message="OK"
    newHeader=""
    reply=""

    try:
        content = inpFile.read(int(headers["Content-length"]))
        name = hashlib.md5()
        name.update(newHeader.encode('utf-8'))
        name.hexdigest()

        with open(f'{headers["Mailbox"]}/{name}',"w") as message:
            message.write(content)

    except ValueError:
        status_code,status_message=(200,' Bad request')
    except FileNotFoundError:
        status_code,status_message=(203,' No such mailbox')
    except KeyError:
        status_code,status_message=(200,' Bad request')

    return(status_code,status_message,newHeader,reply)

def method_ls(headers):
    status_code=100
    status_message="OK"
    newHeader=""
    reply=""

    try:
       files = os.listdir(headers["Mailbox"])
       newHeader = (f'Number-of-messages: {len(files)}\n')
       reply = "\n".join(files)+"\n"
    
    
    except FileNotFoundError:
        status_code,status_message=(203,' No such mailbox')
    except KeyError:
        status_code,status_message=(200,' Bad request')

    return(status_code,status_message,newHeader,reply)

def method_read(headers):
    status_code=100
    satus_message="OK"
    newHeader=""
    reply=""
    
    try:
        with open(f'{headers["Mailbox"]}/{}','r') as message: # tu neviem co dat za / 
            reply = message.read()
            newHeader = (f'Content-length:{len(reply)}')
        
    except KeyError:
        status_code,status_message=(200,' Bad request')
    except FileNotFoundError:
        status_code,status_message=(201,' No such message')
    except OSError:
        status_code,status_message=(202,' Read error')

    return(status_code,status_message,newHeader,reply)


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
s.listen(5)

while True:
    connected_socket,address=s.accept()
    print(f'spojenie z {address}')
    pid_chld=os.fork()
    if pid_chld==0:
        s.close()
        f=connected_socket.makefile(mode='rw',encoding='utf-8')
        
        while True:
            method =f.readline().strip()
            reply=""
            newHeader=""
            headers={}
            header=""
            headIdentif=""
            headValue=""

            if not method:
                break
            
            data = f.readline()
            
            while data != "\n": # nacitavanie az po prazdny riadok
                
                headIdentif,headValue = header_split(data)
                headers[headIdentif] = headValue
                data = f.readline()
                

   
            print("Method: ",method)
            if method== 'WRITE':  
                status_code,status_message,newHeader,reply = method_write(headers,f)
            elif method=='READ':
                status_code,status_message,newHeader,reply = method_read(headers)
            elif method=='LS': 
                 status_code,status_message,newHeader,reply = method_ls(headers)
            else:
                status_code,status_message=(204,' Unknown method')
                f.write('\n')                        
                f.flush()
                sys.exit(0)
                    
            f.write(f'{status_code} {status_message}\n')
            f.write(reply)
            f.write('\n')
            f.write(newHeader)
            f.flush()
            print(f'{address} uzavrel spojenie')
            sys.exit(0)
    else:
        connected_socket.close()

