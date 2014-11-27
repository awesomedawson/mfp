mfp
===

To run fta-server:
python fta-server <server_port> <NetEmu_IP> <NetEmu_port>
Next enter a window size (in packets)
The client can now connect to the server.
Control+c closes the server and closes connections to the client.


To run fta-client:
python fta-client <server_port> <NetEmu_IP> <NetEmu_port>
enter a window size (in packets)
then enter one of the following commands:
	connect-get f: get the specified file from the server
	disconnect: closes the connection to the server and returns