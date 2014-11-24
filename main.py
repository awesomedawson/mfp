from mf_socket import MFSocket

def main():
    socket = MFSocket()
    socket.mf_bind(('0.0.0.0', 1234))
    socket.mf_listen()
    socket.mf_accept()

if __name__ == '__main__':
    main()
