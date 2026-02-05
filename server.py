# This program was modified by Abhishek Masur Jayatheertha / id: N01697721 

import socket
import argparse
import struct

def run_server(port, output_file):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the port (0.0.0.0 means all interfaces)
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save each received file as 'received_<ip>_<port>.jpg' based on sender.")
    sock.bind(server_address)

    # Keep listening for new transfers
    try:
        while True:
            f = None
            sender_filename = None
            
            # State for the current file transfer
            expected_seq_num = 0
            buffer = {} 

            while True:
                # Increased buffer size to accommodate header + data
                data, addr = sock.recvfrom(4096 + 16)
                
                # Protocol: If we receive a small packet (just header or empty), handle EOF
                # In reliable UDP, we check the sequence header first.
                if len(data) < 4:
                    continue

                # Parse the header
                header = data[:4]
                payload = data[4:]
                seq_num = struct.unpack('!I', header)[0]

                # Immediately send ACK for the received packet
                ack_packet = struct.pack('!I', seq_num)
                sock.sendto(ack_packet, addr)

                # Check if this is the "End of File" empty payload
                if not payload:
                    if f:
                        print(f"[*] End of file signal received from {addr}. Closing.")
                        f.close()
                        f = None
                    break

                if f is None:
                    print("==== Start of reception ====")
                    ip, sender_port = addr
                    # Reset state for new file
                    expected_seq_num = 0
                    buffer = {}
                    
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] First packet received from {addr}. File opened for writing as '{sender_filename}'.")

                # REORDERING
                if seq_num == expected_seq_num:
                    # Correct packet: Write to disk
                    f.write(payload)
                    expected_seq_num += 1

                    # Check buffer for subsequent packets
                    while expected_seq_num in buffer:
                        buffered_data = buffer.pop(expected_seq_num)
                        f.write(buffered_data)
                        expected_seq_num += 1
                
                elif seq_num > expected_seq_num:
                    # Packet arrived early: Buffer it
                    buffer[seq_num] = payload
                
                else:
                    # Duplicate packet (seq_num < expected_seq_num): Ignore
                    pass

            if f:
                f.close()
            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    try:
        run_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")