import sys
import socket

if len(sys.argv) < 2:
        print("Please input port number")
        exit()
PORT = int(sys.argv[1])

SERVER = "0.0.0.0"

# Initialize socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER, PORT))

server_socket.listen(1)

print('Listening on port %s ... ' % PORT)

while True:
    # Wait for client connection
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    # Parse HTTP headers
    headers = request.split('\n')
    filename = headers[0].split()[1]

    print(filename)

    # Get the contents of the file
    if filename == '/':
        filename = '/index.html'

    try:
        fin = open('public' + filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.0 200 OK\n\n' + content

    except IOError:

        response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'

    # Send HTTP response
    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
server_socket.close()
