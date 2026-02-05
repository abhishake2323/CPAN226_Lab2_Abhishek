# CPAN 226 - Lab 2: Reliable Transport over UDP

## 1. Overview
This project upgrades a simple UDP file transfer application to handle a chaotic network environment. The original application provided no guarantees regarding packet delivery or order. This submission implements a Reliable Data Transfer (RDT) protocol to handle:
* **Packet Loss:** Using a Stop-and-Wait protocol with timeouts.
* **Out-of-Order Delivery:** Using sequence numbers and server-side buffering.

## 2. Implementation Details

### Part 1: Reliability (Stop-and-Wait)
To handle packet loss, the client adds a 4-byte Sequence Number header to every packet. It sends one packet at a time and waits for an Acknowledgement (ACK) from the server.
* If the ACK is received, the client sends the next packet.
* If the ACK is not received within **0.5 seconds** (timeout), the client assumes the packet was lost and retransmits it.

### Part 2: Ordering (Buffer Logic Explanation)
To fix corrupted images caused by out-of-order packets, the server does not write data immediately. Instead, it tracks the `expected_seq_num`.
* **If a packet arrives efficiently (in order):** It is written to the file immediately, and the `expected_seq_num` is incremented.
* **If a packet arrives early (out of order):** It is stored in a `buffer` dictionary (`{seq_num: data}`) for later use.
* **The Crucial Step:** After writing any packet, the server checks the buffer to see if the *next* expected packet is already waiting there. If it is, the server retrieves it, writes it, and updates the expected counter. This loop continues until the sequence gap is filled, ensuring the file is reconstructed perfectly linearly.

## 3. How to Run

To verify the solution, open three separate terminals.

**Terminal 1 (Server):**
```bash
python server.py --port 12001 --output received_relay.jpg

**Terminal 1 (Server):**
```bash
python relay.py --bind_port 12000 --server_port 12001 --loss 0.3 --reorder 0.2

**Terminal 1 (Server):**
```bash
python client.py --target_port 12000 --file old_lady.jpg