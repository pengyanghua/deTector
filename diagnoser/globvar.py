# this file defines and initializes global variables 
# that will be used across files

import time
import logging
from urllib2 import Request, urlopen, URLError


# create logger
def createLogger():
	logger = logging.getLogger('logger') 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('diagnoser.log') 
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
	except:
		logger.error('Socket timeout.')
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
	global diagnoser_ip, diagnoser_listen_port, server_list
	
	server_list = ['' for i in range(8)]	# 8 servers
	
	fN = 'config.xml'
	fh = open(fN, 'r')
	line = fh.readline()
	while line:
		line = line.replace("\n", "")
		if '=' in line:
			keys = line.split('=')
			if keys[0] == 'diagnoser':
				addr = (keys[1].replace("'", "")).split(':')
				diagnoser_ip = addr[0]
				diagnoser_listen_port = int(addr[1])
			if '_' in keys[0]:
				items = keys[0].split('_')
				if items[0] == 'server':
					server_id = int(items[1]) - 1
					server_ip = keys[1].replace("'", "")
					server_list[server_id] = server_ip
		line = fh.readline()
	fh.close()
	
	
	

	
	
def init(argv):
	global logger, controller_ip, controller_port, result_dir
	
	logger = createLogger()
	logger.info('---------------start diagnoser----------------')
	
	# hard coded here temporarly, if necessary, make it a configuration file or main() args
	controller_ip = argv[1]		#
	controller_port = int(argv[2])	# 8180
	
	# diagnoser configuration
	while(get_config() != 0):	# retry
		time.sleep(3)
	set_config()
	
	
	# file path
	result_dir = './recv_result/'
	
	
	
if __name__ == '__main__':
    init()