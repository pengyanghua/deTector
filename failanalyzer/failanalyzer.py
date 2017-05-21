import time
import threading
import sys

import pll
import globvar


'''
read logs received from diagnoser 
and run loss localization algorithm to pinpoint the failures
'''

def main():
	globvar.init()
	
	pll.loss_localization()

	
	
if __name__ == "__main__":
	main()