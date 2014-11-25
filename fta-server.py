import sys.argv

def main():
	if len(sys.argv) != 4 
		print "USAGE: fta-server X A P"
		print "X: the port number at which the fta-server's UDP socket should bind to"
		print "A: the IP address of NetEmu"
		print "P: the UDP port number of NetEmu"

	server_udp_port = sys.argv[1]
	net_emu_ip = sys.argv[2]
	net_emu_udp_port = sys.argv[3]

	# set up server here

	while True:
		command = raw_input("Enter a command (window W, terminate): ")
		command = command.split()

		if command[0] == "terminate":
			# terminate server
			pass

		else if command[1] == "window":
			# set window here
			pass

		else:
			print "Invalid command"



if __name__ == '__main__':
    main()
