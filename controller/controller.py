import subprocess
import threading
import time
import sys

import globvar
import consprobmat




# run http server
def http():
	logger.info('Starting http server...')
	cmd = 'python -m SimpleHTTPServer ' + str(globvar.controller_listen_port)
	subprocess.call(cmd, shell= True, cwd='./')



	
	
# compute probe path periodically if topology changes and generate pinglist for each server
def gen_lists():
	k = 4		# 4-ary Fattree
	numPod = 4	# compute paths for all 4 pods
	ide = 1		# identifiability, at most 1 for 4-ary Fattree
	cov = 3		# coverage
	coef = 1	# coefficient for score computation
	cores = 1	# parallel computation
	choice = globvar.sys_choice
	
	while(True):
		# compute probe matrix
		logger.info('compute probe matrix...')
		if choice == 1:		# deTector
			consprobmat.consprobmat(k, numPod, ide, cov, coef, cores)
		time.sleep(globvar.time_cyc)
		
		
		
	
	
	


def main():
	global logger
	
	globvar.init()
	logger = globvar.logger
	
	# create two threads, one for sending pkts and another for receiving pkts
	thrd_path = threading.Thread(name='path', target=gen_lists)
	thrd_path.setDaemon(True)
	thrd_path.start()
	
	time.sleep(1)
	
	thrd_http = threading.Thread(name='http', target=http)
	thrd_http.setDaemon(True)	# the child thread will forcefully exit if parent exits
	thrd_http.start()
	
	while(True):
		time.sleep(3)
		
	


	

if __name__ == "__main__":
        main()
	
