
import socket, select, struct, random

# local config
#bind_ip, bind_port = socket.gethostbyname('TODO: local relay private address'), 24540
#src_ip, src_port = socket.gethostbyname('TODO: workstation private address'), None
#dst_ip, dst_port = socket.gethostbyname('TODO: remote relay public address'), 24540
#plaintext_side = src_ip

# remote config
bind_ip, bind_port = socket.gethostbyname('TODO: remote relay public address'), 24540
src_ip, src_port = socket.gethostbyname('TODO: local relay public address'), None
dst_ip, dst_port = socket.gethostbyname('TODO: vpn access point address'), 1194
plaintext_side = dst_ip

def encode(msg: bytes):
    #print('SlippyUDP: encode')
    msg = struct.pack('!H', len(msg)) + msg
    n_pad = random.randrange(1400) - len(msg)
    if (n_pad > 0):
        msg = msg + random.randbytes(n_pad)
    msg = msg[::-1]
    return msg

def decode(msg: bytes):
    #print('SlippyUDP: decode')
    msg = msg[::-1]
    n,  = struct.unpack('!H', msg[0 : 2])
    msg = msg[2 : (2 + n)]
    assert len(msg) == n
    return msg

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, bind_port))
    print('SlippyUDP: ready')
    
    while True:
        read_ready, _, _ = select.select([sock], [], [], 1)
        if sock in read_ready:
            try:
                data, addr = sock.recvfrom(4096)
                #print(f'SlippyUDP: got {len(data)} bytes from {addr}')
                
                ip, port = addr
                if ip == src_ip:
                    src_port = port
                    addr = (dst_ip, dst_port)
                elif ip == dst_ip:
                    addr = (src_ip, src_port)
                else:
                    addr = None
                
                if addr:
                    if ip == plaintext_side:
                        data = encode(data)
                    else:
                        data = decode(data)
                    
                    #print(f'SlippyUDP: sending to {addr}')
                    sock.sendto(data, addr)
                
            except:
                pass
