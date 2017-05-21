import os
import subprocess
import threading
import time
import sys
from datetime import datetime

import globvar
import upong


cpus = []
mems = []

def monitor(fN):
	global cpus, mems
	
	pid = os.getpid()
	cmd = ['ps', '-p', str(pid), '-o', 'pcpu=', '-o', 'rssize=']
	#0.0  12252
	output = subprocess.check_output(cmd)
	output = output.split('\n')[0].split(' ')
	cpu_usage = -1
	mem_usage = -1
	try:
		cpu_usage = float(output[1])
		mem_usage = int(output[2])/1024.0
	except:
		globvar.logger.error('Getting CPU and memory usage error - index out of range!')
		cpu_usage = float(output[0])
		mem_usage = int(output[1])/1024.0
	
	if cpu_usage >= 0 and mem_usage >= 0:
		cpus.append(cpu_usage)
		mems.append(mem_usage)
	
	# batch write
	if len(cpus) == 20:	# 60 seconds	
		fh = open(fN, 'a')
		for i in range(len(cpus)):
			fh.write(str(cpus[i]) + ' ' + str(mems[i]) + '\n')
		fh.close()
		cpus = []
		mems = []
		
		
	
def main(argv):
	globvar.init(argv)
	
	thrd_upong = threading.Thread(name='upong', target=upong.udppong)
	thrd_upong.setDaemon(True)	# the child thread will forcefully exit if parent exits
	thrd_upong.start()
	
	# collect memory and cpu usage info
	date_time = datetime.today()
	timestr = str(date_time.year) + '-' + str(date_time.month) + '-' + str(date_time.day) + '-' + str(date_time.hour) + ':' + str(date_time.minute) +  ':' + str(date_time.second)
	fN = './cpu_mem/responder_cpu_mem.' + timestr + '.log'
	while(True):
		#monitor(fN)
		time.sleep(3)
	


	
	
if __name__ == "__main__":
	if len(sys.argv) != 4:
                print "Please input host ip, controller ip and controller port!"
		print "Usage example: python responder.py 100.1.0.1 100.1.0.1 8080"
                sys.exit(1)
	main(sys.argv)
