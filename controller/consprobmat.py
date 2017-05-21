'''
construct probe matrix for Fattree DCN
'''

import sys
import math
import time
import datetime
import re
import logging
from heapq import *
from itertools import combinations
import os 
import multiprocessing

import globvar



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
	global k, numPod, pathMatrix
	
	pathMatrix = []
	startTime = time.time()
	# logger.info('generating paths for ' + str(numPod) + ' pods...')
	
        for srcPod in range(0,numPod-1):
                for srcToR in range(k/2):
                        for dstPod in range(srcPod+1,numPod):
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
	global numPod, linkMatrix
	
	startTime = time.time()
	# logger.info('creating link matrix ...')
	
	# create link matrix
	linkMatrix =[[] for i in range(k*k*numPod/2)]
	for i in range(len(pathMatrix)):
		for j in range(4):
			if pathMatrix[i][j] > -1:
				linkMatrix[pathMatrix[i][j]].append(i)
	
	endTime = time.time()	
	logger.debug('createLinkMatrix running time: ' + str(endTime - startTime))
	
	logger.debug('the number of physical links: ' + str(len(linkMatrix)))
	logger.debug('the number of paths on each physical link: ' + str(len(linkMatrix[0])))
	for i in range(len(linkMatrix)):
		logger.debug(str(i) + ':' + 'length' + str(len(linkMatrix[i])) + ':' + str(linkMatrix[i]))
	

	
	
# routing matrix decomposition
def splitGraph():
	global linkMatrix, pathMatrix, linksubgraphs
	
	startTime = time.time()
	# logger.info('splitting graph ...')
	
	pathsubgraphs = []
	linksubgraphs = []
	v = [0 for i in range(len(pathMatrix))]
	
	while(True):
		pathID = -1
		for i in range(len(v)):
			if v[i] == 0:
				pathID = i
				break
		if pathID == -1:
			logger.debug('finish spliting graph')
			break
			
		pathset = set([pathID])
		newpathset = set([pathID])
		linkset = set()
		while len(newpathset) > 0:
			tempnewpathset = set()
			for path in newpathset:
				for link in pathMatrix[path]:
					if link not in linkset:
						linkset.add(link)
						for pathID in linkMatrix[link]:
							if pathID not in pathset:
								tempnewpathset.add(pathID)
							
			newpathset = tempnewpathset
			pathset = pathset.union(newpathset)
		
		for path in pathset:
			v[path] = 1
		pathsubgraphs.append(sorted(list(pathset)))
		linksubgraphs.append(sorted(list(linkset)))

	
	#print 'subgraphs: ', subgraphs
	logger.debug('split into ' + str(len(pathsubgraphs)) + ' subgraphs totally')
	endTime = time.time()
	logger.debug('splitGraph running time: ' + str(endTime - startTime))
	
	return (pathsubgraphs, linksubgraphs)

	
	
	

# create virtual path matrix and link matrix to achieve k-identifiability
def createVirtMatrix():
	global pathMatrix, linkMatrix, linksubgraphs
	
	if ki == 1:
		return
	
	startTime = time.time()
	# logger.info('creating virtual link and path matrix ...')
	
	for index in range(len(linksubgraphs)):
		linksubgraph = linksubgraphs[index]
		numOfLinks = len(linkMatrix)
	
		combList = []
		for i in range(2, ki+1):
			combList.append(list(combinations(linksubgraph, i)))
		
		# print 'legnth of linksubgraph:', len(linksubgraph)
		virtLinkNum = 0
		for i in range(len(combList)):
			for j in range(len(combList[i])):
				linkID = numOfLinks + virtLinkNum
				virtLinkNum = virtLinkNum + 1
				pathSet = set()
				for link in combList[i][j]:
					for path in linkMatrix[link]:
						pathSet.add(path)
				pathList = sorted(list(pathSet))
			
				# update linkMatrix
				linkMatrix.append(pathList)
			
				# update pathMatrix
				for path in pathList:
					pathMatrix[path].append(linkID)
				linksubgraphs[index].append(linkID)
			
	endTime = time.time()
	logger.debug('the number of virtual links: ' + str(virtLinkNum*len(linksubgraphs)))	
	logger.debug('createVirtMatrix running time: ' + str(endTime - startTime))
	logger.debug('the number of phys-virt links on each path: ' + str(len(pathMatrix[0])))


	
	
	

