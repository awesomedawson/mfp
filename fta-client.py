import sys.argv

def main():
	if len(sys.argv) != 4 
		print "USAGE: fta-client X A P"
		print "X: the port number at which the fta-client’s UDP socket should bind to"
		print "A: the IP address of NetEmu"
		print "P: the UDP port number of NetEmu"

	client_udp_port = sys.argv[1]
	net_emu_ip = sys.argv[2]
	net_emu_udp_port = sys.argv[3]

	# set up 

	while True:
		command = raw_input("Enter a command (connect-get f, window W, disconnect): ")
		command = command.split()

		if command[0] == "disconnect":
			# disconnect from server
			pass

		else if command[0] == "window":
			# set window here
			pass

		else if command[0] == "connect-get":
			# get file f from server
			pass

		else:
			print "Invalid command"


if __name__ == '__main__':
    main()
