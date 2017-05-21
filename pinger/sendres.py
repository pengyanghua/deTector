# send log to the analyzer
import socket
import os.path
import os
import sys
import time
import random
import globvar

# send the result file to the diagnoser
# diagnoser_addr: the ip address and port of analyzer
# res_path: the directory and name of the result file
# return 0 if successfully send
def send_result(diagnoser_addr, res_path):
	logger = globvar.logger
	
	# open the target log file; get file size
	try:
		fsize = os.path.getsize(res_path)
	except os.error as emsg:
		logger.error('File error: ' + str(emsg))
		return -1

	fd = open(res_path, 'rb')

	# create socket and connect to server
	try:
		sockfd = socket.socket()
		sockfd.connect(diagnoser_addr)
	except socket.error as emsg:
		logger.error('Socket error: ' + str(emsg))
		return -1

	# once the connection is set up;
	# send file name and file size as one string separate by ':'
	# e.g., result1.txt:4096
	res_name = res_path.split('/')[-1]
	msg = res_name + ':' + str(fsize)
	sockfd.send(msg)

	# receive acknowledge - e.g., "OK"
	rmsg = sockfd.recv(10)

	if rmsg != "OK":
		logger.error('Received a negative acknowledgment.')
		return -1

	# send the log
	logger.info('Start sending ' + res_name + '...')
	remaining = fsize
	while remaining > 0:
		smsg = fd.read(1024)
		mlen = len(smsg)
		if mlen == 0:
			logger.error('EOF is reached, but still have ' + str(remaining) + ' bytes to read !!!')
			return -1
		try:
			sockfd.sendall(smsg)
		except socket.error as emsg:
			logger.error('Socket sendall error: ' + str(emsg))
			return -1
		remaining -= mlen

	# close connection
	logger.info('[Send result completed].')
	sockfd.close()
	fd.close()
	
	# remove this file
	os.remove(res_path)
	return 0



if __name__ == '__main__':
	post()
	
	
	
	
