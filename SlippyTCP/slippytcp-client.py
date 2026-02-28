
import sys, socket, select, socketserver, struct, random

# local config
bind_ip = socket.gethostbyname('TODO: local relay private address')
bind_port_udp = 24153
src_ip = socket.gethostbyname('TODO: workstation private address')
src_port = None
dst_ip = socket.gethostbyname('TODO: remote relay public address')
dst_port = 24154
SOCKET_BUFFER_SIZE = 16 * 1024 * 1024
SOCKET_TIMEOUT_SEC = 120
GARBAGE_LIMIT = 64

def tune_tcp_side(sock: socket.socket):
    sock.settimeout(SOCKET_TIMEOUT_SEC)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFER_SIZE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFER_SIZE)

def tune_udp_side(sock: socket.socket):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFER_SIZE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFER_SIZE)

def recvall(sock: socket.socket, n: int, /):
    data, count = [], 0
    while count < n:
        packet = sock.recv(n - count)
        if not packet:
            raise EOFError(f'Read {count} bytes from socket, expected {n} bytes')
        data.append(packet)
        count += len(packet)
    return b''.join(data)

def run_tunnel(tcp_side: socket.socket, udp_side: socket.socket):
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
            
            udp_side.sendto(data, (src_ip, src_port))
        
        if udp_side in read_ready:
            data, addr = udp_side.recvfrom(65507)
            
            ip, port = addr
            if ip == src_ip:
                src_port = port
                
                garbage_count, data_count = random.randrange(GARBAGE_LIMIT), len(data)
                header = struct.pack('!HH', garbage_count, data_count)
                
                garbage = random.randbytes(garbage_count)
                data = data[::-1]
                
                tcp_side.sendall(header + garbage + data)

if __name__ == '__main__':
    while True: # fail-fast
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_side:
                tune_tcp_side(tcp_side)
                tcp_side.connect((dst_ip, dst_port))
                
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_side:
                    tune_udp_side(udp_side)
                    udp_side.bind((bind_ip, bind_port_udp))
                    
                    run_tunnel(tcp_side, udp_side)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            pass
