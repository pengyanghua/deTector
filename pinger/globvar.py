# this file defines and initializes global variables 
# that will be used across files

import time
import logging
import threading
from urllib2 import Request, urlopen, URLError




# create logger
def createLogger():
	logger = logging.getLogger('logger') 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('pinger.log') 
	fh.setLevel(logging.INFO) 

	ch = logging.StreamHandler() 
	ch.setLevel(logging.INFO) 
	
	formatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s') 
	fh.setFormatter(formatter) 
	ch.setFormatter(formatter) 
	 
	logger.addHandler(fh) 
	logger.addHandler(ch) 
	
	return logger
	
	
	

# fetch the configuration file from the controller
def get_config():
	logger.info('Fetching configuration file from the controller...')
	
	url = 'http://' + controller_ip + ':' + str(controller_port) + '/config.xml'	# hard coded
	req = Request(url)
	try:
		response = urlopen(req, timeout=5)
	except URLError as e:
		if hasattr(e, 'reason'):
			logger.error('We failed to reach the controller.')
			logger.error('Reason: ' + str(e.reason))
		elif hasattr(e, 'code'):
			logger.error('The controller couldn\'t fulfill the request.')
			logger.error('Error code: ' + str(e.code))
		return -1
	else:
		# everything is fine, write it to a file pinglist.txt
		config_file = response.read()
		try:
			fh = open("config.xml", 'w')
			fh.write(config_file)
			fh.close()
		except IOError:
			logger.error('write config.xml error')
			return -1
		logger.info('Fetch configuration file successfully.'	)
		return 0

		
		
		
def set_config():
	global pinger_listen_port, responder_listen_port, diagnoser_ip, diagnoser_listen_port, time_cyc, sys_choice
	fN = 'config.xml'
	fh = open(fN, 'r')
	line = fh.readline()
	while line:
		'''
		example:
		pinger_listen_port=7071
		responder_listen_port=7070
		diagnoser='100.1.0.1:9090'
		'''
		line = line.replace("\n", "")
		if '=' in line:
			items = line.split('=')
			if items[0] == 'pinger_listen_port':
				pinger_listen_port = int(items[1])
			elif items[0] == 'responder_listen_port':
				responder_listen_port = int(items[1])
			elif items[0] == 'diagnoser':
				addr = (items[1].replace("'", "")).split(':')
				diagnoser_ip = addr[0]
				diagnoser_listen_port = int(addr[1])
			elif items[0] == 'time_cyc':
				time_cyc = int(items[1])
			elif items[0] == 'sys_choice':
				sys_choice = int(items[1])
		line = fh.readline()
	fh.close()
	
	
	
	
		

		
	
def init(argv):
	global logger, controller_ip, controller_port, host_ip, pathlist_lock, version, pathlist, validTime, interval, tos, send_result_dir, recv_pkt
	
	logger = createLogger()
	logger.info('---------------start pinger----------------')
	
	host_ip = argv[1]
	controller_ip = argv[2]
	controller_port = int(argv[3])
	
	# pinger configuration
	while(get_config() != 0):	# retry
		time.sleep(3)
		
	set_config()
	
	# pinglist variables
	pathlist_lock = threading.Lock()
	version = -1
	pathlist = []
	tos = 0
	interval = 1
	validTime = ''
	send_result_dir = './send_result/'
	recv_pkt = 0
	
	
	
	
if __name__ == '__main__':
    init()