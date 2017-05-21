# this file defines and initializes global variables 
# that will be used across files

import time
import logging


# create logger
def createLogger():
	logger = logging.getLogger('logger') 
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('failanalyzer.log') 
	fh.setLevel(logging.INFO) 

	ch = logging.StreamHandler() 
	ch.setLevel(logging.INFO) 
	
	formatter = logging.Formatter('%(asctime)s %(levelname)s:  %(message)s') 
	fh.setFormatter(formatter) 
	ch.setFormatter(formatter) 
	 
	logger.addHandler(fh) 
	logger.addHandler(ch) 
	
	return logger
	
	


		
def set_config():
	global server_list
	
	server_list = ['' for i in range(8)]	# 8 servers
	
	fN = '../controller/config.xml'	# for simplicity we put failanalyzer and controller together on the same server
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
		line = fh.readline()
	fh.close()
	


	
	
	
	
def init():
	global logger, paths_dir, result_dir, version
	
	logger = createLogger()
	logger.info('---------------start failanalyzer----------------')
	set_config()
	# file path
	paths_dir = '../controller/paths.txt'
	result_dir = '../diagnoser/recv_result/'
	version = 0
	
	
if __name__ == '__main__':
    init()