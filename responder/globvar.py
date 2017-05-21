# this file defines and initializes global variables 
# that will be used across files

import time
import logging
from urllib2 import Request, urlopen, URLError


# create logger
def createLogger():
	logger = logging.getLogger('logger') 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('responder.log') 
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
	global pinger_listen_port, responder_listen_port
	fN = 'config.xml'
	fh = open(fN, 'r')
	line = fh.readline()
	while line:
		'''
		pinger_listen_port=7071
		responder_listen_port=7070
		'''
		line = line.replace("\n", "")
		if '=' in line:
			items = line.split('=')
			if items[0] == 'pinger_listen_port':
				pinger_listen_port = int(items[1])
			elif items[0] == 'responder_listen_port':
				responder_listen_port = int(items[1])
		line = fh.readline()
	fh.close()
	



	
def init(argv):
	global logger, host_ip, controller_ip, controller_port
	
	logger = createLogger()
	logger.info('---------------start responder----------------')
	
	# hard coded here temporarly, if necessary, make it a configuration file or main() args
	host_ip = argv[1]
	controller_ip = argv[2]
	controller_port = int(argv[3])
	
	# responder configuration
	while(get_config() != 0):	# retry
		time.sleep(3)
	
	set_config()
	
	
	
	
if __name__ == '__main__':
    init()