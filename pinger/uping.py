import socket
import sys
from struct import *
import time
from time import sleep
import threading
import random
import copy

import globvar
import sendres
import subprocess


# checksum functions needed for calculation checksum
def checksum(msg):
	s = 0

	# loop taking 2 characters at a time
	for i in range(0, len(msg), 2):
		w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
		s = s + w

	s = (s>>16) + (s & 0xffff);
	s = s + (s >> 16);

	# complement and mask to 4 byte short
	s = ~s & 0xffff
	return s


	

	
'''
		udp header
 0      7 8	 15 16    23 24    31  
 +--------+--------+--------+--------+ 
 |     Source      |   Destination   | 
 |      Port       |      Port       | 
 +--------+--------+--------+--------+ 
 |                 |                 | 
 |     Length      |    Checksum     | 
 +--------+--------+--------+--------+ 
 |                                     
 |          data octets ...            
 +---------------- ...                 

'''
# probe udp header
def udphdr(src_port, dest_port, udp_len, udp_cksum):
	# the ! in the pack format string means network order
	udp_header = pack('!HHH' , src_port, dest_port, udp_len) + pack('H', udp_cksum)
	return udp_header
	
	
	


	
	
'''
		pseudo header
  0      7 8     15 16    23 24    31 
 +--------+--------+--------+--------+
 |          source address           |
 +--------+--------+--------+--------+
 |        destination address        |
 +--------+--------+--------+--------+
 |  zero  |protocol|   UDP length    |
 +--------+--------+--------+--------+
'''	
# compute udp checksum
def udpcksum(src_ip, dest_ip, udp_hdr, payload):
	# pseudo header fields for computing checksum
	source_address = socket.inet_aton(src_ip)
	dest_address = socket.inet_aton(dest_ip)
	placeholder = 0
	protocol = socket.IPPROTO_UDP
	udp_length = len(udp_hdr) + len(payload)
	
	# udp pseudo header + udp header + payload for udp checksum
	pshdr = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , udp_length);
	pshdr = pshdr + udp_hdr + payload;
 
	udpcksum = checksum(pshdr)

	return udpcksum

	
	
	
	
	

	
'''
		probe payload
  0      7 8     15 16    23 24    31 
 +--------+--------+--------+--------+
 |          	sequence             |
 +--------+--------+--------+--------+
 |          pinger sentTime          |
 +--------+--------+--------+--------+
 |  	    target recvTime    	     |
 +--------+--------+--------+--------+
 |   tos  |reserved|
 +--------+--------+
'''
# probe packet payload, 14 bytes
def prbdata(seq, tos):
	pinger_sentTime = int(time.time())
	target_recvTime = 0
	reserved = 0
	
	payload = pack('IIIBB', seq, pinger_sentTime, target_recvTime, tos, reserved)
	return payload
	
	
	
	
	
	
# process received packets
def udprecv():
	try:
		recv_sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	except socket.error, msg:
		logger.error('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message: ' + str(msg[1]))
		sys.exit()
	
	try:
		recv_sockfd.bind((globvar.host_ip, globvar.pinger_listen_port))
	except socket.error, msg:
		logger.error('Socket bound failed. Error Code : ' + str(msg[0]) + ' Message: ' + str(msg[1]))
		sys.exit()
		
	# receive packets
	while(True):
		(recvpkt, addr) = recv_sockfd.recvfrom(1500)
		recvpkt_src_ip = addr[0]
		recvpkt_src_port = addr[1]
		
		# extract payload
		try:
			payload = unpack('IIIBB', recvpkt[0:14])
		except:
			logger.error('Unpack requires a string argument of length 14')
			continue
			
		seq = payload[0]
		pinger_sentTime = payload[1]
		target_recvTime = payload[2]
		payload_tos = payload[3]
		
		logger.info('receive one response from ' + recvpkt_src_ip + ', ECN: ' + str(payload_tos%4))
		
		# acknowledge this pkt
		with threading.Lock():
			if seq in unackpkts.keys():
				pathID = unackpkts[seq]
				del unackpkts[seq]
				
				try:
					(sent, ack) = loss[pathID] 	# key error when shutdown responder: KeyError '1'
					ack = ack + 1
					loss[pathID] = (sent, ack)
				except:
					logger.error('KeyError! Maybe caused by responder shutdown.')
			else:
				logger.error('Received unexpected packets.')
	
	


