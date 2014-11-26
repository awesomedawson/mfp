import sys
from mf_socket import MFSocket
import os.path

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
	socket = MFSocket(window_size=int(window), verbose=True)
	socket.mf_bind(("", int(server_udp_port)))
	socket.mf_accept()
	destination = socket.destination
	print "server set up"

	while True:
		message = socket.mf_read()
		print "Accepted file request: " + message
		
		if message == '':
			pass
		if not os.path.isfile(message):
			print "Received file request that doesn't exist!"
			pass

		f = open(message, 'r')
		
		contents = f.read()
		print "Sending contents"
		socket.mf_write(contents)
		f.close()
		raw_input("Press any key to accept more connections")

if __name__ == '__main__':
	main()
