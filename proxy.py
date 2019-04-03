import socket
import os
import threading
import sys
import struct
import base64

PROXY_PORT = 20100
MAX_CONN = 10
BUFFER_SIZE = 100000000
blocked_cidr = []
blocked_ips = []
vip = []
file_obj = open("blacklist.txt","r")
auth_obj = open("username:password.txt","r")


def cidr_to_ips():
	for i in range(len(blocked_cidr)):
		(ip, cidr) = blocked_cidr[i].split('/')
		cidr = int(cidr) 
		host_bits = 32 - cidr
		i = struct.unpack('>I', socket.inet_aton(ip))[0] 
		start = (i >> host_bits) << host_bits 
		end = start | ((1 << host_bits))
		end += 1
		for i in range(start, end):
		    tp_ip = socket.inet_ntoa(struct.pack('>I',i))
		    blocked_ips.append(tp_ip)

def handle_parsing(client_socket, c_addr, data):
	tdata = data	
	data = str(data)
	print(data)
	fline = data.split('\n')[0]
	try:
		sline = data.split('\n')[2]
		idx = sline.find("Basic")
		hashed_val = sline[idx:].split(' ')[1][:-1]
	except:
		hashed_val = ''
	
	try:
		url = fline.split(' ')[1]
	except:
		sys.exit()
	print(url)

	http_pos = url.find("://") 
	if (http_pos==-1):
	    temp = url
	else:
	    temp = url[(http_pos+3):] 

	port_pos = temp.find(":") 

	# find end of web server
	webserver_pos = temp.find("/")
	if webserver_pos == -1:
	    webserver_pos = len(temp)

	webserver = ""
	port = -1
	if (port_pos==-1 or webserver_pos < port_pos): 

	    # default port 
	    port = 80 
	    webserver = temp[:webserver_pos] 

	else: # specific port 
	    port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
	    webserver = temp[:port_pos] 	
	
	# Check if current IP is blocked

	ip_to_check = socket.gethostbyname(webserver)
	if ip_to_check in blocked_ips:
		print(hashed_val)
		if not hashed_val in vip:
			print("\nCurrent user is NOT AUTHENTICATED to access this")
			client_socket.send(str.encode("Current user is not authenticated to access this"))
			sys.exit()    
	

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.settimeout(60)
	try:
		s.connect((webserver, port))
		s.sendall(tdata)
	except:
		sys.exit()

	while 1:
		try:
		    temp_data = s.recv(BUFFER_SIZE)
		    if (len(temp_data) > 0):
		        client_socket.send(temp_data) 
		    else:
		        break 
		except:
			sys.exit()
	sys.exit()  


def initiate_server():
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxy_socket.bind(('127.0.0.1', PROXY_PORT))
	proxy_socket.listen(MAX_CONN)
	proxy_ip = proxy_socket.getsockname()[0]
	print ("Proxy server running on ip address " + str(proxy_ip) + " and port number = " + str(proxy_socket.getsockname()[1]))
	print
    # Listening and Accepting requests
	while 1:
		try:
			new_socket, c_addr = proxy_socket.accept()
			data = new_socket.recv(BUFFER_SIZE)
			t = threading.Thread(target=handle_parsing, args=(new_socket, c_addr, data))
			t.setDaemon(True)
			t.start()
		except KeyboardInterrupt:
			proxy_socket.close()
			sys.exit()

blocked_cidr = file_obj.readlines()
admins = auth_obj.readlines()
for i in range(len(blocked_cidr)):
	blocked_cidr[i] = blocked_cidr[i][:-1]
cidr_to_ips()

for i in range(len(admins)):
	admins[i] = admins[i][:-1]

for admin in admins:
	vip.append(base64.b64encode(admin))

print(vip)
initiate_server()