# only consider paths in numPod pods
def computePaths(pathsubgraph, linksubgraph, alpha, id):
	
	startTime = time.time()
	# logger.info('selecting paths ...')
	
	#print 'len(pathsubgraph): ', len(pathsubgraph)
	#print 
	#print 'len(linksubgraph): ', len(linksubgraph)
	# visited[i]: how many times the link has been covered by different paths
	visited = {}
	for link in linksubgraph:
		visited[link] = 0
		
	Ulinks = set(linksubgraph)
	Upaths = set(pathsubgraph)
	# selected paths, save the pathIDs
	Spaths = []

	# create heap to maintain each path's score, min element is the root node
	# do not use priority queue because its performance is much lower than heap
	hp = []
	heapify(hp)

	# initialization
	for path in pathsubgraph:
		score = -1 #-len(pathMatrix[0])
		version = 0
		heappush(hp, (score, path, version))	
	
	# setLinkList: set: link1, link2, link3 ...
	# linkSetList: link:set; link:set; link:set ...
	setLinkList = [set() for i in range(len(linksubgraph))]
		
	linkSetList = {}
	for link in linksubgraph:
		linkSetList[link] = 0	
		
	setLinkList[0] = set(linksubgraph)
	globSetID = 0
	pathCounter = len(pathsubgraph)
	linkCounter = len(linksubgraph)
	
	if ki > 0:
		while globSetID != len(linksubgraph)-1 and pathCounter > 0:
			# print 'globSetID: ', globSetID
			# print 'pathCounter: ', pathCounter
			# print 'setLinkList: ', setLinkList
			pathID = -1
			lset = set()
			covset = set()
			(score, pathID, version) = heappop(hp)
			while hp:
				lset = set(pathMatrix[pathID])	# a set of all links on the paths
				covset = set(linkSetList[link] for link in pathMatrix[pathID])	# a set of sets of these links
				
				Rset = set()
				for setID in covset:
					if set(setLinkList[setID]).issubset(lset):
						Rset.add(setID)

				covset = covset.difference(Rset)
					
				if version == len(Spaths):
					break
				else:
					newscore = -len(covset)
					coverage = 0
					for link in pathMatrix[pathID]:
						coverage = coverage + visited[link]
					newscore = newscore + coef*coverage
					(score, pathID, version) = heappushpop(hp, (newscore, pathID, len(Spaths)))
			
			# print 'selected pathID: ', pathID
			if pathID == -1:
				logger.debug('pathID == -1, exit.')
				break
			if len(covset) == 0:
				logger.debug('covset is empty!')
				break
			
			Spaths.append(pathID)
			Upaths.remove(pathID)
			pathCounter = pathCounter - 1
		
			for link in pathMatrix[pathID]:
				visited[link] = visited[link] + 1
				if visited[link] >= alpha and (link in Ulinks):
					Ulinks.remove(link)
					linkCounter = linkCounter - 1
			
			# now each set in covset can be divided into two subsets
			for setID in covset:
				newID = globSetID + 1
				for link in lset:
					if linkSetList[link] == setID:
						# remove from original set and add it to another
						setLinkList[setID].remove(link)					
						setLinkList[newID].add(link)
						linkSetList[link] = newID
				globSetID = globSetID + 1		
		# end while
	
	
	
	
	#--------------------------------------------------------------------------------#
	logger.debug('selecting paths for ' + str(alpha) + '-coverage...')
	
	hp = []
	heapify(hp)
	
	# initialization
	for path in Upaths:
		score = 0
		for link in pathMatrix[path]:
			score = score + visited[link]
		version = 0
		heappush(hp, (score, path, version))
		
	while linkCounter > 0 and pathCounter > 0:
		pathID = -1
		while hp:
        		(score, pathID, version) = heappop(hp)
			if version == len(Spaths):
            			break
            		else:
            			score = 0
				for link in pathMatrix[pathID]:
					score = score + visited[link]
				heappush(hp, (score, pathID, len(Spaths)))
		
		if pathID == -1:
			logger.debug('pathID == -1, exit.')
			break
			
		Spaths.append(pathID)
		Upaths.remove(pathID)
		pathCounter = pathCounter - 1

		# save the paths which need to update score
		for link in pathMatrix[pathID]:
			# no matter the link is removed or not, we should update its weight
			visited[link] = visited[link] + 1

			# check whether to remove the link
			if visited[link] >= alpha and (link in Ulinks):
				Ulinks.remove(link)
				linkCounter = linkCounter - 1
	# end while
	

	endTime = time.time()
	run_time = endTime - startTime
	logger.debug('selectPath running time: ' + str(endTime - startTime))
	logger.debug('the number of selected paths in subgraph:' + str(len(Spaths)))
	
	fN = 'subgraph.spaths.' + str(id) + '.txt'
	fh = open(fN, 'w')
	for path in Spaths:
		fh.write(str(path)+'\n')
	fh.close()
	


	
		
	