'''
ping process:
for each tos:
	for each path:
		for each src_port:
			send a probe
			sleep(interval)
'''
# send ping probes
def udpping():

	try:
		ping_sockfd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)  
	except socket.error, msg:
		logger.error('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message: ' + str(msg[1]))
		sys.exit()

	# non-stop ping
	while(True):	
		seq = random.randint(0, 10000)	# each time we randomly generate an initial sequence number
		src_ip = globvar.host_ip
		dest_port = globvar.responder_listen_port
		dscplist = [i for i in range(8)]		# tos = dscp + ecn
		interval = globvar.interval
		version = globvar.version
		pathlist = []
		with globvar.pathlist_lock:
			pathlist = copy.deepcopy(globvar.pathlist)

		for dscp in dscplist:
			for path in pathlist:
				src_port = random.randint(10000, 60000)
				(pathID, dest_ip, coreswitch_id) = path
				ecn = int(coreswitch_id)	
				tos = dscp*4 + ecn

				ping_sockfd.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)  # set tos  
			
				# prepare payload and packet header
				payload = prbdata(seq, tos)
				udp_hdr = udphdr(src_port, dest_port, len(payload)+8, 0)
			
				udp_cksum = udpcksum(src_ip, dest_ip, udp_hdr, payload)
				udp_hdr = udphdr(src_port, dest_port, len(payload)+8, udp_cksum)
			
				# construct the packet
				packet = udp_hdr + payload
			
				# send the packet finally - the port specified has no effect
				ping_sockfd.sendto(packet, (dest_ip , dest_port))
			
				logger.info('send one probe out, dest_ip: ' + dest_ip + ', ECN: ' + str(ecn))
			
				# update loss and seq
				with threading.Lock():
					unackpkts[seq] = pathID
					if pathID in loss.keys():
						(sent, ack) = loss[pathID] 
						sent = sent + 1
						loss[pathID] = (sent, ack)
					else:
						loss[pathID] = (1, 0)
				seq = (seq + 1) % (sys.maxint)
			
				sleep(interval)
		
		
		while(globvar.version <= version):
			sleep(1)

		

	
def uping():
	global logger, unackpkts, loss
	logger = globvar.logger
	loss = {}	# (pathID, (sent, ack))
	unackpkts = {}	# (seq, pathID)
	
	# create two threads, one for sending pkts and another for receiving pkts
	thrd_recv = threading.Thread(name='recv', target= udprecv)
	thrd_recv.setDaemon(True)	# the child thread will forcefully exit if parent exits
	thrd_recv.start()
	
	thrd_ping = threading.Thread(name='ping', target=udpping)
	thrd_ping.setDaemon(True)
	thrd_ping.start()
	
	result_version = 0
	while(True):
		sleep(53)
		
		# upload ping result to diagnoser every 60 seconds
		fN = globvar.send_result_dir + 'result-' + globvar.host_ip + '-' + str(result_version) + '.xml'
		fh = open(fN, 'w')
		fh.write('<result>' + '\n')
		fh.write('sys_choice:' + str(globvar.sys_choice) + '\n')
		with threading.Lock():
			for pathID in loss.keys():
				fh.write('path-' + pathID + ':' + str(loss[pathID]) + '\n')
			loss = {}
		fh.write('</result>' + '\n')
		fh.close()
		
		# send to diagnoser
		diagnoser_addr = (globvar.diagnoser_ip, globvar.diagnoser_listen_port)
		sendres.send_result(diagnoser_addr, fN)
		
		result_version = result_version + 1
		sleep(7)	
	
	
	

if __name__ == "__main__":
	udpping()
	
	
	
