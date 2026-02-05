# This program was modified by Abhishek Masur Jayatheertha / id: N01697721 

import socket
import argparse
import time
import os
import struct

def run_client(target_ip, target_port, input_file):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set timeout for Stop-and-Wait
    sock.settimeout(0.5)
    
    server_address = (target_ip, target_port)
    sequence_number = 0

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            while True:
                # Read a chunk of the file
                chunk = f.read(1024) 
                
                # Create the packet with header
                header = struct.pack('!I', sequence_number)
                
                # Check for EOF
                if not chunk:
                    # Send empty packet with sequence number to signal EOF
                    packet = header + b'' 
                else:
                    packet = header + chunk

                # RELIABILITY LOGIC (Stop-and-Wait)
                ack_received = False
                while not ack_received:
                    try:
                        # Send the chunk
                        sock.sendto(packet, server_address)
                        
                        # Wait for ACK
                        data, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack('!I', data)[0]
                        
                        if ack_seq == sequence_number:
                            ack_received = True
                            sequence_number += 1
                        
                    except socket.timeout:
                        # Timeout detected, loop repeats to retransmit
                        print(f"Timeout on Seq {sequence_number}, Retransmitting...")
                        continue
                
                # If only sent the EOF packet , break the loop
                if not chunk:
                    break

        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)