import socket, sys, threading, struct, argparse

# port & host used
PORT = 2908
HOST = socket.gethostname()

def readTCPdata(connection, address):
    # the server receives info pack from client (in proper byte format)
    # and unpack it obtaining finally the size of chosen file (int = 4B) and stop-and-wait procedure enabled/disabled (bool = 1B)
    input_bytes, chunks = 0, 0
    print("created a thread for ", address)
    bytes_received_from_client = connection.recv(5)
    size, stop_and_wait_enabled = struct.unpack('i?', bytes_received_from_client)
    print("Received from client ", address)
    print("Input size: ", size)
    print("Stop and wait enabled: ", "Yes" if stop_and_wait_enabled else "No")

    while True:
        # the server receives first the size of file chosen by the client
        # then, using this size it will receive the content of the chosen file
        if stop_and_wait_enabled:
            received_bytes = connection.recv(4)
            if not received_bytes:
                break
            file_bytes_tbr = struct.unpack('i', received_bytes)[0]

            # the file content is brought to the server in chunks of chosen size
            content = connection.recv(size)

            # in case when the brought content size and the input one are not equal
            # the server tries to bring the rest of it
            content_size = len(content)
            while content_size != file_bytes_tbr:
                print("uncomplete chunk detected, trying to recover the lost content")
                content = connection.recv(size - content_size)
                content_size += len(content)
            connection.send(struct.pack('i', 1))  # -> send acknowledgment to client
        else:
            content = connection.recv(size)
        
        if not content:
            break
        chunks += 1
        
        # input_bytes represent the number of bytes introduced by the user
        if stop_and_wait_enabled:
            input_bytes += file_bytes_tbr
        else:
            input_bytes += len(content)
    connection.close()
    print("Used protocol: TCP")
    print("Bytes read:", input_bytes) 
    print("Chunks sent:", chunks)


def server(server_type):

    if server_type == 0:
        # creating a TCP socket using SO_REUSEADDR option
        # followed by its binding
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        print("TCP socket created and binded to port %s" % (PORT))

        # the TCP server will start listening if there are clients who want to connect
        server.listen(5)
        print("socket listening...")

        while True:
            # serving clients using a thread which will start reading data received from client
            connection, address = server.accept()
            print("got connection from ", address)
            threading.Thread(target=readTCPdata, args=(connection, address)).start()

    elif server_type == 1:
        # creating a UDP socket using SO_REUSEADDR option
        # followed by its binding
        # the UDP server will start listening immediately after it's being created
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        print("UDP socket created and binded to port %s" % (PORT))

        while True:
            # the server receives info pack from client (in proper byte format)
            # and unpack it obtaining finally the size of chosen file (int = 4B) and stop-and-wait procedure enabled/disabled (bool = 1B)
            input_bytes, chunks = 0, 0
            bytes_received_from_client, address = server.recvfrom(5)
            size, stop_and_wait_enabled = struct.unpack('i?', bytes_received_from_client)
            server.settimeout(3)

            while True:
                try:        
                    # the server receives first the size of file chosen by the client
                    # then, using this size it will receive the content of the chosen file
                    if stop_and_wait_enabled:
                        received_bytes, client_address = server.recvfrom(4)
                        file_bytes_tbr = struct.unpack('i', received_bytes)[0]
                        server.sendto(struct.pack('i', 1), client_address)

                        # the file content is brought to the server in chunks of chosen size
                        content, client_address = server.recvfrom(size)

                        # in cases when the brought content size and the input one are not equal
                        # in such case the server tries to bring the rest of it
                        content_size = len(content)
                        while content_size != file_bytes_tbr:
                            print("uncomplete chunk detected, trying to recover the lost content")
                            content, client_address = server.recvfrom(size)
                            content_size += len(content)
                        server.sendto(struct.pack('i', 1), client_address)
                    else:
                        content, client_address = server.recvfrom(size)
                    chunks += 1

                    # input_bytes represent the number of bytes introduced by the user
                    if stop_and_wait_enabled:
                        input_bytes += file_bytes_tbr
                    else:
                        input_bytes += len(content)
                except:
                    server.settimeout(None)
                    print("From address: ", client_address)
                    print("Used protocol: UDP")
                    print("Bytes read:", input_bytes) 
                    print("Messages sent:", chunks)
                    break

parser = argparse.ArgumentParser()
parser.add_argument("--protocol", default=0, type=int, help="Pick a protocol: 0 for TCP, 1 for UDP")
options = parser.parse_args()
protocol = options.protocol
server(protocol)
