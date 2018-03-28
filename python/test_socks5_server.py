from optparse import OptionParser
import socket
import os
import re

def writeoutput(output_path,line):
	if output_path:
		with open(output_path,"a") as f:
			f.write(line)
			if line[-1]!='\n':
				f.write('\n')

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
		print("error test_addr: ",e)
		ret=False
	return ret

def process_file(file_name,output_path):
	try:
		file = open(file_name, 'r') 
		line=file.readline()
		while len(line) > 0:
			process_address(line,output_path)
			line=file.readline()
		file.close()
	except IOError as ioe:
		print(ioe)

def process_address(line,output_path):
	ip=''
	port=1080
	ip_regex=re.compile(r'(\d+(?:\.\d+){3})')
	port_regex=re.compile(r'(\d+(?:\.\d+){3}):(\d+)')
	
	m=ip_regex.search(line)
	if m:
		ip=m[0]
	else:
		return
	m=port_regex.search(line)
	if m and m.lastindex==2:
		port=int(m[2])
	ret=test_socks5_server(ip,port)
	if ret==True:
		print('{0}:{1:d} connection success'.format(ip,port))
		writeoutput(output_path,line)	
	else:
		print('ERROR: {0}:{1:d} connection failure'.format(ip,port))

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
				process_file(f,options.output)
		else:
			for addr in args:
				process_address(addr,options.output)
	else:
		print("no arguments provided")

if __name__=="__main__":
	main()