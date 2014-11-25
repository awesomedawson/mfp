from mf_socket import MFSocket

def main():
    socket = MFSocket(4321)
    socket.mf_bind(("", 4321))
    socket.mf_accept()

if __name__ == '__main__':
    main()
