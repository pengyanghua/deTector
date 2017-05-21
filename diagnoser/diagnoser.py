import time
import threading
import sys

import globvar
import recvres





	
	
	
def main(argv):
	globvar.init(argv)
	
	logger = globvar.logger
	result_dir = globvar.result_dir
	# receive result => preprocessing result => fault localization
	thd_recv_result = threading.Thread(name='recv_result', target= recvres.recv_result, args=(result_dir, ))
	thd_recv_result.setDaemon(True)
	thd_recv_result.start()
	
	while(True):
		time.sleep(10)

	
	
if __name__ == "__main__":
	if len(sys.argv) != 3:
                print "Please input controller ip and controller port!"
		print "Usage Example: python diagnoser.py 100.1.0.1 8180"
                sys.exit(1)
	main(sys.argv)