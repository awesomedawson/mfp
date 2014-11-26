from mf_socket import MFSocket

def main():
    socket = MFSocket(verbose = True)
    socket.mf_bind(('', 4321))
    socket.mf_accept()
    message = socket.mf_read()
    print 'message received: ' + message
    print 'press any key to exit'
    raw_input()

if __name__ == '__main__':
    main()
