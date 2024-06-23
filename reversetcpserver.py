import socket
import struct
import select

server_ip = '127.0.0.1'
server_port = 12345

# 处理客户端请求的函数
def handle_client(client_socket):
    while True:
        try:
            # 读取消息类型
            msg_type = struct.unpack("!H", client_socket.recv(2))[0]

            if msg_type == 1:  # 初始化消息
                num_blocks = struct.unpack("!I", client_socket.recv(4))[0]
                # 发送确认消息
                client_socket.send(struct.pack("!H", 2))
            elif msg_type == 3:  # 反转请求消息
                data_len = struct.unpack("!I", client_socket.recv(4))[0]
                # 读取数据
                data = client_socket.recv(data_len)
                # 反转数据
                reversed_data = data[::-1]
                # 发送反转结果
                client_socket.send(struct.pack("!H", 4) + struct.pack("!I", data_len) + reversed_data)
        except Exception as e:
            print(f"客户端连接错误: {e}")
            break

    client_socket.close()

def main():


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定 IP 和端口
        server_socket.bind((server_ip, server_port))
        # 监听客户端连接
        server_socket.listen(5)
        # 允许地址重用
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"服务器正在监听 {server_ip}:{server_port}")

        # 创建一个列表来存储所有客户端套接字
        client_sockets = [server_socket]

        while True:
            # 使用 select 检查是否有套接字就绪
            ready_to_read, _, _ = select.select(client_sockets, [], [])

            for sock in ready_to_read:
                if sock == server_socket:  # 如果是服务器套接字，表示有新的连接
                    client_socket, client_addr = server_socket.accept()
                    print(f"接受来自 {client_addr} 的连接")
                    client_sockets.append(client_socket)
                else:
                    # 如果是客户端套接字，表示有数据到达
                    handle_client(sock)
                    # 从客户端套接字列表中移除已处理的套接字
                    client_sockets.remove(sock)

if __name__ == "__main__":
    main()
