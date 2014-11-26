import sys
from mf_socket import MFSocket

def main():
	if len(sys.argv) != 4:
		print "USAGE: fta-server X A P"
		print "X: the port number at which the fta-server's UDP socket should bind to"
		print "A: the IP address of NetEmu"
		print "P: the UDP port number of NetEmu"
		sys.exit(0)

	server_udp_port = sys.argv[1]
	net_emu_ip = sys.argv[2]
	net_emu_udp_port = sys.argv[3]

	window = raw_input("Enter a window size W: ")
	print "Control + c to terminate"
	
	# set up server here
	socket = MFSocket(window_size=window, verbose=True)
	socket.mf_bind(("", int(server_udp_port)))
	print "server set up"

	while True:
		socket.mf_accept()
		destination = socket.destination
		message = socket.mf_read()
		print "Accepted file request: " + message
		f = open(message, 'r').read()
		print "Sending contents: " + f
		socket.mf_write(f)
		f.close()

if __name__ == '__main__':
    main()
