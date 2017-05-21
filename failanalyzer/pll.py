'''
run PLL algorithm to locate bad links
'''

import sys
import math
import time
import random
from heapq import *
import os
import threading
import copy
from datetime import datetime

import globvar
import sdn_failure_simu as failAPI



# switch1 = [i, j]
# switch1 is in lower layer
# if switch2 is in core layer, the pod id is k.
def getLinkID(tier, switch1, switch2):
	global numPod
	
        if tier == 0:
                # print 'link betwen aggregation and core layer'
                podID = switch1[0]
                orderInCore = podID*(k*k/4) + switch2[1]
                return int(k*k*numPod/4 + orderInCore)
        else:
                # print 'link between edge and aggregation layer'
                if switch1[0] == switch2[0]:
                        podID = switch1[0]
                        orderInPod = switch1[1]*(k/2) + switch2[1]
                        return int((k*k/4)*podID + orderInPod)
                else:
                        logger.error('error: not in the same pod')


	
			
# read inter-pod paths
def genPodPath():
	global pathMatrix, k, numPod
	
	startTime = time.time()
	logger.info('generating paths for ' + str(numPod) + ' pods...')
	
	pathMatrix = []
        for srcPod in range(0, numPod-1):
                for srcToR in range(k/2):
                        for dstPod in range(srcPod+1, numPod):
                                for dstToR in range(k/2):
                                        # compute paths between (srcPod, srcToR) and (dstPod, dstToR)
                                        for i in range(k*k/4):
                                                path = [0 for n in range(4)]
                                                path[0] = getLinkID(1, [srcPod, srcToR],[srcPod, math.floor(i/(k/2))])
                                                path[1] = getLinkID(0, [srcPod, math.floor(i/(k/2))],[k, i])
                                                path[2] = getLinkID(0, [dstPod, math.floor(i/(k/2))],[k, i])
                                                path[3] = getLinkID(1, [dstPod, dstToR],[dstPod, math.floor(i/(k/2))])

                                                pathMatrix.append(path)
	
	endTime = time.time()		
	logger.debug('genPodPath running time: ' + str(endTime - startTime))
	logger.debug('the number of paths: ' + str(len(pathMatrix)))
	
	

	
	

# create link matrix
def createLinkMatrix():
	global pathMatrix, linkMatrix, numPod
	
	startTime = time.time()
	logger.info('creating link matrix ...')
	
	# create link matrix
	linkMatrix =[[] for i in range(k*k*numPod/2)]
	for i in range(len(pathMatrix)):
		for j in range(4):
			if pathMatrix[i][j] > -1:
				linkMatrix[pathMatrix[i][j]].append(i)
	
	endTime = time.time()
	logger.debug('createLinkMatrix running time: ' + str(endTime - startTime))

	logger.debug('the number of links: ' + str(len(linkMatrix)))
	logger.debug('the number of paths on each link: ' + str(len(linkMatrix[0])))


	


	
# read selected paths from file
def readSpaths():
	global Spaths, selectedLinkMatrix, k, ki
	Spaths = []
	
	logger.info('reading Spaths...')
	
	fN = globvar.paths_dir
	try:
		fh = open(fN, 'r')
	except:
		logger.error('can not find the paths file!')
		return -1
		
	line = fh.readline()
	while line:
		path = int(line.split('\n')[0])
		Spaths.append(path)
		line = fh.readline()
	fh.close()
	
	# create selected link matrix
	selectedLinkMatrix =[[] for i in range(len(linkMatrix))]
	for path in Spaths:
		for j in range(4):
			link = pathMatrix[path][j]
			selectedLinkMatrix[link].append(path)
	
	return 0



	
	
# read packet loss measurements
def readLoss(flag):
	global sys_choice
	
	if flag == 1:
		logger.info('Read ping result...')
	
	'''
	for example:
	<result>
	sys_choice:1
	path-0:(8, 8)
	path-2:(8, 8)
	path-5:(7, 0)
	path-7:(7, 0)
	</result>
	'''
	# measures[path] = # of packet loss
	measures = {}
	
	# get all files under result_dir
	filelist = os.listdir(globvar.result_dir)
	
	if flag == 1:
		for file in filelist:	
			# read ping result file
			
			if "test" in file:
				continue
			fN = globvar.result_dir + file
			try:
				fh = open(fN, 'r')
			except:
				logger.error('can not find '+fN)
				return measures
			
			line = fh.readline().replace("\n", "")
			while line:
				if ':' in line:
					items = line.split(':')
					if items[0] == 'sys_choice':
						sys_choice = int(items[1])
					else:
						pathID = int(items[0].split('-')[1])
						
						tuple = items[1].split('(')[1].split(')')[0].split(',')
						sent = int(tuple[0])
						recv = int(tuple[1].split(' ')[1])
						loss = sent - recv
						if loss > 0:	# allow 1 pkt loss
							measures[pathID] = loss
				line = fh.readline()
			fh.close()
			os.remove(fN)
		
		if len(measures) == 0:
			logger.info('empty measures!')
		return measures



