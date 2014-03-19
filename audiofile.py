import struct,wave
import pyaudio,time
from math import *

class Audiofile:
	def __init__(self,filename,mode):
		self.file=wave.open(filename,mode)
		self.data=[]
		self.pid=-1
		self.playing=0
		if mode == 'r' or mode == 'rb':
			self.read()
		
	def close(self):
		self.file.close()
		
	def write(self,sample):
		if sample > 32767:
			sample = 32767
		if sample < -32768:
			sample = -32768
		if self.getsampwidth() == 1:
			sample = sample - 128
			if sample > 127:
				sample = 127
			if sample < -128:
				sample = -128
			sample = sample + 128
			packed_data = struct.pack('B',sample)
		if self.getsampwidth() == 2:
			if sample > 32767:
				sample = 32767
			if sample < -32768:
				sample = -32768	
			packed_data = struct.pack('h',sample)
		params=self.file.getparams()
		self.file.writeframes(packed_data)
		
	def getnframes(self):
		return self.file.getnframes()
		
	def getnchannels(self):
		return self.file.getnchannels()
		
	def getframerate(self):
		return self.file.getframerate()
	
	def getsampwidth(self):
		return self.file.getsampwidth()
		
	def setparams(self,nchannels,sampwidth,framerate,nframes,comptype,compname):
		self.file.setparams((nchannels,sampwidth,framerate,nframes,comptype,compname))
	
	def tell(self):
		return self.file.tell()
		
	def read(self):
		self.file.setpos(0)
		self.data=[]
		sampwidth = self.getsampwidth()
		r = self.file.readframes( self.getnframes() )
        	total_samples = self.getnframes() * self.getnchannels()
	        if sampwidth == 1:
       	     		fmt = "%iB" % total_samples
       	 	elif sampwidth == 2:
       	     		fmt = "%ih" % total_samples
       	 	inw = struct.unpack(fmt, r)
       	 	for i in inw:
            		self.data.append(i)
		
	def play(self):
		chunk = 1024
		p = pyaudio.PyAudio()
		self.file.setpos(0)
		stream = p.open(format=p.get_format_from_width(self.file.getsampwidth()),channels=self.file.getnchannels(),rate=self.file.getframerate(),output=True)
		data = self.file.readframes(chunk)
		while data != '':
			stream.write(data)
			data = self.file.readframes(chunk)
		stream.close()
		p.terminate()
	
	def reverse_audio(self,params,fname):
		fout = Audiofile(fname,'wb')
		fout.file.setparams(params)
		mode='mono'
		if(self.file.getnchannels==2):
			mode='stereo'
		self.file.setpos(0)
		length = self.getnframes()
		raudio = self.data
		if(mode == 'mono'):
			raudio.reverse()
		else:
			l=len(raudio)
			for i in range(0,len/2,2):
				raudio[i],raudio[len-2]=raudio[len-2],raudio[i]
				raudio[i+1],raudio[len-1]=raudio[len-1],raudio[i+1]
		self.data=raudio
		l=len(raudio)
		for i in range(0,l):
			fout.write(raudio[i])
		fout.close()
				
	def amplify(self,factor,params,fname):
    		fout = Audiofile(fname,'w')
    		fout.file.setparams(params)
    		self.file.setpos(0)
    		length = len(self.data)
    		for i in range(0,length):
    			self.data[i] = float(self.data[i]) * factor
    			fout.write(self.data[i])
    		fout.close()
    	
    	def time_scale(self,factor,params,fname):
    		fout = Audiofile(fname,'wb')
    		fout.file.setparams(params)
    		self.file.setpos(0)
    		channels = self.getnchannels()
    		length = len(self.data)
    		flag=0
		mydata=[]
		if factor < 1 :
			if channels == 1:
				for i in range(length):
					mydata.append(self.data[i])
					fout.write(self.data[i])
					x = int(ceil(1/factor))-1
					for j in range(x):
						mydata.append(0)
						fout.write(0)
			else :
				for i in range(0,length-2,2):	
					fout.write(self.data[i])
    					fout.write(self.data[i+1])
    					mydata.append(self.data[i])
    					mydata.append(self.data[i+1])
					x = int(1/factor)-1
					for j in range(x):
						mydata.append(0)
						fout.write(0)
		else:			
	    		if factor == float(int(factor)):
	    			factor=int(factor) * channels
	    		else:
	    			flag=1
	    			factor = factor / channels
	    		for i in range(0,length-2):
	    			if flag==0:
	    				if i%factor == 0:
	    					mydata.append(self.data[i])
	    					fout.write(self.data[i])
	    			else:
	    				if float(i)*factor == float(int(float(i)*factor)):
	   					if(i%2==0):
	    						fout.write(self.data[i])
	    						fout.write(self.data[i+1])
	    						mydata.append(self.data[i])
	    						mydata.append(self.data[i+1])
	    					else:
	    						fout.write(self.data[i-1])
	    						fout.write(self.data[i])
	    						mydata.append(self.data[i-1])
	    						mydata.append(self.data[i])
    		self.data=mydata   			
    		fout.close()	
    	
    	def time_shift(self,factor,params,fname):
    		fout = Audiofile(fname,'wb')
    		fout.file.setparams(params)
    		self.file.setpos(0)
    		rate = self.getframerate()
    		channels = self.getnchannels()
    		length = self.getnframes()
		start = int(float(rate)*factor)
		mydata=[]
		if factor >= 0:
	    		self.file.setpos(start)
	    		for i in range(start,length):
	    			fout.write(self.data[i])
	    			mydata.append(self.data[i])
		else :
			start = start * -1
			for i in range(start):
				fout.write(0)
				mydata.append(0)
			for i in range(length):
				fout.write(self.data[i])
	    			mydata.append(self.data[i])
	    	self.data=mydata
    		fout.close()
