from gi.repository import Gtk, GObject
from audiofile import *
from subprocess import call
import os,sys,time
from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave

fl=0
files={}
scale=[]
files[1]=0
files[2]=0
files[3]=0
pids = [-1 for x in xrange(7)]
ofiles={}
ofiles[1]='output1.wav'
ofiles[2]='output2.wav'
ofiles[3]='output3.wav'
ofiles[4]='output4.wav'
ofiles[5]='output5.wav'
factor = [[0.0 for x in xrange(3)] for x in xrange(3)]
switch = [[0.0 for x in xrange(3)] for x in xrange(3)]
timex = [0.0 for x in xrange(7)]
state = [-1 for x in xrange(7)]
for i in range(9):
	scale.append(0.0)

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in xrange(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in xrange(int(seconds*RATE))])
    return r

def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(x,path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

class DialogExample(Gtk.Dialog):

    def __init__(self, parent,msg):
        Gtk.Dialog.__init__(self, "Error", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label(msg)

        box = self.get_content_area()
        box.add(label)
        self.show_all()
	
class FileChooserWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Wave Mixer")
	self.flagster=0
    

	#Creating Boxes
	hbox = Gtk.Box(spacing=0)
        hbox.set_homogeneous(False)
	vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox1.set_homogeneous(False)
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox2.set_homogeneous(False)
        vbox3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox3.set_homogeneous(False)
        vbox4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox4.set_homogeneous(False)
        hbox.pack_start(vbox1, True, True, 50)
        hbox.pack_start(vbox2, True, True, 50)
        hbox.pack_start(vbox3, True, True, 50)
        hbox.pack_start(vbox4, True, True, 50)
        image1 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
        image2 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
        image3 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
	image4 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
	image5 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
	        
        #Creating Labels for boxes
        label=Gtk.Label("Wave 1");
        vbox1.pack_start(label,True,False,0);
        label=Gtk.Label("Wave 2");
        vbox2.pack_start(label,True,False,0);
        label=Gtk.Label("Wave 3");
        vbox3.pack_start(label,True,False,0);
	
	#Creating fileChooser Dialogs
        button1 = Gtk.Button("Choose File")
        button1.connect("clicked", self.on_file_clicked,1)
        button2 = Gtk.Button("Choose File")
        button2.connect("clicked", self.on_file_clicked,2)
        button3 = Gtk.Button("Choose File")
        button3.connect("clicked", self.on_file_clicked,3)
        
        #Adding fileChooser buttons to vertical boxes
        vbox1.pack_start(button1,True,False,0);
        vbox2.pack_start(button2,True,False,0);
        vbox3.pack_start(button3,True,False,0);
        
        #Creating Labels for Amplitude
        label=Gtk.Label("Amplitude");
        vbox1.pack_start(label,True,False,0);
        label=Gtk.Label("Amplitude");
        vbox2.pack_start(label,True,False,0);
        label=Gtk.Label("Amplitude");
        vbox3.pack_start(label,True,False,0);
        
        #Creating Horizontal scales
        adjustment1 = Gtk.Adjustment(1, 0, 50, 5, 10, 0)
        adjustment2 = Gtk.Adjustment(1, 0, 100, 5, 10, 0)
        adjustment3 = Gtk.Adjustment(1, 0, 100, 5, 10, 0)
        self.hscale1 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment1)
        vbox1.pack_start(self.hscale1,True,False,0);
	self.hscale2 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment2)
        vbox2.pack_start(self.hscale2,True,False,0);
        self.hscale3 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment3)
        vbox3.pack_start(self.hscale3,True,False,0);
        
        #Creating Labels for Time Shift
        label=Gtk.Label("Time Shift");
        vbox1.pack_start(label,True,False,0);
        label=Gtk.Label("Time Shift");
        vbox2.pack_start(label,True,False,0);
        label=Gtk.Label("Time Shift");
        vbox3.pack_start(label,True,False,0);
        
        #Creating Horizontal scales
        adjustment4 = Gtk.Adjustment(0, -10, 10, 5, 10, 0)
        adjustment5 = Gtk.Adjustment(0, -10, 10, 5, 10, 0)
        adjustment6 = Gtk.Adjustment(0, -10, 10, 5, 10, 0)
        self.hscale4 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment4)
        vbox1.pack_start(self.hscale4,True,False,0);
	self.hscale5 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment5)
        vbox2.pack_start(self.hscale5,True,False,0);
        self.hscale6 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment6)
        vbox3.pack_start(self.hscale6,True,False,0);
        
        #Creating Labels for Time Scaling
        label=Gtk.Label("Time Scaling");
        vbox1.pack_start(label,True,False,0);
        label=Gtk.Label("Time Scaling");
        vbox2.pack_start(label,True,False,0);
        label=Gtk.Label("Time Scaling");
        vbox3.pack_start(label,True,False,0);
        
        #Creating Horizontal scales
        adjustment7 = Gtk.Adjustment(1, 0, 32, 5, 10, 0)
        adjustment8 = Gtk.Adjustment(1, 0, 32, 5, 10, 0)
        adjustment9 = Gtk.Adjustment(1, 0, 32, 5, 10, 0)
        self.hscale7 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment7)
        vbox1.pack_start(self.hscale7,True,False,0);
	self.hscale8 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment8)
        vbox2.pack_start(self.hscale8,True,False,0);
        self.hscale9 = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=adjustment9)
        vbox3.pack_start(self.hscale9,True,False,0);
        
        #Creating CheckBoxes for Time Reversal
        self.cbutton1=Gtk.CheckButton(label="Time Reversal", use_underline=False)
        self.cbutton2=Gtk.CheckButton(label="Time Reversal", use_underline=False)
        self.cbutton3=Gtk.CheckButton(label="Time Reversal", use_underline=False)
        vbox1.pack_start(self.cbutton1,True,False,0);
        vbox2.pack_start(self.cbutton2,True,False,0);
        vbox3.pack_start(self.cbutton3,True,False,0);
        
        #Creating CheckBoxes for Selection for Modulation
        self.cbutton4=Gtk.CheckButton(label="Selection for Modulation", use_underline=False)
        #self.cbutton4.connect("clicked", self.modulate)
        self.cbutton5=Gtk.CheckButton(label="Selection for Modulation", use_underline=False)
        #self.cbutton5.connect("clicked", self.modulate)
        self.cbutton6=Gtk.CheckButton(label="Selection for Modulation", use_underline=False)
        #self.cbutton6.connect("clicked", self.modulate)
        vbox1.pack_start(self.cbutton4,True,False,0);
        vbox2.pack_start(self.cbutton5,True,False,0);
        vbox3.pack_start(self.cbutton6,True,False,0);
        
        #Creating CheckBoxes for Selection for Mixing
        self.cbutton7=Gtk.CheckButton(label="Selection for Mixing", use_underline=False)
        self.cbutton8=Gtk.CheckButton(label="Selection for Mixing", use_underline=False)
        self.cbutton9=Gtk.CheckButton(label="Selection for Mixing", use_underline=False)
        vbox1.pack_start(self.cbutton7,True,False,0);
        vbox2.pack_start(self.cbutton8,True,False,0);
        vbox3.pack_start(self.cbutton9,True,False,0);
        
        #Adding play button
        self.playbutton1 = Gtk.Button(label=None, image=image1)
        self.playbutton2 = Gtk.Button(label=None, image=image2)
        self.playbutton3 = Gtk.Button(label=None, image=image3)
        vbox1.pack_start(self.playbutton1,True,False,0);
        self.playbutton1.connect("clicked", self.play_audio,1)
        vbox2.pack_start(self.playbutton2,True,False,0);
        self.playbutton2.connect("clicked", self.play_audio,2)
	vbox3.pack_start(self.playbutton3,True,False,0);
        self.playbutton3.connect("clicked", self.play_audio,3)

	#Adding ProgressBars
	self.progressbar1 = Gtk.ProgressBar()
	vbox1.pack_start(self.progressbar1, True, True, 0)
	self.progressbar2 = Gtk.ProgressBar()
	vbox2.pack_start(self.progressbar2, True, True, 0)
	self.progressbar3 = Gtk.ProgressBar()
	vbox3.pack_start(self.progressbar3, True, True, 0)
                
        #Creating Mixer
        label=Gtk.Label("Modulate and Play");
        vbox4.pack_start(label,True,False,0);
        self.playbutton4 = Gtk.Button(label=None, image=image4)
        self.playbutton4.connect("clicked", self.modulate_mix,1)
        vbox4.pack_start(self.playbutton4,True,False,0);
	self.progressbar4 = Gtk.ProgressBar()
	vbox4.pack_start(self.progressbar4, True, True, 0)
	label=Gtk.Label("Mix and Play");
        vbox4.pack_start(label,True,False,0);
        self.playbutton5 = Gtk.Button(label=None, image=image5)
        self.playbutton5.connect("clicked", self.modulate_mix,2)
        vbox4.pack_start(self.playbutton5,True,False,0);
	self.progressbar5 = Gtk.ProgressBar()
	vbox4.pack_start(self.progressbar5, True, True, 0)
        

    
	#Creating Record Button
	image6 = Gtk.Image(stock=Gtk.STOCK_MEDIA_RECORD)
        label=Gtk.Label("Record Audio");
        vbox4.pack_start(label,True,False,0);
        self.playbutton6 = Gtk.Button(label=None, image=image6)
        self.playbutton6.connect("clicked", record_to_file,"routput.wav")
        vbox4.pack_start(self.playbutton6,True,False,0);
	image7 = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)	
	label=Gtk.Label("Play Recorded Audio");
        vbox4.pack_start(label,True,False,0);
        self.playbutton7 = Gtk.Button(label="Play/Stop")
        self.playbutton7.connect("clicked", self.play_recorded,"routput.wav")
        vbox4.pack_start(self.playbutton7,True,False,0);
 
	self.progressbar=[]
        self.progressbar.append(self.progressbar1)
        self.progressbar.append(self.progressbar2)
        self.progressbar.append(self.progressbar3)
        self.progressbar.append(self.progressbar4)
        self.progressbar.append(self.progressbar5)

        self.timeout_id = GObject.timeout_add(100, self.on_timeout, self.progressbar)
        self.activity_mode = False
       
        self.add(hbox)

    def play_recorded(self,widget,filename):
	try:
		with open(filename):
			fout = Audiofile(filename,'rb')
			if (pids[6]>-1 and ((time.time()-timex[6])*100>=fout.getframerate()*fout.getnframes())) or pids[6]==-1 or fl==0:
				print '1'				
				fl=1	
				pid=os.fork()
		    		pids[6]=pid
				state[6]=1
				if pid==0:
					timex[6]=time.time()
					fout.play()
					sys.exit(0)
				self.flagster=1
			elif(pids[6]>0):
				state[6]=-1
		    		os.kill(pids[6],9)
	    			pids[6]=-1
			fout.close()
					
	except IOError:
		dialog=DialogExample(self,'No Audio Recorded')
		self.flagster=0
		response=dialog.run()
		dialog.destroy()
		return

	
    def on_timeout(self,user_data):
	for i in range(1,6):
            if(state[i]==1):
		if Audiofile(ofiles[i],'r').getnframes()!=0:
			user_data[i-1].set_fraction(((time.time()-timex[i])*Audiofile(ofiles[i],'r').getframerate())/(Audiofile(ofiles[i],'r').getnframes()))
		        if (((time.time()-timex[i])*Audiofile(ofiles[i],'r').getframerate())/(Audiofile(ofiles[i],'r').getnframes()))>=1:
		            user_data[i-1].set_fraction(0)
		            state[i]=-1
			    pids[i]=-1
		            image = Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)
		            if(i==1):
		                self.playbutton1.set_image(image)
		            if(i==2):
		                self.playbutton2.set_image(image)
		            if(i==3):
		                self.playbutton3.set_image(image)
		            if(i==4):
		                self.playbutton4.set_image(image)
		            if(i==5):
		                self.playbutton5.set_image(image)
	    elif(state[i]==-1):
	        user_data[i-1].set_fraction(0)

	# As this is a timeout function, return True so that it
	# continues to get called
	return True
	
    def on_file_clicked(self, widget,data):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
        	if data == 1:
        		files[1] = dialog.get_filename()
       		elif data == 2:
       			files[2] = dialog.get_filename()
       		else:
       			files[3] = dialog.get_filename()
       			
        dialog.destroy()
        
    def check(self):
    	factor[0][0] = self.hscale1.get_value()
    	factor[0][1] = self.hscale4.get_value()
    	factor[0][2] = self.hscale7.get_value()
    	switch[0][0] = self.cbutton1.get_active()
    	switch[0][1] = self.cbutton4.get_active()
    	switch[0][2] = self.cbutton7.get_active()
    	
    	factor[1][0] = self.hscale2.get_value()
    	factor[1][1] = self.hscale5.get_value()
    	factor[1][2] = self.hscale8.get_value()
    	switch[1][0] = self.cbutton2.get_active()
    	switch[1][1] = self.cbutton5.get_active()
    	switch[1][2] = self.cbutton8.get_active()
    	
    	factor[2][0] = self.hscale3.get_value()
    	factor[2][1] = self.hscale6.get_value()
    	factor[2][2] = self.hscale9.get_value()
    	switch[2][0] = self.cbutton3.get_active()
    	switch[2][1] = self.cbutton6.get_active()
    	switch[2][2] = self.cbutton9.get_active()
    		
    def modulate_mix(self,widget,dat):
	self.check()
	if((files[1] == 0 and files[2] == 0 and files[3] == 0) or (switch[0][dat] == 0 and switch[1][dat] == 0 and switch[2][dat] == 0)):
		dialog=DialogExample(self,'No file Selected')
		response=dialog.run()
		dialog.destroy()
		return

    	if(pids[dat+3]>0):
    		state[dat+3]=-1
	    	os.kill(pids[dat+3],9)
    		pids[dat+3]=-1
    	else:
		image = Gtk.Image(stock=Gtk.STOCK_MEDIA_STOP)
		if(dat==1):
		       	self.playbutton4.set_image(image)
		if(dat==2):
		       	self.playbutton5.set_image(image)
    		pid=os.fork()
	    	pids[dat+3]=pid		
	    	mydata=[]
	    	large=1
	    	for i in range(0,3):
	    		if switch[i][dat] == 1:
		    		fin=Audiofile(files[i+1],'rb')
		    		params=fin.file.getparams()
		    		fin.amplify(factor[i][0],params,ofiles[i+1])
		    		fin.time_shift(factor[i][1],params,ofiles[i+1])
		    		fin.time_scale(factor[i][2],params,ofiles[i+1])
		    		if switch[i][0] == 1:
		    			fin.reverse_audio(params,ofiles[i+1])
		    		fin.close()
		    		fout = Audiofile(ofiles[i+1],'rb')
		    		l = len(mydata)
		    		length = fout.getnframes()
		    		for j in range(length):
		    			if(l == 0 or j>=l):
		    				if(j>=l):
		    					large=i+1
		    				mydata.append(fout.data[j])
		    			else:
		    				if dat == 1:
		    					mydata[j]*=fout.data[j]
		    				else:
		    					mydata[j]+=fout.data[j]
		    		fout.close()
	    	fout = Audiofile(ofiles[dat+3],'wb')
	    	params=Audiofile(files[large],'rb').file.getparams()
	    	fout.file.setparams(params)
	    	lmax=len(mydata)
	    	for i in range(0,lmax):
	    		fout.write(mydata[i])
	    	fout.close()
		state[dat+3]=1
		timex[dat+3]=time.time()
	    	if pid==0:
			fout = Audiofile(ofiles[dat+3],'rb')
	    		fout.play()
	    		fout.close()
	    		sys.exit(0)
    		
    def play_audio(self,widget,data):
	if files[data] == 0:
		dialog=DialogExample(self,'No file Selected')
		response=dialog.run()
		dialog.destroy()
		
	else :
	    	if(pids[data]>0):
	    		state[data]=-1
	    		os.kill(pids[data],9)
	    		pids[data]=-1
	    	else:
		    	self.check()
			image = Gtk.Image(stock=Gtk.STOCK_MEDIA_STOP)
		        if(data==1):
		        	self.playbutton1.set_image(image)
		        if(data==2):
		        	self.playbutton2.set_image(image)
		        if(data==3):
		                self.playbutton3.set_image(image)
		    	pid=os.fork()
		    	fin = Audiofile(files[data],'r')
		    	params = fin.file.getparams()
		    	fin.read()
		    	pids[data]=pid
		    	fin.amplify(factor[data-1][0],params,ofiles[data])
			fin.time_shift(factor[data-1][1],params,ofiles[data])
		    	fin.time_scale(factor[data-1][2],params,ofiles[data])
		    	if switch[data-1][0] == 1:
		    		fin.reverse_audio(params,ofiles[data])
		    	fout = Audiofile(ofiles[data],'rb')
			state[data]=1
			timex[data]=time.time()
			if pid==0:	
				fout.play()
		    		sys.exit(0)
		    		

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("WAV Files")
        filter_text.add_mime_type("audio/wav")
        dialog.add_filter(filter_text)

win = FileChooserWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

