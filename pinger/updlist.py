from urllib2 import Request, urlopen, URLError
from time import sleep
import random

import globvar





# fetch the pinglist file from the controller
# return 0 if successful
def get_pinglist(url):
	logger.info('Fetching pinglist file from the controller...')
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
		pinglist_file = response.read()
		try:
			fd = open('pinglist-' + globvar.host_ip + '.xml', 'w')
			fd.write(pinglist_file)
			fd.close()
		except IOError:
			logger.error('write pinglist error')
			return -1
		logger.info('Fetch pinglist file successfully.'	)
		return 0

		
	


def get_testpair(url):
	logger.info('Fetching testpair file from the controller...')
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
		pinglist_file = response.read()
		try:
			fd = open('testpair-' + globvar.host_ip + '.xml', 'w')
			fd.write(pinglist_file)
			fd.close()
		except IOError:
			logger.error('write pinglist error')
			return -1
		logger.info('Fetch pinglist file successfully.'	)
		return 0

		

		
		
		
		
	

# read and analyze pinglist
def analyze_pinglist():
	# analyze the pinglist file
	
	pathlist = []
	fN = 'pinglist-' + globvar.host_ip + '.xml'
	fh = open(fN, 'r')
	line = fh.readline()
	while line:
		line = line.replace("\n", "")
		if '=' in line:
			items = line.split('=')
			if items[0] == 'pinger':
				pinger_ip = items[1].replace("'", "")
				if pinger_ip != globvar.host_ip:
					logger.error("pinger_ip does not match host_ip!")
					break
					
			elif items[0] == 'version':
				next_version = int(items[1].replace("'", ""))
				if next_version <= globvar.version:
					logger.error("Fetched pinglist file is out of date!")
					break
				else:
					globvar.version = next_version
					
			elif items[0] == 'validFrom':	#'2016-09-25 14:45:32'
				globvar.validTime = items[1].replace("'", "")
				
			elif items[0] == 'interval':
				globvar.interval = float((items[1].replace("'", "")))
				
			elif items[0] == 'tos':		
				globvar.tos = (items[1].replace("'", ""))	
				
			elif items[0] == 'paths':
				pathNum = int(items[1].replace("'", ""))
				# read all paths
				for i in range(pathNum):
					line = fh.readline().replace("\n", "")
					elements = line.split(" ")
					
					pathID = elements[0].split(':')[0].split('_')[1]
					
					dest_ip_str = elements[1]
					dest_ip_items = dest_ip_str.split("=")
					dest_ip = dest_ip_items[1].replace("'", "")
					
					coreswitch_str = elements[2]
					coreswitch_str_items = coreswitch_str.split("=")
					coreswitch_id = coreswitch_str_items[1].replace("'", "")
					
					pathlist.append((pathID, dest_ip, coreswitch_id))
							
		line = fh.readline()
	fh.close()
	
	# randomly scatter path
	count = len(pathlist)
	while count > 0:
		count = count - 1
		id1 = random.randint(0,len(pathlist)-1)
		id2 = random.randint(0,len(pathlist)-1)
		
		# swap
		# in fattree, we use core switch to define an end-to-end path
		(pathID1, dest_ip1, coreswitch_id1) = pathlist[id1]
		(pathID2, dest_ip2, coreswitch_id2) = pathlist[id2]
		pathlist[id1] = (pathID2, dest_ip2, coreswitch_id2)
		pathlist[id2] = (pathID1, dest_ip1, coreswitch_id1)

	
	with globvar.pathlist_lock:
		globvar.pathlist = pathlist

	return 

	
	
# periodically fetch pinglist file and update pinglist
def update_pinglist():
	global logger
	
	logger = globvar.logger
	time_cyc = globvar.time_cyc
	ping_url = 'http://' + globvar.controller_ip + ':' + str(globvar.controller_port) + '/pinglists/pinglist-' + globvar.host_ip + '.xml'
	while(True):
		
		while(get_pinglist(ping_url) != 0):	# retry
			sleep(3)
		# if successfully fetch pinglist file, analyze it
		analyze_pinglist()	
		sleep(time_cyc)
					
	logger.info('[Update pinglist completed.]')



	
if __name__ == "__main__":
	update_pinglist()



