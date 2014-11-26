from mf_socket import MFSocket

def main():
    socket = MFSocket(verbose = True)
    socket.mf_assign(1234)
    socket.mf_connect(('127.0.0.1', 4321))
    socket.mf_write('hello. this is a test. 1234567890    xxxxxx')
    print 'press any key to exit.'
    raw_input()

if __name__ == '__main__':
    main()
