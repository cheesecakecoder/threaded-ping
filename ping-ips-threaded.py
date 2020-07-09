import sys
import os
import hashlib
import time
import threading
from pythonping import ping
import subprocess
import re

counter = 0
printLock = threading.Lock()
readFileLock = threading.Lock()
writeFileLock = threading.Lock()

class myThread (threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		global counter
		global f
		

		printLock.acquire()
		print("Starting Thread {}".format(self.threadID))
		printLock.release()

		lIP = "127.0.0.1"
		lCounter = 0
		while len(lIP) > 0:
			readFileLock.acquire()
			lIP = f.readline()
			counter += 1
			lCounter = counter
			readFileLock.release()

			if len(lIP) > 0:
				lIP = lIP.replace("\r", "")
				lIP = lIP.replace("\n", "")
				args=['/bin/ping', '-c', '1', '-W', '1', str(lIP)]
				printLock.acquire()
				print("[Goog Thread {}] {} -- {}".format(self.threadID, lCounter, lIP))
				printLock.release()

				#result = ping_ip(lIP)
				result = 0
				p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
				p_ping_out = str(p_ping.communicate()[0])
				if (p_ping.wait() == 0):
					search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms', p_ping_out, re.M|re.I)
					ping_rtt = search.group(2)
					printLock.acquire()
					print("[Thread {}] {} -- result:{}".format(self.threadID, lIP, ping_rtt))
					printLock.release()


				#if result == 1:
					writeFileLock.acquire()
					fout = open("live-ips.txt", "a")
					fout.write("%s\r\n" % (str(lIP)))
					fout.flush()
					fout.close()
					writeFileLock.release()
					printLock.acquire()
					print("[Thread {}] {} -- {} LIVE IP!".format(self.threadID, lCounter, lIP))
					printLock.release()

				
		
		printLock.acquire()
		print("Exiting Thread {}".format(self.threadID))
		printLock.release()
		return

def ping_ip(ip_address):
	global writeFileLock
	ping_result = ping(ip_address, count=1, verbose=False)

	print("---{}---".format(str(ping_result.success)))

	if "Request timed out" in str(ping_result.success):
		return 0
	elif " bytes in " in str(ping_result.success):
		return 1

	writeFileLock.acquire()
	fout = open("error-ips.txt", "a")
	fout.write("%s : %s\r\n" % (str(ip_address), str(ping_result.success)))
	fout.flush()
	fout.close()
	writeFileLock.release()
	return 2



num_threads = 185
f = open("google-ips_02-28-2020.txt", "r")
if f.mode != "r":
	print("Error could not open file.")
else:
	i = 1
	while i <= num_threads:
		thread = myThread(i)
		thread.start()
		i += 1
