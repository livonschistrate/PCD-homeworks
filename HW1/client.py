import socket, sys, struct, time, argparse

# port & host used
PORT = 2908
HOST = socket.gethostname()

def client(protocol, size, stop_and_wait_enabled, filename):
    if protocol == 0:
        # creating a TCP socket using SO_REUSEADDR option
        # followed by opening connection
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST, PORT))

        # creating a byte-formatted packet which contains info about chunk size and stop-and-wait indicator
        # this packet will be sent to server
        packed_string = struct.pack('i?', size, stop_and_wait_enabled)
        server.send(packed_string)
        chunks, output_bytes = 0, 0

        # we open the specified file and read the content into x-sized chunks
        with open(filename, "rb") as file:
            start_time = time.time()
            while True:
                input_bytes = file.read(size)
                if len(input_bytes) != 0:
                    if stop_and_wait_enabled:
                        server.send(struct.pack('i', len(input_bytes)))
                        output_bytes += server.send(input_bytes)
                        acknowledgment = struct.unpack('i', server.recv(4))
                    else:
                        output_bytes += server.send(input_bytes)
                    chunks += 1
                else:
                    break
            end_time = time.time()
        server.close()
        print("Transmission time:", end_time - start_time)
        print("Chunks of size %s sent: %s" % (size, chunks))
        print("Bytes sent:", output_bytes)
        # return output_bytes, chunks, end_time - start_time
    
    elif protocol == 1:
        # creating a UDP socket using SO_REUSEADDR option
        # connection is opened at the creation of the socket
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # creating a byte-formatted packet which contains info about chunk size and stop-and-wait indicator
        # this packet will be sent to server
        packed_string = struct.pack('i?', size, stop_and_wait_enabled)
        server.sendto(packed_string, (HOST, PORT))
        chunks, output_bytes = 0, 0

        # we open the specified file and read the content into x-sized chunks
        with open(filename, "rb") as file:
            start_time = time.time()
            while True:
                input_bytes = file.read(size)
                if len(input_bytes) != 0:
                    if stop_and_wait_enabled:
                        server.sendto(struct.pack('i', len(input_bytes)), (HOST, PORT))
                        server.recvfrom(4)
                        output_bytes += server.sendto(input_bytes, (HOST, PORT))
                        server.recvfrom(4)
                    else:
                        output_bytes += server.sendto(input_bytes, (HOST, PORT))
                        acknowledge_approved = True
                    chunks += 1
                else:
                    break
            end_time = time.time()
        print("Transmission time:", end_time - start_time)
        print("Chunks of size %s sent: %s" % (size, chunks))
        print("Bytes sent:", output_bytes)


# the client chooses the protocol, chunk size, file and enables stop-and-wait procedure
# all these inputs will be used to initiate communication with the server and transmit the bytes from the file into chunks
parser = argparse.ArgumentParser()
parser.add_argument("--protocol", default=0, type=int, help="Pick a protocol: 0 for TCP, 1 for UDP")
parser.add_argument("--size", default=256, type=int, help="Choose message size")
parser.add_argument("--saw", default="n", type=str, help="Enable stop-and-wait [Y/n]")
parser.add_argument("--filename", default="files/filename.txt", type=str, help="Path of file")
options = parser.parse_args()
protocol = options.protocol
size = options.size
stop_and_wait_enabled = options.saw
if stop_and_wait_enabled == 'n':
    stop_and_wait_enabled = False
else:
    stop_and_wait_enabled = True
filename = options.filename
result = client(protocol, size, stop_and_wait_enabled, filename)