# aggregate all selected path	
def aggrPaths(N):
	
	#logger.info('aggregate all selected paths...')
	globSpaths = set()
	for i in range(N):
		fN = 'subgraph.spaths.' + str(i) + '.txt'
		fh = open(fN, 'r')
		line = fh.readline()
		while line:
			path = int(line.split('\n')[0])
			globSpaths.add(path)
			line = fh.readline()
		fh.close()
		os.remove(fN)
	globSpaths = sorted(list(globSpaths))
	
	logger.debug('total number of selected paths in graphs: ' + str(len(globSpaths)))
	logger.info('total number of selected paths in whole DCN:' + str(k/numPod*len(globSpaths)))
	
	# write globSpaths to file
	fN = 'paths.txt'
	fh = open(fN, 'w')
	for path in globSpaths:
		fh.write(str(path)+'\n')
	fh.close()
	
	return globSpaths
	


	
	
# generate pinglists for all pingers	
def genPinglist(globSpaths):
	
	logger.info('generating deTector pinglist...')
	
	server_list = globvar.server_list
	# coreswitch_list = globvar.coreswitch_list
	# compute the paths on each server
	numOfServers = 8
	serverpaths = [[] for i in range(numOfServers)]
	for path in globSpaths:
		firstLinkID = pathMatrix[path][0]
		if firstLinkID < numOfServers*2:
			serverpaths[firstLinkID/2].append(path)
	
	'''
	define pinglist:
	<pinglist>
	pinger='A' 
	version='0'
	validFrom='timestamp'
	interval='1'
	tos='ALL'
	paths='the number of paths'
	path_1: dest_ip='B' coreswitch_ip='C'
	path_2: ...
	</pinglist>
	'''
	
	# generate pinglist for each server
	for server_id in range(numOfServers):
		ip = server_list[server_id]
		if len(ip) > 0:	# server exists
			fN = './pinglists/pinglist-' + ip + '.xml'
			fh = open(fN, 'w')
			fh.write('<pinglist>' + '\n')
			
			string = 'pinger=' + "'" + ip + "'"
			fh.write(string + '\n')
			
			string = 'version=' + "'" + str(globvar.version) + "'"
			fh.write(string + '\n')
			
			ts = time.time()
			timestamp = datetime.datetime.fromtimestamp(ts)
			timedelta = datetime.timedelta(minutes=1)       # valid after 1 min
			string = "validFrom='" + str((timestamp + timedelta).strftime('%Y-%m-%d %H:%M:%S')) + "'"
			fh.write(string + '\n')
			
			string = "interval=" + "'" + str(globvar.interval) + "'"
			fh.write(string + '\n')
			
			string = "tos='ALL'"
			fh.write(string + '\n')
			
			string = "paths=" + "'" + str(len(serverpaths[server_id])) + "'"
			fh.write(string + '\n')
			for i in range(len(serverpaths[server_id])):
				path = serverpaths[server_id][i]
				links = pathMatrix[path]
				dest_id = links[3]/2
				dest_ip = "'" + server_list[dest_id] + "'"
				
				coreswitch_id = "'" + str((links[1]-16)%4) + "'"	# core switch id in a 4-ary Fattree
				# coreswitch_ip = "'" + coreswitch_list[coreswitch_id] + "'"
				
				string = "path_" + str(path) + ": dest_ip=" + dest_ip + " coreswitch_id=" + coreswitch_id
				fh.write(string + '\n')
				
			fh.write('</pinglist>' + '\n')
	
	fh.close()
	globvar.version = globvar.version + 1


	


	
# construct probe matrix	
def consprobmat(para_k, para_numPod, para_ki, para_alpha, para_coef, para_cores):
        global logger, k, numPod, ki, coef
	
	logger = globvar.logger
	
        startTime = time.time()

        k = para_k
        if k < 1 or k % 2 == 1:
                raise ValueError('k must be a positive even integer')
	numPod = para_numPod
	ki = para_ki
	alpha = para_alpha
	coef = para_coef
	numOfCores = para_cores
	logger.info('Fattree DCN: ' + 'k = ' + str(k) + ', numPod = ' + str(numPod) + ', identifiability = ' + str(ki) + ', coverage = ' + str(alpha) + ', coef = ' + str(coef) + ', cores = ' + str(numOfCores))
	
	genPodPath()
	createLinkMatrix()
	(pathsubgraphs, linksubgraphs) = splitGraph()
	createVirtMatrix()
	
	pool = multiprocessing.Pool(processes = numOfCores)
	for graphID in range(len(pathsubgraphs)):
        	pool.apply_async(computePaths, (pathsubgraphs[graphID], linksubgraphs[graphID], alpha, graphID, ) )
	pool.close()
        pool.join()	
	
	globSpaths = aggrPaths(len(pathsubgraphs))
	genPinglist(globSpaths)
	
        endTime = time.time()
        logger.debug('total running time for constructing probe matrix: ' + str(endTime - startTime))





if __name__ == '__main__':
        if len(sys.argv) != 7:
                print "Please input k, numPod, beta, alpha, coef and cores!"
                sys.exit(1)
        consprobmat(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
