from optparse import OptionParser
import socket
import os
import re
import math
import multiprocessing as mp
import queue
import sys

def writeoutput(output_path,line):
	if output_path:
		with open(output_path,"a") as f:
			f.write(line)
			if line[-1]!='\n':
				f.write('\n')

def split_addr_port(str):
	ip=''
	port=1080
	ip_regex=re.compile(r'(\d+(?:\.\d+){3})')
	port_regex=re.compile(r'(\d+(?:\.\d+){3}):(\d+)')
	
	m=ip_regex.search(str)
	if m:
		ip=m[0]
	else:
		raise Exception("Bad IP Format for",str) 
	m=port_regex.search(str)
	if m and m.lastindex==2:
		port=int(m[2])
	return(ip,port)

def test_socks5_server(ip_addr,port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ret = False
	try:
		s.connect((ip_addr,port))
		#\x05: VERSION \x01: NB AUTH METHODS, 1 \x00 METHOD: NO AUTHENTICATION
		s.send(b'\x05\x01\x00')
		resp=s.recv(2)
		#print('{0:#x} {1:#x}'.format(resp[0],resp[1]))
		ret = resp==b'\x05\x00'
		s.close()
	except Exception as e:
		raise Exception("ERROR: {0}:{1:d} Exception {2}".format( ip_addr, port, e))
	if not ret:
		raise Exception('ERROR: {0}:{1:d} proxy sock connection failure'.format(ip_addr,port))

def process_address(line):
	(ip,port)=split_addr_port(line)
	test_socks5_server(ip,port)

def process_file(file_name,output_path):
	try:
		file = open(file_name, 'r') 
		line=file.readline()
		while len(line) > 0:
			try:
				process_address(line,output_path)
				print('{0} connection success'.format(line))
				writeoutput(output_path,line)
			except Exception as e:
				print(e)
			line=file.readline()
		file.close()
	except IOError as ioe:
		print(ioe)

#multi process implementation
def process_logqueue(logqueue,event):
	nblines=0
	while not (event.is_set() and logqueue.empty()):
		try:
			logline = logqueue.get(True,1) #wait 1 second
			
			if type(logline) is tuple:
				(output_path,line) = logline
				writeoutput(output_path,line)
			else:
				nblines += 1
				print("{0}".format(nblines),logline)
				
		except queue.Empty:
			#print("Exception: queue empty")
			pass
		except KeyboardInterrupt:
			break
	print("Stop log process. Nb lines read:",nblines)
	
def process_file_chunk(file_name,start,end,logqueue,output_path):
	print("starting worker process pid={0} [{1}-{2}]".format(os.getpid(),start,end))
	try:
		with open(file_name,"r") as fd:
			if start > 0:
				fd.seek(start-1)
				ch=fd.read(1)
				while ch!="\n" and fd.tell() < end: #start at next line
					ch=fd.read(1)
			
			while fd.tell() < end:
				line=''
				ch=fd.read(1)
				while ch!="\n" and ch!="":
					line+=ch
					ch=fd.read(1)
				if ch=="\n" or ch=="":
					#print("[{0},{1}] {2}".format(start,end,line))
					try:
						process_address(line)
						logqueue.put('[{0}] {1} connection success'.format(os.getpid(),line)) #log console
						logqueue.put((output_path,line)) #log to file
					except Exception as e:
						logqueue.put('[{0}] {1}'.format(os.getpid(),str(e)))
	except KeyboardInterrupt:
		print("Keyboard interrupt => exit worker process {0}".format(os.getpid()))
		sys.exit()
	except FileNotFoundError as ioe:
		print("error opening file",e)
	except Exception as e:
		print("error while reading",e)
		
def process_file_mp(file_name,output_path):
	
	file_size = os.stat(file_name).st_size
	chunk_size = 128 #min_chunk_size
	
	nbparts = min( int(mp.cpu_count()) , math.ceil(file_size / chunk_size) )
	chunk_size = math.ceil(file_size / nbparts)
	
	logqueue = mp.Queue();
	event = mp.Event()
	
	processes = [ mp.Process( target=process_file_chunk, args=(file_name, x, min(x+chunk_size-1,file_size),logqueue,output_path) ) for x in range(0,file_size,chunk_size)]
	
	try:
		# Run processes
		for p in processes:
			p.start()
	
		outputprocess = mp.Process( target=process_logqueue, args=(logqueue,event) )
		outputprocess.start()
		# Exit the completed processes
		for p in processes:
			p.join()
	except KeyboardInterrupt:
		logqueue.put("Keyboard interrupt => exit process {0}".format(os.getpid()))
	#shutdown log process
	event.set()
	outputprocess.join()

def main():
	parser=OptionParser()
	parser.add_option("-f","--file",action="store_true",default=False,help="if set, arguments processed as files")
	parser.add_option("-o","--output",action="store",default=None,help="if set, arguments processed as files")
	(options,args)=parser.parse_args()

	if options.output and os.path.isfile(options.output):
		os.remove(options.output)
	if len(args) > 0:
		if options.file:
			for f in args:
				process_file_mp(f,options.output)
		else:
			for addr in args:
				process_address(addr,options.output)
	else:
		print("no arguments provided")

if __name__=="__main__":
	main()