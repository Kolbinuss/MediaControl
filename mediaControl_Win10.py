import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import tkinter.messagebox as tkm
import socket, math, os, time, threading
from PIL import Image, ImageTk
from subprocess import Popen, PIPE
import subprocess as subp
from functools import partial


class simpleapp_tk(tk.Tk):
    def __init__(self,parent):
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Variablen /Einleitungs - Kram:
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        #------- Initialisierung -----------------------------------------------
        tk.Tk.__init__(self,parent)
        self.parent = parent

        #------- Logfiles in txt schreiben/ Fenstermodus -------------------------------------
        self.debug=1
        self.fenster=0

        #------- Projektoren ---------------------------------------------------
        self.proj_vars = []
        self.proj_buts = []
        self.wall_buts = []
        self.proj_ips=['192.168.168.221','192.168.168.222','192.168.168.223','192.168.168.224','192.168.168.225','192.168.168.226','192.168.168.227','192.168.168.228','192.168.168.229','192.168.168.230']
        self.proj_name=['Beamer 1','Beamer 2','Beamer 3','Beamer 4','Beamer 5','Beamer 6','Beamer 7','Beamer 8','Beamer 9','Beamer 10']
        self.proj_telnet_port=['1','2','1','2','1','2','1','2','1','2']
        self.proj_telnet_on=[b'port 1 1\r\n',b'port 2 1\r\n',b'port 1 1\r\n',b'port 2 1\r\n',b'port 1 1\r\n',b'port 2 1\r\n',b'port 1 1\r\n',b'port 2 1\r\n',b'port 1 1\r\n',b'port 2 1\r\n']
        self.proj_telnet_off=[b'port 1 0\r\n',b'port 2 0\r\n',b'port 1 0\r\n',b'port 2 0\r\n',b'port 1 0\r\n',b'port 2 0\r\n',b'port 1 0\r\n',b'port 2 0\r\n',b'port 1 0\r\n',b'port 2 0\r\n']
        self.proj_telnet_is_off=[4,5,4,5,4,5,4,5,4,5]
        self.proj_post={'%001 POST 000000':'Deep Sleep','%001 POST 000001':'aus','%001 POST 000002':'am Starten','%001 POST 000003':'an','%001 POST 000004':'am Abkühlen','%001 POST 000005':'Critical powering down','%001 POST 000006':'Critical off'}

        #------- slave-pc's ---------------------------------------------------

        

        #--- KVE ---#
        self.pc_vars=[]
        self.pc_wol_start=['54BF647B237B','D89EF346C397', 'D89EF346C6DA','D89EF346C779','54BF647B71D2','54BF647A9DF3','54BF645D6EE6','54BF647B7F81','54BF647AF58D','D89EF346C570']
        self.pc_ips=['192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255','192.168.168.255']
        self.pc_names=['KVE41','KVE42','KVE43','KVE44','KVE45','KVE46','KVE47','KVE48','KVE49','KVE50']
        self.vrmhs='192.168.168.40'
        self.tablet='192.168.168.215'
        self.tracking='192.168.168.220'
        self.pc_warpingbat=['autostartCalibclient_Left','autostartCalibclient_Left','autostartCalibclient_Front_slave','autostartCalibclient_Front_master','autostartCalibclient_Right','autostartCalibclient_Right','autostartCalibclient_Top','autostartCalibclient_Top','autostartCalibclient_Bottom','autostartCalibclient_Bottom',]

        #--- JD ---#
        # self.vrmjd='192.168.168.200'

                
        #------- ip-steckdosen/Waende ----------------------------------------
        self.wall_vars=[]
        self.proj_ipsteck=['192.168.168.231','192.168.168.231','192.168.168.232','192.168.168.232','192.168.168.233','192.168.168.233','192.168.168.234','192.168.168.234','192.168.168.235','192.168.168.235']
        self.ip_ips=['192.168.168.231','192.168.168.232','192.168.168.233','192.168.168.234','192.168.168.235']
        self.proj_ipname=['IP 1','IP 1','IP 2','IP 2','IP 3','IP 3','IP 4','IP 4','IP 5','IP 5']

        #----- Befehle für Projektoren ---------------------------------------
        self.LOGINIP    = b'login admin admin\r\n'
        self.STATUSIP   = b'port list\r\n'
        self.STATUSPROJ = b':POST?\r'
        self.STARTROJ   = b':POWR1\r'
        self.STOPPROJ   = b':POWR0\r'
        self.HOURS      = b':LTR1?\r'
        self.SETDVI     = b':IDVI\r'
        self.SETHDMI    = b':IHDM\r'
        self.SETLEDVI   = b':IABS 2 0\r'
        self.SETREHDMI  = b':IABS 8 1\r'
        self.STEREO     = b':TDSM3\r'

        #----- Befehle für Projektoren und deren Abfrage ob gesetzt, für weniger Funktionen------------
        self.command_teststart =['Starten des Testbildes ',b':TEST1\r',b'%001 TEST 000001\r\n']
        self.command_testende  =['Beenden des Testbildes ',b':TEST0\r',b'%001 TEST 000000\r\n']
        self.command_mutstart  =['Muten des Bildes ',b':PMUT1\r',b'%001 PMUT 000001\r\n']
        self.command_mutende   =['Entmuten des Bildes ',b':PMUT0\r',b'%001 PMUT 000000\r\n']
        self.command_mono      =['Stereo ausschalten ',b':TDSM0\r',b'%001 TDSM 000000\r\n']
        self.command_stereo    =['Stereo einschalten ',b':TDSM3\r',b'%001 TDSM 000003\r\n']
        
        #----- Befehle für Umschalter ----------------------------------------
        # self.varWorkPlaceJD=[b'2\r',b'\x3a','JD',b'2\r   Route to input 2  \r','VRMJD']
        #self.varWorkPlaceHS=[b'1\r',b'\x3b','HS',b'1\r   Route to input 1  \r','VRMHS']
        self.varWorkPlaceHS=[b'3\r',b'\x3b','HS',b'3\r   Route to input 1  \r','VRMHS']


        #----- Masterrechner Eigenschaften -----------------------------------
        self.masterHS = ['192.168.168.40','VRMHS','D89EF346E29B']
        # self.masterJD = ['192.168.168.200','VRMJD','5065F32D6239']
        
        #----- Arrays initialisieren -----------------------------------------
        self.button_start = []
        self.button_slaves = []        
        self.threads = []
        self.statusButtons='on'
        
        #----- Fenster und Anpassungen ---------------------------------------
        if self.fenster==1:
            w=1366
            h=768
        else:
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.overrideredirect(1)
            
        self.geometry("%dx%d+0+0" % (w, h))        
        self.title('Mediensteuerung')

        #----- Schrift ändern ------------------------------------------------
        mytabfont=tkf.Font(size=20)
        myfont=tkf.Font(size=15)
        mytextfont=tkf.Font(size=12)
        myStyle = ttk.Style()
        myStyle.configure('.', font=mytabfont)
        myStyle.configure('TButton',font=myfont, padding  = 9)
        myStyle.configure('TLabel',font=mytextfont, padding  = 12)
        myStyle.configure('TCheckbutton',font=myfont, padding  = 12)
        myStyle.map("TButton",foreground=[('pressed', 'grey'),('disabled', 'white')])

        #----- Tabs definieren ----------------------------------------------
        self.mytabs=ttk.Notebook(parent)
        self.mytabs.pack(fill='both', expand='yes')
        tk.Text(self.mytabs, font=mytabfont)
        
        self.tabStart = ttk.Frame()
        self.mytabs.add(self.tabStart, text='Start   ')        
        self.tabSlaves = ttk.Frame()        
        self.mytabs.add(self.tabSlaves, text='Slaves   ')
        self.tabStatus = ttk.Frame()        
        self.mytabs.add(self.tabStatus, text='Status   ')

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Variablen /Einleitungs - Kram Ende!
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Layout Tab 1 = Startseite: John Deere / HS- System starten
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------

        self.tab1_top = tk.Frame(self.tabStart)
        self.tab1_top.pack(fill='both', expand='yes', side = "top" )

        self.tab1_fhs=tk.Frame(self.tab1_top, bg='#E6FFFF')
        self.tab1_fhs.pack(fill='both', expand='yes', side = "left" )
        # self.tab1_fjd=tk.Frame(self.tab1_top, bg='#E6F5EB')
        # self.tab1_fjd.pack(fill='both', expand='yes', side = "left" )
        
        self.tab1_ftrack=tk.Frame(self.tab1_top,bg='#E6FFFF')
        self.tab1_ftrack.pack(fill='both', expand='yes', side = "left" ) 
                   
        self.tab1_shutoff = tk.Frame(self.tabStart)
        self.tab1_shutoff.pack(fill='x', expand='yes', side = "top" )
        
        self.tab1_info = tk.Frame(self.tabStart,bg='#FFEBE6')
        self.tab1_info.pack(fill='both',expand='yes', side = "bottom" )


        self.setWorkPlaceHS=partial(self.setWorkPlace,self.varWorkPlaceHS)        
        self.button_start.append(ttk.Button(self.tab1_fhs,text="Bild/Tastatur/Maus", command=self.setWorkPlaceHS))

        self.stopHSMaster=partial(self.stopMaster,self.masterHS)
        self.button_start.append(ttk.Button(self.tab1_fhs,text="HS Master aus", command=self.stopHSMaster))

        self.startHSMaster=partial(self.startMaster,self.masterHS)
        self.button_start.append(ttk.Button(self.tab1_fhs,text="HS Master ein", command=self.startHSMaster))        
        
        photoHS =  tk.PhotoImage(file="images/1344949742-hs.gif")
        self.button_start.append(ttk.Button(self.tab1_fhs, image=photoHS, command=self.startSystemHS))
        self.button_start[-1].photo = photoHS

        # self.setWorkPlaceJD=partial(self.setWorkPlace,self.varWorkPlaceJD)
        # self.button_start.append(ttk.Button(self.tab1_fjd,text="Bild/Tastatur/Maus", command=self.setWorkPlaceJD))
        #
        # self.stopJDMaster=partial(self.stopMaster,self.masterJD)
        # self.button_start.append(ttk.Button(self.tab1_fjd,text="JD Master aus",command=self.stopJDMaster))
        #
        # self.startJDMaster=partial(self.startMaster,self.masterJD)
        # self.button_start.append(ttk.Button(self.tab1_fjd,text="JD Master ein",command=self.startJDMaster))
        #
        # photoJD =  tk.PhotoImage(file="images/1344949737-jd.gif")
        # self.button_start.append(ttk.Button(self.tab1_fjd, image=photoJD, command=self.startSystemJD))
        # self.button_start[-1].photo = photoJD

        self.button_start.append(ttk.Button(self.tab1_ftrack,text="start Tracking Software", command= self.startdtrack2))
        self.button_start.append(ttk.Button(self.tab1_ftrack,text="Tracking aus", command = self.stopTracking))
        self.button_start.append(ttk.Button(self.tab1_ftrack,text="(Neu)Start Tracking", command=self.Re_StartTracking))
        self.button_start.append(ttk.Button(self.tab1_ftrack,text="Kameras aus", command=self.endKameras))
        self.button_start.append(ttk.Button(self.tab1_ftrack,text="Kameras ein", command=self.startKameras))

        self.checkVRMHSlabel=tk.Label(self.tab1_ftrack,text="VRMHS läuft!")
        self.checkVRMHSlabel.pack(pady = 5)
        # self.checkVRMJDlabel=tk.Label(self.tab1_ftrack,text="VRMJD läuft!")
        # self.checkVRMJDlabel.pack(pady = 5)
        
        photoHS =  tk.PhotoImage(file="images/stop.gif")
        self.button_start.append(ttk.Button(self.tab1_shutoff, image=photoHS, command=self.systemOff))
        self.button_start[-1].photo = photoHS
        
        #------- Info-Leiste unten ---------------------------------------------
        self.info1text=['','','','','']
        self.info1 = tk.Label(self.tab1_info, text=self.info1text[0]+"\n"+self.info1text[1]+'\n'+self.info1text[2]+'\n'+self.info1text[3]+'\n'+self.info1text[4],bg='#FFEBE6')
        self.info1.pack(pady =10, fill="x")

        #------- Buttons endgültig darstellen ----------------------------------
        for i in range(len(self.button_start)):
            self.button_start[i].pack(fill ="x",pady = 5, padx=20,side="bottom")

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Layout Tab 2 = Slave-Rechner starten / bearbeiten
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------    
        self.tabSlaves_f6 = tk.Frame(self.tabSlaves)
        self.tabSlaves_f6.pack(side = "bottom", expand='yes', fill='both')
        
        self.tabSlaves_fill = tk.Frame(self.tabSlaves)
        self.tabSlaves_fill.pack(side = "bottom", expand='yes', fill='both')            

        self.tabSlaves_f1 = tk.Frame(self.tabSlaves, bg='#FFFFCC')
        self.tabSlaves_f1.pack(fill='both', expand='no', side = "left")

        self.tabSlaves_f3 = tk.Frame(self.tabSlaves, bg='#FFF5E6')
        self.tabSlaves_f3.pack(fill='both', expand='no', side = "left", padx=50)

        self.tabSlaves_f2 = tk.Frame(self.tabSlaves, padx=5)
        self.tabSlaves_f2.pack(side = "left", expand= "yes")

        self.tabSlaves_f5 = tk.Frame(self.tabSlaves, bg='#F0FAFF')
        self.tabSlaves_f5.pack(fill='both', expand='no', side = "left")

        self.tabSlaves_f7 = tk.Frame(self.tabSlaves)
        self.tabSlaves_f7.pack(expand='yes', side = "left")        

        #------- Projektoren ---------------------------------------------------
        for i in range(len(self.proj_ips)):
            self.proj_vars.append(tk.IntVar())
            photoBeamer = ImageTk.PhotoImage(Image.open("images/beamer"+str(i+1)+".gif"))            
            self.proj_buts.append(tk.Checkbutton(self.tabSlaves_f1, image=photoBeamer,variable=self.proj_vars[i], indicatoron=0, command=self.setChoiceProj))             
            self.proj_buts[i].photo = photoBeamer
            if i%2 == 0: 
                self.proj_buts[i].grid(row = math.ceil(i/2)+1, column = 0,pady = 5, padx = 5)
            else:
                self.proj_buts[i].grid(row = math.ceil(i/2), column = 1,pady = 5, padx = 5)

        #------- Wände ---------------------------------------------------------
        self.allProj_var=tk.IntVar()
        for i in range(len(self.ip_ips)):
            self.wall_vars.append(tk.IntVar())
            photoBeamer = ImageTk.PhotoImage(Image.open("images/ip_"+str(i+1)+".gif"))
            self.setChoiceWall_A=partial(self.setChoiceWall, i)
            self.wall_buts.append(tk.Checkbutton(self.tabSlaves_f3, image=photoBeamer,variable=self.wall_vars[i], indicatoron=0, command=self.setChoiceWall_A))
            self.wall_buts[i].photo = photoBeamer 
            self.wall_buts[i].pack(pady = 5, padx = 5)

        #------- Buttons Projektoren / Wände -----------------------------------
        self.allProj_but=ttk.Checkbutton(self.tabSlaves_f2, text="alle Projektoren", variable=self.allProj_var, command=self.setAllProj)
        self.allProj_but.pack(fill ="x", pady = 2,anchor="center")  

        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Steckdoseneingang ein", command=self.startIp))
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Steckdoseneingang aus",  command=self.stopIp))        
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Projektoren an", command=self.startProjektorEn))
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Projektoren aus",  command=self.stopProjektorEn))        

        self.setPropertyProjektor_stereo=partial(self.setPropertyProjektor, self.command_stereo)
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Stereo an", command=self.setPropertyProjektor_stereo))

        self.setPropertyProjektor_mono=partial(self.setPropertyProjektor, self.command_mono)
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Stereo aus",command=self.setPropertyProjektor_mono))

        self.setPropertyProjektor_teststart=partial(self.setPropertyProjektor, self.command_teststart)
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Testbild ein",  command=self.setPropertyProjektor_teststart))

        self.setPropertyProjektor_testende=partial(self.setPropertyProjektor, self.command_testende)       
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Testbild aus", command=self.setPropertyProjektor_testende))

        self.setPropertyProjektor_mutstart=partial(self.setPropertyProjektor, self.command_mutstart)
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Mute ein", command=self.setPropertyProjektor_mutstart))

        self.setPropertyProjektor_mutende=partial(self.setPropertyProjektor, self.command_mutende)
        self.button_slaves.append(ttk.Button(self.tabSlaves_f2,text="Mute aus", command=self.setPropertyProjektor_mutende))

        #------- Rechner -------------------------------------------------------
        for i in range(len(self.pc_ips)):
            self.pc_vars.append(tk.IntVar())
            if i<9:
                photoBeamer1=Image.open("images/vrs0"+str(i+1)+".gif")
            else:
                photoBeamer1=Image.open("images/vrs"+str(i+1)+".gif")
            
            photoBeamer = ImageTk.PhotoImage(photoBeamer1)            
            but=tk.Checkbutton(self.tabSlaves_f5, image=photoBeamer,variable=self.pc_vars[i], indicatoron=0, command=self.checkAllPcs)         
            but.photo = photoBeamer
            if i%2 == 0: 
                but.grid(row = math.ceil(i/2)+1, column = 0,pady = 5, padx = 5)
            else:
                but.grid(row = math.ceil(i/2), column = 1,pady = 5, padx = 5)

        #------- Button für die Rechner ----------------------------------------
        self.allPCVar=tk.IntVar()
        ttk.Checkbutton(self.tabSlaves_f7, text="alle Rechner", variable=self.allPCVar, command=self.setAllPC).pack(fill ="x", pady = 2, padx = 5)                
        self.button_slaves.append(ttk.Button(self.tabSlaves_f7,text="Herunterfahren",command=self.stopPC))
        self.button_slaves.append(ttk.Button(self.tabSlaves_f7,text="(Neu)Starten", command=self.Re_StartPC))
        self.button_slaves.append(ttk.Button(self.tabSlaves_f7,text="Warping (Neu)Starten", command=self.warping))
        self.button_slaves.append(ttk.Button(self.tabSlaves_f7,text="ICIDO Temp löschen", command=self.delICIDOTemp))
        
        #------- Info-Leiste unten ---------------------------------------------
        self.info2text=['','','','','']
        self.info2 = tk.Label(self.tabSlaves_f6, text=self.info2text[0]+"\n"+self.info2text[1]+'\n'+self.info2text[2]+'\n'+self.info2text[3]+'\n'+self.info2text[4],bg='#FFEBE6')
        self.info2.pack(fill="both")

        #------- Buttons endgültig darstellen ----------------------------------
        for i in range(len(self.button_slaves)):
            self.button_slaves[i].pack(fill ="x",pady = 2)            

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Layout Tab 3 = Status anzeigen lassen
        #----------------------------------------------------------------------------------------------------------------------------------------------------------- 
        self.statusButton=ttk.Button(self.tabStatus,text="Status auslesen / aktualisieren", command=self.getStatus)
        self.statusButton.pack( fill='x')
        self.tabStatusAll = tk.Frame(self.tabStatus)
        self.tabStatusAll.pack(anchor="n")

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Dauerschleife Master überprüfen
        #----------------------------------------------------------------------------------------------------------------------------------------------------------- 
        self.checkVRMHS()
        # self.checkVRMJD()
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
        # ENDE Initialisierung
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # START Funktionen
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------             
    #------- Threads/Funktionen ob ein Master per Ping erreichbar = an ist -
    def checkVRMHS(self):        
        t = threading.Thread(target=self.checkVRMHSThread)
        self.threads.append(t)
        t.start()   
    def checkVRMHSThread(self):
        while(1):
            out=Popen('ping -n 1 -w 5 '+self.vrmhs, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()
            if out.find('TTL')==-1:
                self.checkVRMHSlabel.pack_forget()
            else:
                self.checkVRMHSlabel.pack()
            time.sleep(10)
            
    # def checkVRMJD(self):
    #     t = threading.Thread(target=self.checkVRMJDThread)
    #     self.threads.append(t)
    #     t.start()
    # def checkVRMJDThread(self):
    #     while(1):
    #         out=Popen('ping -n 2 -w 5 '+self.vrmjd, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()
    #         if out.find('TTL')==-1:
    #             self.checkVRMJDlabel.pack_forget()
    #         else:
    #             self.checkVRMJDlabel.pack()
    #         time.sleep(20)

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Variablen Setzerei für Auswahlmöglichkeiten unter Slaves
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------              
    def setChoiceWall(self,h):
        allWalls=1
        if self.wall_vars[h].get()==1:
            self.proj_buts[h*2].select()
            self.proj_vars[h*2].set(1)
            self.proj_buts[h*2+1].select()
            self.proj_vars[h*2+1].set(1)
        else:
            self.proj_buts[h*2].select()
            self.proj_vars[h*2].set(0)
            self.proj_buts[h*2+1].select()
            self.proj_vars[h*2+1].set(0)
            self.allProj_var.set(0)  

        for i in range(len(self.wall_vars)):
            if self.wall_vars[i].get()!=1:
                allWalls=0 
        if allWalls==1:
            self.allProj_var.set(1)            

    def setChoiceProj(self):
        allProjs=1
        for i in range(len(self.wall_vars)):            
            if self.proj_vars[i*2].get()==1 and self.proj_vars[i*2+1].get()==1:
                self.wall_buts[i].select()
                self.wall_vars[i].set(1)
            else:
                self.wall_buts[i].select()
                self.wall_vars[i].set(0)
                self.allProj_var.set(0)
                allProjs=0
        if allProjs==1:
            self.allProj_var.set(1)

    def setAllProj(self):
        for i in range(len(self.wall_vars)):
            if self.allProj_var.get()==1:
                self.wall_vars[i].set(1)
                self.wall_buts[i].select()
                self.proj_buts[i*2+1].select()
                self.proj_buts[i*2+0].select()  
                self.proj_vars[i*2+1].set(1)
                self.proj_vars[i*2+0].set(1)
            else:
                self.wall_vars[i].set(0)
                self.wall_buts[i].deselect()
                self.proj_buts[i*2+1].deselect()
                self.proj_buts[i*2+0].deselect()  
                self.proj_vars[i*2+1].set(0)
                self.proj_vars[i*2+0].set(0)
                
    def setAllPC(self):
        for i in range(10):
            if self.allPCVar.get()==1:
                self.pc_vars[i].set(1)
            else:
                self.pc_vars[i].set(0)

    def checkAllPcs(self):
        allPcs=1
        for i in range(10):
            if self.pc_vars[i].get()==0:
                self.allPCVar.set(0)
                allPcs=0
        if allPcs==1:
            self.allPCVar.set(1)
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Grund - Funktionen zum (Neu)Starten / Stoppen von Rechnern
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #------- Master stoppen und starten ---------------------------------------------------    
    def startMaster(self,WHO):
        self.wake(WHO[2],WHO[1])
        
    def stopMaster(self,who):
        p=Popen('ping -n 1 -w 5 '+who[0], stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if str(stdout).find('TTL')!=-1:
            #geht nicht mit Firewall... deswegen nur Infofenster
            #os.system('shutdown -s -t 5 -m \\\\'+self.vrmhs)
            if who[1]=="VRMHS":
                self.setWorkPlace(self.varWorkPlaceHS)
            # if who[1]=="VRMJD":
            #     self.setWorkPlace(self.varWorkPlaceJD)
            tkm.showinfo('Achtung', who[1]+' bitte von Hand ausschalten XD ', icon="warning")
        else:
            self.setInfoText(self.getTime()+' PC '+who[1]+' nicht erreichbar, schon aus?')
            
    #------- Tracking stoppen und starten ---------------------------------------------
    def stopTracking(self):
        s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.settimeout(2)
        var = s1.connect_ex((self.tracking, 50105))
        if (not var):
            s1.send(b'dtrack2 system shutdown')
            if s1.recv(1024) != b'dtrack2 ok\x00':
                self.setInfoText(self.getTime()+' Runterfahren des Trackingsystems war nicht erfolgreich')
            else:
                self.setInfoText(self.getTime()+' Runterfahren des Trackingsystems war erfolgreich')
        else:
            self.setInfoText(self.getTime()+' Trackingsystem mit der IP-Adresse '+self.tracking+' nicht erreichbar, schon aus?')
        s1.close()
    
    def Re_StartTracking(self):
        p=Popen("ping -n 1 -w 5 "+self.tracking, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        #hochfahrbefehl senden, wenn nicht erreichbar
        if str(stdout).find('TTL')==-1:
            self.wake('6cf049a15ae7','Tracking')

        #Neustarten, wenn erreichbar            
        else:
            s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(2)
            var = s1.connect_ex((self.tracking, 50105))
            if (not var):
                s1.send(b'dtrack2 system reboot')
                if s1.recv(1024) != b'dtrack2 ok\x00':
                    self.setInfoText(self.getTime()+' Neustart des Trackingsystems war nicht erfolgreich')
                else:
                    self.setInfoText(self.getTime()+'Trackingsystem ist an --> Neustart war erfolgreich')                     
            else:
                self.setInfoText(self.getTime()+' Trackingsystem mit der IP-Adresse '+self.tracking+' nicht erreichbar!?')
            s1.close()     

    def startdtrack2(self):
        subp.call(['C:\\Program Files (x86)\\ART\\DTrack2\\DTrack2.exe'])

    #------- Sonstige Rechner per wol starten ---------------------------------------------
    def wake(self, whoMAC, whoNAME):
        p=Popen('wol '+whoMAC+' '+self.tablet, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if stdout==b'Wake-On-LAN Utility 1.5\r\r\nCopyright (C) 2000-2009 by Greg Wittmeyer - All Rights Reserved\r\r\n\r\r\nFailed to send wake-up packet, code 4\r\r\nFailed to bind to adapter.':
             # self.setInfoText(self.getTime()+' VRMJD wird nicht gestartet - Fehler im WOL-Befehl')
             self.setInfoText(self.getTime() + ' Test')
        else:
            if stderr==b'':
                self.setInfoText(self.getTime()+' '+whoNAME+' : Startbefehl erfolgreich gesendet')
            else:
                self.setInfoText(self.getTime()+' '+whoNAME+' : Startbefehl nicht gesendet Fehler- '+str(stderr))

    #------- Rechner stoppen mit Thread --------------------------------------------------
    def stopPC(self):
        t = threading.Thread(target=self.stopPCThread)
        self.threads.append(t)
        t.start()
    def stopPCThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
            
        for h in range(len(self.pc_ips)):    
            if self.pc_vars[h].get() == 1:
                p=Popen("ping -n 1 -w 5 "+self.pc_ips[h], stdout=PIPE, stderr=PIPE, shell=True)
                stdout, stderr = p.communicate()
                if str(stdout).find('TTL')!=-1:                  
                    p2=Popen('shutdown -s -t 5 -m \\\\'+self.pc_ips[h], stdout=PIPE, stderr=PIPE, shell=True)
                    stdout2, stderr2 = p2.communicate()
                    if stderr2==b'':
                        self.setInfoText(self.getTime()+' '+self.pc_names[h] +' wird heruntergefahren')
                    else:
                        self.setInfoText(self.getTime()+' '+self.pc_names[h] +' wird nicht heruntergefahren, hier stimmt was nicht?!')
                else:
                    self.setInfoText(self.getTime()+' '+self.pc_names[h] +' nicht erreichbar, schon aus?')

        if statusbevor=='on':                  
            self.enableButtons()

    #------- Rechner Nnustarten mit Thread --------------------------------------------------
    def Re_StartPC(self):
        t = threading.Thread(target=self.Re_StartPCThread)
        self.threads.append(t)
        t.start()
    def Re_StartPCThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
            
        for h in range(len(self.pc_ips)):            
            if self.pc_vars[h].get() == 1:
                #hochfahrbefehl senden, wenn nicht erreichbar
                stdout=Popen("ping -n 1 -w 5 "+self.pc_ips[h], stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()   
                if stdout.find('TTL')==-1:
                    #self.setInfoText(self.getTime()+' PC '+self.pc_names[h]+' ist aus --> jetzt wecken')
                    self.wake(self.pc_wol_start[h], self.pc_names[h])
                else:
                    #self.setInfoText(self.getTime()+' PC '+self.pc_names[h]+' ist an --> neutarten')
                    # sonst neustarten
                    befehl='psexec \\\\'+self.pc_ips[h]+' -d -i C:\\Windows\\System32\\shutdown.exe -r -t 2'
                    stderr2=Popen(befehl, stdout=PIPE, stderr=PIPE, shell=True).communicate()[1].decode("utf-8", errors='ignore').strip()
                    if stderr2.find('shutdown.exe started on ')!=-1:
                        self.setInfoText(self.getTime()+' '+self.pc_names[h] +' ist an --> wird neugestartet')
                    else:
                        self.setInfoText(self.getTime()+' '+self.pc_names[h] +' wird nicht neugestartet, undefinierbarer Fehler ')
                        print(stderr2)
        if statusbevor=='on':
            self.enableButtons()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Bild / Maus / Tastur umschalten
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def setWorkPlace(self, WHO):
        #set mouse+keyboard     
        s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.settimeout(2)
        var = s1.connect_ex(('192.168.168.240', 4999))
        if (not var):
            s1.send(WHO[1])
            if s1.recv(1024)!=b';':
                self.setInfoText(self.getTime()+' Umrouten von Maus & Tastatur auf '+WHO[4]+' war nicht erfolgreich')
            else:
                self.setInfoText(self.getTime()+' Umrouten von Maus & Tastatur auf '+WHO[4]+' war erfolgreich')
        else:
            self.setInfoText(self.getTime()+' Umschalter mit der IP-Adresse 192.168.168.240 ist nicht erreichbar')
        s1.close()
        
        #set image      
        s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.settimeout(2)
        var = s1.connect_ex(('192.168.168.240', 5000))
        if (not var):
            s1.send(WHO[0])
            a=s1.recv(1024)
            if a!=WHO[0] and  a!=WHO[3]:
                self.setInfoText(self.getTime()+' Umrouten von Bild auf '+WHO[4]+' war nicht erfolgreich')
            else:
                self.setInfoText(self.getTime()+' Umrouten von Bild auf '+WHO[4]+' war erfolgreich')
        else:
            self.setInfoText(self.getTime()+' Umschalter mit der IP-Adresse 192.168.168.240 ist nicht erreichbar')
        s1.close()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Kameras 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def startKameras(self):
        for h in range(5): 
            s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(2)
            var = s1.connect_ex((self.ip_ips[h], 1234))
            if (not var):
                s1.recv(1025)
                s1.send(b'login admin admin\r\n')
                if s1.recv(1025)!=b'250 OK\r\n':
                    self.setInfoText(self.getTime()+' Beim Login zur Steckdose '+self.ip_ips[h]+' ist ein Fehler aufgetreten')
                else:
                    s1.send(b'port 3 1\r\n')
                    if s1.recv(1025)==b'250 OK\r\n':
                        self.setInfoText(self.getTime()+' Einschalten der Steckdose  '+self.ip_ips[h]+'  an Port 3 erfolgreich')
            else:
                self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.ip_ips[h]+ ' ist nicht erreichbar.')
            s1.close()

    def endKameras(self):
        for h in range(5): 
            s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(2)
            var = s1.connect_ex((self.ip_ips[h], 1234))
            if (not var):
                s1.recv(1025)
                s1.send(b'login admin admin\r\n')
                if s1.recv(1025)!=b'250 OK\r\n':
                    self.setInfoText(self.getTime()+' Beim Login zur Steckdose '+self.ip_ips[h]+' ist ein Fehler aufgetreten')
                else:
                    s1.send(b'port 3 0\r\n')
                    if s1.recv(1025)==b'250 OK\r\n':
                        self.setInfoText(self.getTime()+' Auschalten der Steckdose  '+self.ip_ips[h]+'  an Port 3 erfolgreich')
            else:
                self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.ip_ips[h]+ ' ist nicht erreichbar.')
            s1.close()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # HS System starten 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------       
    def startSystemHS(self):
        
        t = threading.Thread(target=self.startSystemHSThread)
        self.threads.append(t)
        t.start()

    def startSystemHSThread(self):
        self.disableButtons()
        self.setWorkPlace(self.varWorkPlaceHS)

        for i in range(10):
            self.proj_vars[i].set(1)
        for i in range(10):
            self.pc_vars[i].set(1)       

        self.startIp()
        self.Re_StartPC()

        # JD Master ist an? -->Meldung, bitte Ausschalten
        # p=Popen('ping -n 1 -w 5 '+self.vrmjd, stdout=PIPE, stderr=PIPE, shell=True)
        # stdout, stderr = p.communicate()
        # if str(stdout).find('TTL')!=-1:
        #     #self.setInfoText('Bitte John-Deere Master per Hand runter fahren!')
        #     self.setWorkPlace(self.varWorkPlaceJD)
        #     tkm.showinfo('Achtung', 'VRMJD bitte von Hand ausschalten XD \n DANACH okay drücken!', icon="warning")
        #     self.setWorkPlace(self.varWorkPlaceHS)
    
        p=Popen('ping -n 1 -w 5 '+self.vrmhs, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        # HS Master ist aus: --> Starte HS-MASTER
        if str(stdout).find('TTL')==-1:        
            self.setInfoText(self.getTime()+' Starte HS Master')
            self.startMaster(self.masterHS)
        # HS Master ist an: --> Starte HS-MASTER neu
        else:
            #a=os.system('shutdown -r -t 5 -m \\\\'+self.vrmhs)
            tkm.showinfo('Achtung', 'VRMHS bitte von Hand neustarten XD ', icon="warning")
            #self.setInfoText(self.getTime()+' Bitte HS Master neustarten')
        
        self.Re_StartTracking()
        iTime=0
        while iTime<140:
            self.setInfoText(self.getTime()+' Warte noch '+str(140-iTime)+'s bis die Projektoren gestartet werden...')
            time.sleep(20)
            iTime=iTime+20

        self.startProjektorEn()
        self.projThread.join()        
        for i in range(10):
            self.proj_vars[i].set(0)
        for i in range(10):
            self.pc_vars[i].set(0)
        for i in range(5):
            self.wall_vars[i].set(0)            

        self.enableButtons()
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # JD System starten 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------  
    # def startSystemJD(self):
    #     t = threading.Thread(target=self.startSystemJDThread)
    #     self.threads.append(t)
    #     t.start()
    #
    # def startSystemJDThread(self):
    #     self.disableButtons()
    #     self.setWorkPlace(self.varWorkPlaceJD)
    #
    #     for i in range(10):
    #         self.proj_vars[i].set(1)
    #     for i in range(10):
    #         self.pc_vars[i].set(1)
    #
    #     #----IP weglassen, wegen IP-Adressenverlust Test
    #     self.startIp()
    #     self.Re_StartPC()
    #
    #     # HS Master ist an? -->Meldung, bitte Ausschalten
    #     p=Popen('ping -n 1 -w 5 '+self.vrmhs, stdout=PIPE, stderr=PIPE, shell=True)
    #     stdout, stderr = p.communicate()
    #     if str(stdout).find('TTL')!=-1:
    #         #self.setInfoText('Bitte HS Master per Hand runter fahren!')
    #         self.setWorkPlace(self.varWorkPlaceHS)
    #         tkm.showinfo('Achtung', 'VRMHS  bitte von Hand ausschalten XD \n DANACH okay drücken!', icon="warning")
    #         self.setWorkPlace(self.varWorkPlaceJD)
    #
    #     # JD Master an oder aus?
    #     p=Popen('ping -n 1 -w 5 '+self.vrmjd, stdout=PIPE, stderr=PIPE, shell=True)
    #     stdout, stderr = p.communicate()
    #     # JD Master ist aus: --> Starte JD-MASTER
    #     if str(stdout).find('TTL')==-1:
    #         self.setInfoText(self.getTime()+' Starte JD Master')
    #         self.startMaster(self.masterJD)
    #     # JD Master ist an: --> Starte JD-MASTER neu
    #     else:
    #         #a=os.system('shutdown -r -t 5 -m \\\\'+self.vrmhs)
    #         #self.setInfoText(self.getTime()+' Bitte JD Master neustarten')
    #         tkm.showinfo('Achtung', 'VRMJD bitte von Hand neustarten XD ', icon="warning")
    #
    #     self.Re_StartTracking()
    #
    #     iTime=0
    #     while iTime<140:
    #         self.setInfoText(self.getTime()+' Warte noch '+str(140-iTime)+' bis die Projektoren gestartet werden...')
    #         time.sleep(20)
    #         iTime=iTime+20
    #     self.startProjektorEn()
    #     self.projThread.join()
    #     for i in range(10):
    #         self.proj_vars[i].set(0)
    #     for i in range(10):
    #         self.pc_vars[i].set(0)
    #     self.enableButtons()
    #     for i in range(5):
    #         self.wall_vars[i].set(0)

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # ALLES runterfahren und Stoppen
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------           
    def systemOff(self):        
        t = threading.Thread(target=self.systemOffThread)
        self.threads.append(t)
        t.start()   
    def systemOffThread(self):
        self.disableButtons()
        self.setInfoText(self.getTime()+' System herunterfahren')

        self.stopHSMaster()
        # self.stopJDMaster()

        for i in range(10):
            self.pc_vars[i].set(1)       
        self.stopPC()
        time.sleep(10)
        
        for i in range(10):
            self.proj_vars[i].set(1)       
        self.stopProjektorEn()  
            
        self.stopTracking()
        iTime=0

        while iTime<120:
            self.setInfoText(self.getTime()+' Warte noch '+str(120-iTime)+'s bis die Projektoren abgekühlt sind...')
            time.sleep(20)
            iTime=iTime+20

        self.stopIp()
        self.StopIpThread.join()
            
        for i in range(10):
            self.proj_vars[i].set(0)
        for i in range(5):
            self.wall_vars[i].set(0)            
        for i in range(10):
            self.pc_vars[i].set(0)        
        self.enableButtons()
   
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Projektoren starten
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------         
    def startProjektorEn(self):        
        t = threading.Thread(target=self.startProjektorEnThread)
        self.threads.append(t)
        t.start()
        self.projThread=t
    def startProjektorEnThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
        
        #for h in range(len(self.proj_ips)):
        for h in range(len(self.proj_ips)):
            if self.proj_vars[h].get() == 1:
                #--> IP Steckdose Verbinden
                #print('Verbinden auf: '+self.proj_ipsteck[h])
                s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s1.settimeout(1)
                var = s1.connect_ex((self.proj_ipsteck[h], 1234))
                if (not var):
                    get1=s1.recv(1025).decode("utf-8").strip()
                    #print(get1)
                    s1.send(self.LOGINIP)
                    #--> IP Steckdose einloggen erfolgreich?
                    get2=s1.recv(1025).decode("utf-8").strip()
                    #print(get2)
                    if get2!='250 OK':                
                        self.setInfoText(self.getTime()+' No Login possible on IP '+self.proj_ipsteck[h])
                        s1.close()
                    else:
                        s1.send(self.proj_telnet_on[h])
                        get3=s1.recv(1025).decode("utf-8").strip()
                        s1.close()
                        #print(get3)
                        if get3!='250 OK':
                            self.setInfoText(self.getTime()+' Start IP isn`t possible on '+self.proj_ipsteck[h])
                        else:
                            #-->Steckdose erfolgreich gestartet -->Projektor starten                           
                            s2  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.settimeout(15.0)
                            #print('Verbinden auf: '+self.proj_ips[h])
                            var = s2.connect_ex((self.proj_ips[h], 1025))
                            if (not var):
                                s2.send(self.STATUSPROJ)
                                time.sleep(1)
                                get4=s2.recv(1025).decode("utf-8").strip()
                                #print(get4)
                                if get4=='%001 POST 000000' or get4=='%001 POST 000001': 
                                    s2.send(self.STARTROJ)
                                    get5=s2.recv(1025).decode("utf-8").strip()
                                    #print(get5)
                                    if get5=='%001 POWR 000001':
                                        self.setInfoText(self.getTime()+' Starten von Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' war erfolgreich')
                                        time.sleep(1)
                                        s2.send(self.STEREO)
                                        time.sleep(1)
                                        s2.send(self.SETLEDVI)
                                        time.sleep(1)
                                        s2.send(self.SETREHDMI)                                
                                    else:
                                        self.setInfoText(self.getTime()+'Starten von Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' war nicht erfolgreich')
                                else:
                                    if get4 in self.proj_post.keys():                                    
                                        self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist: '+self.proj_post[get4])
                                    else:
                                        self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' hat seltsame Meldung: '+get4)
                            else:
                                self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist nicht erreichbar')
                            s2.close()                            
                else:
                    self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist nicht erreichbar')                        

        if statusbevor=='on':                  
            self.enableButtons()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Projektoren stoppen
    #----------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def stopProjektorEn(self):        
        t = threading.Thread(target=self.stopProjektorEnThread)
        self.threads.append(t)
        t.start()   
    def stopProjektorEnThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
        for h in range(len(self.proj_ips)):            
            if self.proj_vars[h].get() == 1:
                #Steckdose an oder aus?
                s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s1.settimeout(1)
                var = s1.connect_ex((self.proj_ipsteck[h], 1234))
                if (not var):
                    get1=s1.recv(1025).decode("utf-8").strip()
                    #print(get1)
                    s1.send(self.LOGINIP)
                    #--> IP Steckdose einloggen erfolgreich?
                    get2=s1.recv(1025).decode("utf-8").strip()
                    #print(get2)
                    if get2=='250 OK':
                        #-->Ausgang an oder aus?
                        s1.send(self.STATUSIP)
                        get2=s1.recv(1025).decode("utf-8").strip()
                        #print(get2)
                        if get2[self.proj_telnet_is_off[h]]=='0':
                            #ausgang aus -->Projektor MUSS aus sein
                            self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist schon aus --> Projektor muss auch aus sein')
                        else:
                            #ausgang ein -->Projektor überprüfen:
                            s2  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.settimeout(2)
                            var = s2.connect_ex((self.proj_ips[h], 1025))
                            if (not var):
                                s2.send(self.STATUSPROJ)
                                get3=s2.recv(1025).decode("utf-8").strip()
                                #print(get3)
                                #print('Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist '+self.proj_post[get3])
                                if get3=='%001 POST 000000':
                                    self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist ganz arg aus ;)')                                
                                elif get3=='%001 POST 000001':
                                    self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist aus')
                                elif get3=='%001 POST 000002':
                                    self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist am Hochfahren')                                    
                                elif get3=='%001 POST 000003':
                                    s2.send(self.STOPPROJ)
                                    get4=s2.recv(1025).decode("utf-8").strip()
                                    if get4=='%001 POWR 000000':
                                        self.setInfoText(self.getTime()+' Stoppen von Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' war erfolgreich')
                                    else:
                                        self.setInfoText(self.getTime()+' Stoppen von Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' war nicht erfolgreich')
                                elif get3=='%001 POST 000004':
                                    self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist am abkühlen')
                                else:
                                    self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' hat BÖSEN Fehler')

                            else:
                                self.setInfoText(self.getTime()+' Projektor mit IP-Adresse '+ self.proj_ips[h]+ ' ist nicht erreichbar')
                            s2.close()
                    else:
                        self.setInfoText(self.getTime()+' Login an der Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+' nicht möglich')

                else:
                    self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist nicht erreichbar')                     
                    
                s1.close()

        if statusbevor=='on':                  
            self.enableButtons()            
                        
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # IP - Steckdosen ansteuern
    #----------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def startIp(self):
        t = threading.Thread(target=self.startIpThread)
        self.threads.append(t)
        t.start()
    def startIpThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
            
        for h in range(len(self.proj_ipsteck)):            
            if self.proj_vars[h].get() == 1:
                LOGIN=b'login admin admin\r\n'
                s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s1.settimeout(2)
                var = s1.connect_ex((self.proj_ipsteck[h], 1234))
                if (not var):
                    s1.recv(1025)
                    s1.send(LOGIN)
                    if s1.recv(1025)!=b'250 OK\r\n':                
                        self.setInfoText(self.getTime()+' No Login possible on IP '+self.proj_ipsteck[h])
                    else:
                        s1.send(self.proj_telnet_on[h])
                        if s1.recv(1025)!=b'250 OK\r\n':
                            self.setInfoText(self.getTime()+' Start IP isn`t possible on '+self.proj_ipsteck[h])
                        else:
                            self.setInfoText(self.getTime()+' Start power outlet was successful on '+self.proj_ipsteck[h]+' on port '+self.proj_telnet_port[h])
                else:
                    self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist nicht erreichbar')
                s1.close()
                time.sleep(1)

        if statusbevor=='on':
            self.enableButtons()
        #print('-------------------------------------------')            

    def stopIp(self):
        t = threading.Thread(target=self.stopIpThread)
        self.threads.append(t)
        self.StopIpThread=t
        t.start()
    def stopIpThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
 
        for h in range(10):            
            if self.proj_vars[h].get() == 1:              
                #überprüfen, ob ip-Steckdose schon aus
                s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s1.settimeout(2)
                var = s1.connect_ex((self.proj_ipsteck[h], 1234))
                if (not var):
                    get1=s1.recv(1025).decode("utf-8").strip()
                    #print(get1)
                    s1.send(self.LOGINIP)
                    #--> IP Steckdose einloggen erfolgreich?
                    get2=s1.recv(1025).decode("utf-8").strip()
                    #print(get2)
                    if get2!='250 OK':                
                        self.setInfoText(self.getTime()+' No Login possible on IP '+self.proj_ipsteck[h])
                    else:
                        s1.send(b'port list\r\n')
                        a=s1.recv(1025).decode("utf-8").strip()
                        if a[self.proj_telnet_is_off[h]]=='1':
                            #print('Auf dem Eingang ist strom')
                            #Steckdose an --> Status des Projektors auslesen:
                            s2  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.settimeout(2)
                            var = s2.connect_ex((self.proj_ips[h], 1025))
                            if (not var):
                                s2.send(self.STATUSPROJ)
                                get3=s2.recv(1025).decode("utf-8").strip()
                                #print(get3)
                                #----> Projektor aus  --> Steckdose ausschalten
                                if get3=='%001 POST 000000' or get3=='%001 POST 000001':
                                    #print('Steckdose ausschalten')
                                    s1.send(self.proj_telnet_off[h])
                                    get4=s1.recv(1025).decode("utf-8").strip()   
                                    if get4=='250 OK':
                                        self.setInfoText(self.getTime()+' Ausschalten der Steckdose '+self.proj_ipsteck[h]+' erfolgreich')
                                    else:
                                        self.setInfoText(self.getTime()+' Beim Ausschalten der Steckdose '+self.proj_ipsteck[h]+' ist ein Fehler aufgetreten')

                                #----> Sonstiger Zustand: Meldung und abfragen
                                else:
                                    #print('Hier Meldungsfenster mit Abfrage')
                                    if tkm.askyesno('Achtung', 'Der Projektor ( '+self.proj_ips[h]+' ) ist noch nicht aus, wirklich ausschalten? GEFAHR für den Projektor!!!! Status: '+self.proj_post[get3], icon="warning")==True:
                                        #print('ausschalten!')
                                        s1.send(self.proj_telnet_off[h])
                                        get4=s1.recv(1025).decode("utf-8").strip()   
                                        if get4=='250 OK':
                                            self.setInfoText(self.getTime()+' Ausschalten der Steckdose '+self.proj_ipsteck[h]+' erfolgreich')
                                        else:
                                            self.setInfoText(self.getTime()+' Beim Ausschalten der Steckdose '+self.proj_ipsteck[h]+' ist ein Fehler aufgetreten')                                            
                                    else:
                                        self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' wird nicht ausgeschaltet')  
                            else:
                                self.setInfoText(self.getTime()+' Projektor mit der IP-Adresse '+ self.proj_ips[h]+ ' ist nicht erreichbar?!')
                                    #print('Hier Meldungsfenster mit Abfrage')
                                if tkm.askyesno('Achtung', 'Der Projektor ( '+self.proj_ips[h]+' ) ist nicht erreichbar, wirklich Steckodes ausschalten?!! GEFAHR für den Projektor!!!!', icon="warning")==True:
                                    #print('ausschalten!')
                                    s1.send(self.proj_telnet_off[h])
                                    get4=s1.recv(1025).decode("utf-8").strip()   
                                    if get4=='250 OK':
                                        self.setInfoText(self.getTime()+' Ausschalten der Steckdose '+self.proj_ipsteck[h]+' erfolgreich')
                                    else:
                                        self.setInfoText(self.getTime()+' Beim Ausschalten der Steckdose '+self.proj_ipsteck[h]+' ist ein Fehler aufgetreten')                                            
                                else:
                                    self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' wird nicht ausgeschaltet')                                
                                
                            s2.close()
                        else:
                            self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist schon aus')                      
                else:
                    self.setInfoText(self.getTime()+' Steckdose mit der IP-Adresse '+self.proj_ipsteck[h]+ ' ist nicht erreichbar?')
                s1.close()

        if statusbevor=='on':                  
            self.enableButtons()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Slave - Tab: NEUE und verkürzte Funktionen für Projektoren
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    def setPropertyProjektor(self,command):
        t = threading.Thread(target=self.setPropertyProjektorThread (command))
        self.threads.append(t)
        t.start()
    def setPropertyProjektorThread(self,command):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'            
              
        for h in range(len(self.proj_ips)):            
            if self.proj_vars[h].get() == 1:
                s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s1.settimeout(2)
                var = s1.connect_ex((self.proj_ips[h], 1025))
                if (not var):
                    #print(command[1])
                    s1.send(command[1])    # Befehl     
                    if s1.recv(1024)!=command[2]: #schauen ob eigenschaft gesetzt
                        self.setInfoText(self.getTime()+command[0]+' auf Projektor mit der IP-Adresse '+ self.proj_ips[h]+ ' war nicht erfolgreich')
                    else:
                    #    time.sleep(1)
                    #    s1.send(self.SETLEDVI)
                    #    time.sleep(1)
                    #    s1.send(self.SETREHDMI)
                        self.setInfoText(self.getTime()+command[0]+' auf Projektor mit der IP-Adresse '+ self.proj_ips[h])
                else:
                    self.setInfoText(self.getTime()+' Projektor mit der IP-Adresse '+ self.proj_ips[h]+ ' ist nicht erreichbar')
                s1.close()
            
        if statusbevor=='on':                  
            self.enableButtons()       
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Slave - Tab: Warping auf Rechnern neu starten
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------              
    def warping(self):
        t = threading.Thread(target=self.warpingThread)
        self.threads.append(t)
        t.start()
    def warpingThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
            
        for h in range(len(self.pc_ips)):
            if self.pc_vars[h].get() == 1 and h is not 3:
                befehl='psexec \\\\'+self.pc_names[h]+' -i -d -u CAVE -p CAVE C:\\' +self.pc_warpingbat[h]+'.bat'
                p2=Popen(befehl, stdout=PIPE, stderr=PIPE, shell=True)
                stdout, stderr = p2.communicate()
                if stdout==b'':
                    self.setInfoText(self.getTime()+' '+self.pc_warpingbat[h] +' auf '+self.pc_names[h]+' wird ausgeführt')                
                else:
                    self.setInfoText(self.getTime()+' '+self.pc_warpingbat[h] +' auf' +self.pc_names[h]+' wird nicht ausgeführt. Fehler: '+str(stderr2))

        befehl='psexec \\\\'+self.pc_names[3]+' -i -d -u CAVE -p CAVE C:\\' +self.pc_warpingbat[3]+'.bat'
        p2=Popen(befehl, stdout=PIPE, stderr=PIPE, shell=True)    
            
        if statusbevor=='on':                  
            self.enableButtons()            

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Status - Tab mit Inhalt füllen
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------      
    def getStatus(self):
        t = threading.Thread(target=self.getStatusThread)
        self.threads.append(t)
        t.start()
    def getStatusThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'        

        for child in self.tabStatusAll.winfo_children():
            child.destroy()
            
        myrow=0        
        #HS Master
        mycolor='red'
        output=Popen("ping -n 1 -w 5 "+self.vrmhs, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()
        #print('HSMASTER: '+output)
        if str(output).find('TTL')!=-1:
            mycolor='green'
        T = ttk.Label(self.tabStatusAll, text='VRMHS', foreground=mycolor).grid(row=0,column=2)
        
        # #JD Master
        # mycolor='red'
        # get=Popen("ping -n 1 -w 5 "+self.vrmjd, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()
        # #print(get)
        # if str(get).find('TTL')!=-1:
        #     mycolor='green'
        # T = ttk.Label(self.tabStatusAll, text='VRMJD', foreground=mycolor).grid(row=0,column=5)
        
        #Tracking
        mycolor='red' 
        get=Popen("ping -n 1 -w 5 "+self.tracking, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()    
        #print(get)        
        if get.find('TTL')!=-1:
            mycolor='green'       
        T = ttk.Label(self.tabStatusAll, text='Tracking', foreground=mycolor).grid(row=myrow,column=7)

        myrow=1        
        #Rechner Status:
        self.logo=[]
        self.logoImage=[]
        for h in range(10):
            mycolor='red'
            get=Popen("ping -n 1 -w 5 "+self.pc_ips[h], stdout=PIPE, stderr=PIPE, shell=True).communicate()[0].decode("utf-8", errors='ignore').strip()                
            if str(get).find('TTL')!=-1:
                mycolor='green'
            if h<9:
                self.logo.append(Image.open("images/vrsx/vrs0"+str(h+1)+".gif"))
            else:
                self.logo.append(Image.open("images/vrsx/vrs"+str(h+1)+".gif"))
                
            self.logoImage.append(ImageTk.PhotoImage(self.logo[h]))
            ttk.Label(self.tabStatusAll, text=self.pc_names[h], foreground=mycolor,image=self.logoImage[h], compound='top').grid(row=myrow,column=h)

        myrow=2
        #Steckdosen Status:
        self.photoBeamer1=[]
        self.photoBeamer=[]
        statusIP=[]
        for h in range(10):
            statusIP.append('0')
            mycolor='red' 
            s1  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.settimeout(1)
            var = s1.connect_ex((self.proj_ipsteck[h], 1234))
            if (not var):
                get1=s1.recv(1025).decode("utf-8", errors='ignore').strip()
                s1.send(self.LOGINIP)
                get2=s1.recv(1025).decode("utf-8", errors='ignore').strip()
                if get2!='250 OK':                
                    self.setInfoText(self.getTime()+' No Login possible on IP '+self.proj_ipsteck[h])
                    s1.close()
                else:
                    s1.send(self.STATUSIP)
                    get3=s1.recv(1025).decode("utf-8", errors='ignore').strip()
                    s1.close()

                    if get3[self.proj_telnet_is_off[h]]=='1':
                        mycolor='green'
                        statusIP[h]='1'

            self.photoBeamer1.append(Image.open("images/beamer"+str(h+1)+".gif"))
            self. photoBeamer.append(ImageTk.PhotoImage(self.photoBeamer1[h]))                   
            ttk.Label(self.tabStatusAll, text=self.proj_ipname[h]+':'+self.proj_telnet_port[h], foreground=mycolor,image=self.photoBeamer[h], compound='top').grid(row=myrow,column=h)            

        myrow=4
        #Projektoren Status:
        for h in range(10):
            get5=''
            mycolor='red'
            if statusIP[h]=='1':
                s2  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s2.settimeout(2)
                var = s2.connect_ex((self.proj_ips[h], 1025))
                if (not var):
                    s2.send(self.STATUSPROJ)
                    time.sleep(1)
                    get4=s2.recv(1025).decode("utf-8", errors='ignore').strip()

                    s2.send(self.HOURS)
                    time.sleep(1)
                    get5=str(s2.recv(1024).decode("utf-8", errors='ignore').strip()[10:16])
                    
                    s2.close()
                    if get4=='%001 POST 000003':
                        mycolor='green'
            T = ttk.Label(self.tabStatusAll, text=self.proj_name[h], foreground=mycolor).grid(row=myrow,column=h)
            T = ttk.Label(self.tabStatusAll, text=get5, foreground=mycolor).grid(row=myrow+1,column=h)

        if statusbevor=='on':                  
            self.enableButtons()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Hilfsfunktion: Infotext aktualisieren
    #----------------------------------------------------------------------------------------------------------------------------------------------------------- 
    def setInfoText(self,text):
        tab=self.mytabs.index(self.mytabs.select())
        if tab==0:
            self.info1text.append(text)
            self.info1text.pop(0)
            self.info1.config(text=self.info1text[0]+"\n"+self.info1text[1]+'\n'+self.info1text[2]+'\n'+self.info1text[3]+'\n'+self.info1text[4])

        if tab==1:
            self.info2text.append(text)
            self.info2text.pop(0)
            self.info2.config(text=self.info2text[0]+"\n"+self.info2text[1]+'\n'+self.info2text[2]+'\n'+self.info2text[3]+'\n'+self.info2text[4])

        if self.debug==1:
            logfile=open('log.txt','a')
            logfile.write(self.getDate()+' '+text+'\n')
            logfile.close()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Hilfsfunktion: Buttons deaktivieren, wenn Threads laufen
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------                 
    def disableButtons(self):
        for i in range(len(self.button_start)):
            self.button_start[i].state(["disabled"])            
        for i in range(len(self.button_slaves)):
            self.button_slaves[i].state(["disabled"])
        self.statusButtons='off'
        self.statusButton.state(["disabled"])  
            
    def enableButtons(self):
        for i in range(len(self.button_start)):
            self.button_start[i].state(["!disabled"])            
        for i in range(len(self.button_slaves)):
            self.button_slaves[i].state(["!disabled"])
        self.statusButtons='on'
        self.statusButton.state(["!disabled"])              

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Hilfsfunktion: ICIDO-Temp Ornder löschen auf den Slaves
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------      
    def delICIDOTemp(self):
        t = threading.Thread(target=self.delICIDOTempThread)
        self.threads.append(t)
        t.start()
    def delICIDOTempThread(self):
        if self.statusButtons=='on':
            self.disableButtons()
            statusbevor='on'
        else:
            statusbevor='off'
            
        for h in range(len(self.pc_ips)):            
            if self.pc_vars[h].get() == 1:
                befehl='psexec \\\\'+self.pc_names[h]+' -i -d -u CAVE -p CAVE C:\\deleteICIDOTemp.bat'
                p2=Popen(befehl, stdout=PIPE, stderr=PIPE, shell=True)
                stdout, stderr = p2.communicate()
                if stdout==b'':
                    self.setInfoText(self.getTime()+' '+self.pc_names[h]+' : Löschen von Tempverzeichnis erfolgreich angestoßen')
                else:
                    self.setInfoText(self.getTime()+' '+self.pc_names[h]+' : Löschen nicht angestoßen- '+str(stderr))
            
        if statusbevor=='on':                  
            self.enableButtons()            
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    # Hilfsfunktion für Zeit
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------              
    def getTime(self):
        return time.strftime("%H:%M:%S ", time.localtime())

    def getDate(self):
        return time.strftime("%d.%m.%Y", time.localtime())
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------------  		
if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('CAVE Steuerung')    
    app.mainloop()            