def PLL(measures):
	global selectedLinkMatrix, pathMatrix
	
	startTime = time.time()
	logger.info('PLL localizing packet loss ...')
	
	# construct suspicious links
	suspLinks = set()
	for path in measures.keys():
		for link in pathMatrix[path]:
			suspLinks.add(link)
	
	fullpktlosslink = set()		
	for link in suspLinks:
		isfull = True
		for path in selectedLinkMatrix[link]:
			if path not in measures.keys():
				isfull = False
				break
		if isfull == True:
			fullpktlosslink.add(link)

	partialpktlosslink =  suspLinks.difference(fullpktlosslink)
	
	fullmeasures = {}
	for link in fullpktlosslink:
		for path in selectedLinkMatrix[link]:
			fullmeasures[path] = measures[path]
	for path in fullmeasures.keys():
		del measures[path]
			
	partialmeasures = measures
			
	candLinks = set(scoresym(fullmeasures, fullpktlosslink))
	candLinks = candLinks.union(set(scoresym(partialmeasures, partialpktlosslink)))
	
	logger.info('candLinks: ' + str(candLinks))
	
	return candLinks
	
	

	

def scoresym(measures, suspLinks):
	global selectedLinkMatrix, pathMatrix
	
	startTime = time.time()
	logger.debug('score localizing packet loss ...')
		
	badPaths = set(measures.keys())
	
	candLinks = []
	
	hitRThrshd = 0.8
	
	while len(measures) != 0 and len(suspLinks) != 0:
		# compute a score for all remaining links
		maxScore = 0
		linkID = -1
		for link in suspLinks:
			score = 0
			for path in measures.keys():
				if link in pathMatrix[path]:
					score = score + measures[path]
			
			if maxScore < score:
				count = 0
				# compute hit ratio here
				for path in selectedLinkMatrix[link]:
					if path in badPaths:
						count = count + 1
				hitR = count*1.0/len(selectedLinkMatrix[link])
				
				if hitR > hitRThrshd:
					maxScore = score
					linkID = link
				
		# add linkID to candLinks and del all related paths
		if linkID == -1:
			if hitRThrshd >= 0.8:
				hitRThrshd = hitRThrshd - 0.2
				continue
			else:
				break

		suspLinks.remove(linkID)
		candLinks.append(linkID)
		
		for path in measures.keys():
			if linkID in pathMatrix[path]:
				del(measures[path])
	
	endTime = time.time()	
	# logger.info('score finished in ' + str(endTime - startTime) + ' seconds.')
	
	# possible failed links
	logger.debug('candLinks:' + str(candLinks))	
	
	return candLinks
	

	
	
	
	
	
	
def loss_localization():
        global logger, k, numPod, tot_round, tot_accur
	
	logger = globvar.logger
	
        startTime = time.time()
	
        k = 4
        if k < 1 or k % 2 == 1:
                raise ValueError('k must be a positive even integer')
	numPod = 4
	F = 1
	
	genPodPath()
	createLinkMatrix()
	
	if readSpaths() == -1:
		return -1
	
	date_time = datetime.today()
	timestr = str(date_time.year) + '-' + str(date_time.month) + '-' + str(date_time.day) + '-' + str(date_time.hour) + ':' + str(date_time.minute) +  ':' + str(date_time.second)
	fN = './locfail/locfail_log.' + timestr + '.txt'
	fh = open(fN, 'w')
	fh.close()
	
	failurelist = []
	
	tot_round = 0
	tot_accur = 0
	tot_cov = 0
	tot_fp = 0
	tot_fn = 0
	tot_tp = 0
	tot_badlinks = 0
	tot_candlinks = 0
			
	first = True
	
	while(True):
		time.sleep(60)
		measures = readLoss(1)	# read pkt loss result
		if len(measures) == 0:
			logger.info("measures are empty")
			continue
		logger.info('measures: ', measures)	
		
		measurescopy = copy.deepcopy(measures)
		candLinks = PLL(measures)
				
		# update statistics
		tot_round = tot_round + 1
			
		# log in into file
		fh = open(fN, 'a')
		fh.write('*********A NEW ROUND**********\n')
		date_time = datetime.today()
		timestr = str(date_time.year) + '-' + str(date_time.month) + '-' + str(date_time.day) + '-' + str(date_time.hour) + ':' + str(date_time.minute) +  ':' + str(date_time.second)
		fh.write('time:'+timestr+'\n')
		fh.write('measures:'+str(measurescopy)+'\n')
		fh.write('failures:'+str(failurelist)+'\n')
		fh.write('candLinks:'+str(candLinks)+'\n')	
		fh.write('\n')
		fh.close()	
				
	endTime = time.time()
	logger.info('total running time: ' + str(endTime - startTime))

	return 0



	
	
	 
	
	
if __name__ == '__main__':
        if len(sys.argv) != 2:
                print "Please input k, numPod!"
                sys.exit(1)
        main(sys.argv[1], sys.argv[2])
