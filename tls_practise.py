# encoding=utf-8
import argparse
import socket
import ssl


def client(host, port, cafile=None):
    purpose = ssl.Purpose.SERVER_AUTH
    # tls 上下文
    # 保存对证书认证和加密算法选择的偏好设置
    # 指定创建该上下文对象的目的，ssl.Purpose.SERVER_AUTH表明该为客户端所用，
    # 用于验证其连接的服务器
    # cafile选项表明验证远程证书时信任的证书机构
    context = ssl.create_default_context(purpose, cafile=cafile)

    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.connect((host, port))
    print("connect to host {} and port {}".format(host, port))
    # 让openssl库控制tcp连接，然后与通信对方交换必要的握手信息，并建立加密连接
    # 客户端需要主机名，将主机名与服务端提供的证书的subject字段进行比对
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
    while True:
        data = ssl_sock.recv(1024)
        if not data:
            break
        print(repr(data))


def server(host, port, certfile, cafile=None):
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose, cafile=cafile)
    context.load_cert_chain(certfile)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host, port))
    listener.listen(1)

    print('listening at interface {} and port {}'.format(host, port))
    raw_sock, address = listener.accept()
    print('connection from host {} and port {}'.format(*address))

    ssl_sock = context.wrap_socket(raw_sock, server_side=True)

    ssl_sock.sendall('simple is better than complex'.encode('ascii'))
    ssl_sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='safe tls client and server')
    parser.add_argument('host', help='hostname or ip address')
    parser.add_argument('port', type=int, help='TCP port number')
    # -a 表示信任的证书
    parser.add_argument('-a', metavar='cafile', default=None, help='authority: path to CA cerfificate pem file')
    parser.add_argument('-s', metavar='certfile', default=None, help='run as server: path to server pem file')
    args = parser.parse_args()

    if args.s:
        server(args.host, args.port, args.s, args.a)
    else:
        client(args.host, args.port, args.a)

    # Note
    # 运行服务端：python tls_practise.py -s localhost.pem '' 1060
    # 运行客户端：python tls_practise.py -a ca_localhost.ca localhost  1060
    # 可以通过sudo tcpdump -n port 1060 -i lo0 -X来抓包
