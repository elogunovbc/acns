
import sys, socket, select, socketserver, struct, random

# remote config
bind_ip = socket.gethostbyname('TODO: remote relay public address')
bind_port_tcp = 24154
bind_port_udp = 24155
src_ip = socket.gethostbyname('TODO: local relay public address')
dst_ip = socket.gethostbyname('TODO: vpn access point address')
dst_port = 1194
SOCKET_BUFFER_SIZE = 16 * 1024 * 1024
SOCKET_TIMEOUT_SEC = 120
GARBAGE_LIMIT = 64

def recvall(sock: socket.socket, n: int, /):
    data, count = [], 0
    while count < n:
        packet = sock.recv(n - count)
        if not packet:
            raise EOFError(f'Read {count} bytes from socket, expected {n} bytes')
        data.append(packet)
        count += len(packet)
    return b''.join(data)

class TunnelHandler(socketserver.StreamRequestHandler):
    def tune_tcp_side(self, sock: socket.socket):
        sock.settimeout(SOCKET_TIMEOUT_SEC)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFER_SIZE)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFER_SIZE)
    
    def tune_udp_side(self, sock: socket.socket):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFER_SIZE)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFER_SIZE)
    
    def run_tunnel(self, tcp_side: socket.socket, udp_side: socket.socket):
        print('SlippyTCP: run_tunnel()')
        sock_list = [tcp_side, udp_side]
        while True:
            read_ready, _, _ = select.select(sock_list, [], [], 0.5)
            
            if tcp_side in read_ready:
                header = recvall(tcp_side, 4)
                garbage_count, data_count = struct.unpack('!HH', header)
                
                garbage = recvall(tcp_side, garbage_count)
                data = recvall(tcp_side, data_count)
                
                data = data[::-1]
                
                udp_side.sendto(data, (dst_ip, dst_port))
            
            if udp_side in read_ready:
                data, addr = udp_side.recvfrom(65507)
                
                ip, port = addr
                if ip == dst_ip:
                    garbage_count, data_count = random.randrange(GARBAGE_LIMIT), len(data)
                    header = struct.pack('!HH', garbage_count, data_count)
                    
                    garbage = random.randbytes(garbage_count)
                    data = data[::-1]
                    
                    tcp_side.sendall(header + garbage + data)
    
    def handle(self):
        #print(f'SlippyTCP: connection accepted from {self.client_address}')
        try:
            ip, port = self.client_address
            if ip == src_ip:
                tcp_side = self.connection
                self.tune_tcp_side(tcp_side)
                
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_side:
                    self.tune_udp_side(udp_side)
                    udp_side.bind((bind_ip, bind_port_udp))
                    
                    self.run_tunnel(tcp_side, udp_side)
        finally:
            self.server.close_request(self.request)

if __name__ == '__main__':
    try:
        with socketserver.ThreadingTCPServer((bind_ip, bind_port_tcp), TunnelHandler) as server:
            print('SlippyTCP: ready')
            server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
