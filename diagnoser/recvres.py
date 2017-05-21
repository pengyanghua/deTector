import socket
import sys
import threading
import time
import globvar


'''
receive summary logs from pingers
'''


# argv[1] result directory
# argv[2] listening port
def recv_result(dir):
	global logger 
	
	# set logger
	logger = globvar.logger
	
	# create socket and bind
	sockfd = socket.socket()
	sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# Here, we set the server listening socket to have a timeout
	# duration of 3.0 seconds
	sockfd.settimeout(3.0)
	try:
		sockfd.bind((globvar.diagnoser_ip, globvar.diagnoser_listen_port))
	except socket.error as emsg:
		logger.error('Socket bind error: ' + str(emsg))
		sys.exit(1)

	# listen and accept new connection
	sockfd.listen(10000)
	
	# this is for keeping all threads' handlers
	cthread = []

	logger.info('Start recv result server, start loop...')
	
	# start the loop
	while True:
		try:
			# wait for incoming connection request			
			try:
				newfd, caddr = sockfd.accept()
			except socket.timeout:
				# raise a timeout exception if the timeout duration has elapsed
				# well, if no other exception, just call accept again
				continue

			# the system just accepted a new client connection
			# logger.info('A new client has arrived. It is at: ' + str(caddr))

			# generate a name to this client
			cname = caddr[0] + ':' + str(caddr[1])

			# create and start a new thread to handle this new connection
			thd = threading.Thread(name=cname, target= recv_res_thd, args=(newfd, dir,))
			thd.start()

			# add this new thread to cthread list
			cthread.append(thd)

		except KeyboardInterrupt:
			# if Cltr-C is detected, break out of the loop
			# and run the shutdown procedure
			logger.info('caught the KeyboardInterrupt')
			break

	# wait for all threads to terminate before termination of main thread
	for t in cthread:
		t.join()
	logger.info('All threads terminated.')

	

	

# this is the starting function of each client thread
def recv_res_thd(sockfd, path):
	
	# receive file name, file size; and create the file
	try:
		rmsg = sockfd.recv(100)
	except socket.error as emsg:
		logger.error('Socket recv error: ' + str(emsg))
		sys.exit(1)
	if rmsg == '':
		logger.error('Connection is broken')
		sys.exit(1)
	fname, filesize = rmsg.split(":")
	logger.info('Receiving a result file with name '+ fname + ' with size ' + str(filesize) + ' bytes.')
	try:
		fd = open(path+fname, 'wb')
	except IOerror as emsg:
		logger.error('File open error: ' + str(emsg))
		sys.exit(1)
	remaining = long(filesize)
	
	# send acknowledge - e.g., "OK"
	sockfd.send('OK')

	# receive the file contents
	# logger.info('Start receiving result file...')
	while remaining > 0L:
		rmsg = sockfd.recv(2048)
		if rmsg == '':
			logger.error('Connection is broken')
			sys.exit(1)
		fd.write(rmsg)
		remaining -= len(rmsg)

	# close connection
	# logger.info('[Recv result file Completed]')
	sockfd.close()
	fd.close()
	
	# termination
	return

	
	



