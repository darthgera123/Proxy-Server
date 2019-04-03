import socket
import os
import threading
import sys

PROXY_PORT = 20100
MAX_CONN = 10
BUFFER_SIZE = 2048000

def handle_parsing(client_socket, c_addr, data):
	tdata = data	
	data = str(data)
	fline = data.split('\n')[0]
	url = fline.split(' ')[1]
	print(url)

	http_pos = url.find("://") # find pos of ://
	if (http_pos==-1):
	    temp = url
	else:
	    temp = url[(http_pos+3):] # get the rest of url

	port_pos = temp.find(":") # find the port pos (if any)

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

	print(webserver)
	print(port)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.settimeout(60)
	s.connect((webserver, port))
	s.sendall(tdata)

	while 1:
    
	    temp_data = s.recv(BUFFER_SIZE)
	    if (len(temp_data) > 0):
	        client_socket.send(temp_data) 
	    else:
	        break   


def initiate_server():
	try:
		proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		proxy_socket.bind(('127.0.0.1', PROXY_PORT))
		proxy_socket.listen(MAX_CONN)
		proxy_ip = proxy_socket.getsockname()[0]
		print ("Proxy server running on ip address " + str(proxy_ip) + " and port number = " + str(proxy_socket.getsockname()[1]))
	except Exception as e: 
		print(e)
		# When specified address is already in use
		proxy_socket.close()
		sys.exit()


    # Listening and Accepting requests
	while 1:
		try:
			new_socket, c_addr = proxy_socket.accept()
			data = new_socket.recv(BUFFER_SIZE)
			t = threading.Thread(target=handle_parsing, args=(new_socket, c_addr, data))
			t.start()
		except KeyboardInterrupt:
			proxy_socket.close()
			sys.exit()

initiate_server()


