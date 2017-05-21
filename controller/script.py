import subprocess
import threading
import time







def readConfig():
	global serlist, controller_ip, controller_listen_port, diagnoser_ip, diagnoser_listen_port
	
	print 'Read configuration...'
	serlist = ['' for i in range(8)]	# 8 servers
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
					serlist[server_id] = server_ip
			if keys[0] == 'controller':
				addr = (keys[1].replace("'", "")).split(':')
				controller_ip = addr[0]
				controller_listen_port = int(addr[1])
			if keys[0] == 'diagnoser':
				addr = (keys[1].replace("'", "")).split(':')
				diagnoser_ip = addr[0]
				diagnoser_listen_port = int(addr[1])				
		line = fh.readline()
	fh.close()
	


	
def main():
	readConfig()
	
	# copy source code to each server
	print 'copy source code...'
	for server in serlist:
		cmd = 'timeout 3s scp -r /home/net/pyh_code/system net@' + server + ':/home/net/pyh_code/'
		prog = subprocess.Popen([cmd], stderr=subprocess.PIPE, shell=True)
		print  server, ': ', prog.communicate()[1]
	
	# start controller
	print 'start controller...'
	cmd = 'sudo python main.py'
	prog = subprocess.Popen([cmd], stderr=subprocess.PIPE, cwd = '/home/net/pyh_code/system/controller/', shell=True)
	
	# start diagnoser
	print 'start diagnoser...'
	cmd = 'sudo python main.py ' + controller_ip + ' ' + str(controller_listen_port)
	prog = subprocess.Popen([cmd], stderr=subprocess.PIPE, cwd = '/home/net/pyh_code/system/diagnoser/', shell=True)
	
	# start responder
	print 'start responder...'
	for server in serlist:
		cmd = 'sudo python main.py ' + server + ' ' + controller_ip + ' ' + str(controller_listen_port)
		ssh_cmd = 'net@' + server
		dir_cmd = 'cd /home/net/pyh_code/system/responder/;'
		prog = subprocess.Popen(['ssh', ssh_cmd, dir_cmd, cmd], stderr=subprocess.PIPE)
		
	# start pinger
	print 'start pinger...'
	for server in serlist:
		cmd = 'sudo python main.py ' + server + ' ' + controller_ip + ' ' + str(controller_listen_port)
		ssh_cmd = 'net@' + server
		dir_cmd = 'cd /home/net/pyh_code/system/pinger/;'
		prog = subprocess.Popen(['ssh', ssh_cmd, dir_cmd, cmd], stderr=subprocess.PIPE)
		
	print 'deTector is running...'
	while True:
		try:
			time.sleep(3)
		except:
			print 'shutdown deTector...'
			cmd = 'sudo pkill python'
			subprocess.Popen([cmd], stderr=subprocess.PIPE, shell=True)
			for server in serlist:
				ssh_cmd = 'net@' + server
				prog = subprocess.Popen(['ssh', ssh_cmd, cmd], stderr=subprocess.PIPE)
			print 'exit'

	

if __name__ == "__main__":
	print 'WARN: you need to modify the code to run it successfully (e.g., the path)'
	main()
	
