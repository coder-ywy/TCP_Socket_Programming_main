import socket
import random
import struct
import sys

if len(sys.argv) < 6:
    print('Usage: python reversetcpclient.py <server_ip> <server_port> <Lmin> <Lmax> <file_path>')
    sys.exit(1)

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
Lmin = int(sys.argv[3])
Lmax = int(sys.argv[4])
file_path = sys.argv[5]
if Lmin >= Lmax:
    print("Error: Lmin should be less than Lmax")
    sys.exit(1)

def send_initialization(sock, num_blocks):
    msg_type = struct.pack("!H", 1)
    num_blocks_packed = struct.pack("!I", num_blocks)
    sock.send(msg_type + num_blocks_packed)


def send_reverse_request(sock, data):
    msg_type = struct.pack("!H", 3)
    data_len = len(data)
    data_len_packed = struct.pack("!I", data_len)
    sock.send(msg_type + data_len_packed + data)


def receive_reverse_answer(sock):
    msg_type = struct.unpack("!H", sock.recv(2))[0]
    data_len = struct.unpack("!I", sock.recv(4))[0]
    reversed_data = sock.recv(data_len)
    return reversed_data


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))

        with open(file_path, 'r',encoding='utf-8') as file:
            ascii_text = file.read()

        block_lengths = []
        remaining_text = ascii_text
        while remaining_text:
            # 随机选择分块大小
            block_size = random.randint(Lmin, Lmax)
            # 如果剩余部分小于分块大小，则将剩余部分作为一个新块
            if len(remaining_text) <= block_size:
                block_lengths.append(len(remaining_text))
                remaining_text = ""
            else:
                block_lengths.append(block_size)
                remaining_text = remaining_text[block_size:]

        send_initialization(sock, len(block_lengths))

        reversed_blocks = []
        flag=0
        for i, length in enumerate(block_lengths):
            data_block = ascii_text[:length]
            ascii_text = ascii_text[length:]

            send_reverse_request(sock, data_block.encode())

            if (flag==0) :
                sock.recv(2)
                reversed_data = receive_reverse_answer(sock)
                flag=1
            else :
                reversed_data = receive_reverse_answer(sock)
            reversed_blocks.append(reversed_data.decode())
            print(f"第{i + 1}块：{reversed_data.decode()}")

        reversed_blocks.reverse()
        complete_reversed_text = ''.join(reversed_blocks)
        print("完整的反转文本：", complete_reversed_text)

        with open('reversed_text.txt', 'w') as file:
            file.write(complete_reversed_text)

if __name__ == "__main__":
    main()

