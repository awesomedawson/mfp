from mf_socket import MFSocket

def main():
    socket = MFSocket()
    socket.mf_bind(("", 4321))
    socket.mf_accept()
    message = socket.mf_read()
    print 'message received: ' + message

if __name__ == '__main__':
    main()
