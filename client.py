from mf_socket import MFSocket

def main():
    socket = MFSocket(1234)
    #socket.mf_connect(('10.0.1.14', 4321))
    socket.mf_connect(('127.0.0.1', 4321))

if __name__ == '__main__':
    main()
