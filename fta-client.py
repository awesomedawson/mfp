import sys
from mf_socket import MFSocket

def main():
	if len(sys.argv) != 4:
		print "USAGE: fta-client X A P"
		print "X: the port that the ftp-client's UDP port should bind to"
		print "A: the IP address of NetEmu"
		print "P: the UDP port number of NetEmu"
		sys.exit(0)

	client_udp_port = sys.argv[1]
	net_emu_ip = sys.argv[2]
	net_emu_udp_port = sys.argv[3]

	window = raw_input("Enter a window size W: ")

	# set up 
	socket = MFSocket(window_size=int(window), verbose=True)
	socket.mf_assign(int(client_udp_port))
	socket.mf_bind(("0.0.0.0", int(client_udp_port)))
	#socket.mf_connect(('127.0.0.1', 4321))
	socket.mf_connect((str(net_emu_ip), int(net_emu_udp_port)))


	while True:
		command = raw_input("Enter a command (connect-get f, disconnect): ")
		command = command.split()

		if command[0] == "disconnect":
			# disconnect from server
			socket.mf_close()
			sys.exit(0)

		elif command[0] == "connect-get":
			socket.mf_write(command[1])
			print "Sending file request: " + command[1]
			read_val = socket.mf_read()
			print "Recieved contents"
			f = open("copied_" + command[1], 'w')
			f.write(read_val)
			print "Saved file as: " + "copied_" + command[1]
			f.close()

		else:
			print "Invalid command"




if __name__ == '__main__':
    main()
