import socket
import sys
from struct import *
import time

import globvar




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
def prbdata(recv_payload):
	seq = recv_payload[0]
	pinger_sentTime = recv_payload[1]
	target_recvTime = int(time.time())	# timestamp
	tos = recv_payload[3]
	reserved = recv_payload[4]
	
	sent_payload = pack('IIIBB', seq, pinger_sentTime, target_recvTime, tos, reserved)
	return sent_payload


		
	
	
	

def udppong():
	global logger
	
	logger = globvar.logger
	
	try:
		sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		reply_sockfd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
	except socket.error, msg:
		logger.error('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message: ' + str(msg[1]))
		sys.exit()
	try:
		sockfd.bind((globvar.host_ip, globvar.responder_listen_port))
	except socket.error, msg:
		logger.error('Socket bound failed. Error Code : ' + str(msg[0]) + ' Message: ' + str(msg[1]))
		sys.exit()
		
	while(True):
		# receive packets
		(recvpkt, addr) = sockfd.recvfrom(1500)
		recvpkt_src_ip = addr[0]
		recvpkt_src_port = addr[1]


		# extract payload
		try:
			payload = unpack('IIIBB', recvpkt[0:14])
		except:
			logger.error('Unpack requires a string argument of length 14')
			continue
			
		tos = payload[3]
		reserved = payload[4]
		# construct a pong packet
		src_ip = globvar.host_ip
		dest_ip = recvpkt_src_ip
		src_port = globvar.responder_listen_port
		if reserved == 0:
			dest_port = globvar.pinger_listen_port
		
		payload = prbdata(payload)
		udp_hdr = udphdr(src_port, dest_port, len(payload)+8, 0)
		udp_cksum = udpcksum(src_ip, dest_ip, udp_hdr, payload)
		udp_hdr = udphdr(src_port, dest_port, len(payload)+8, udp_cksum)
		
		# construct the packet
		packet = udp_hdr + payload
		
		# set socket tos
		reply_sockfd.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)
		
		# send the packet finally - the port specified has no effect
		reply_sockfd.sendto(packet, (dest_ip, dest_port))
		
		logger.info('reply one packet from ' + recvpkt_src_ip + ', ECN: ' + str(tos%4))
	
	
	
	
	


if __name__ == "__main__":
	udppong()
	
