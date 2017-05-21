# this file defines and initializes global variables 
# that will be used across files

import logging
import random


# create logger
def createLogger():
	logger = logging.getLogger('logger') 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('controller.log') 
	fh.setLevel(logging.INFO) 

	ch = logging.StreamHandler() 
	ch.setLevel(logging.INFO) 
	
	formatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s') 
	fh.setFormatter(formatter) 
	ch.setFormatter(formatter) 
	 
	logger.addHandler(fh) 
	logger.addHandler(ch) 
	
	return logger
	
	
	

def readConfig():
	global server_list, time_cyc, controller_listen_port, interval, sys_choice
	
	time_cyc = -1
	logger.info('Read configuration...')
	server_list = ['' for i in range(8)]
	fN = 'config.xml'
	fh = open(fN, 'r')
	line = fh.readline()
	while line:
		line = line.replace("\n", "")
		if '=' in line:
			keys = line.split('=')
			if '_' in keys[0]:
				items = keys[0].split('_')
				if items[0] == 'server':
					server_id = int(items[1]) - 1
					server_ip = keys[1].replace("'", "")
					server_list[server_id] = server_ip
			if keys[0] == 'time_cyc':
				time_cyc = int(keys[1])
			if keys[0] == 'interval':
				interval = float(keys[1])
			if keys[0] == 'controller':
				addr = (keys[1].replace("'", "")).split(':')
				controller_ip = addr[0]
				controller_listen_port = int(addr[1])
			if keys[0] == 'sys_choice':
				sys_choice = int(keys[1])
		line = fh.readline()
	fh.close()
	
	
	
	
	
def init():
	global logger, time_cyc, version
	
	logger = createLogger()
	logger.info('---------------start controller----------------')
	
	readConfig()
	
	# randomly generate a version number for pinglist file
	version = random.randint(0, 10000)
	
	
	
if __name__ == '__main__':
    init()