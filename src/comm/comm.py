'''
Created on 2016.12.20

@author: Zero
'''

import wx
import threading



import binascii
import serial.tools.list_ports



from wx._misc import MessageBox





class Comm():


    def openCom(self):
        
#          self.serialFd = serial.Serial('COM1',9600,timeout = 60)

        self.plist = list(serial.tools.list_ports.comports())
        if len(self.plist) <= 0:
            print "The Serial port can't find!"
            MessageBox('faile to open serial port','error')
             
        else:
            self.plist_0 =list(self.plist[0])
            serialName = self.plist_0[0]
            self.serialFd = serial.Serial(serialName,115200,timeout = 60)
            print "check which port was really used >",self.serialFd.name

    
    def comread(self):
        return self.serialFd.read(16)
    
    def senddata(self,data):
        self.serialFd.write(data)
    
    def getcom(self):
        return self.serialFd.portstr


    
class WorkThread(threading.Thread):
    def __init__(self,threadNum,window,com):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
        self.window = window
        self.timetoQuit = threading.Event()
        self.timetoQuit.clear()
        self.com = com
        self.doorisOpen = False

        
    def stop(self):
        self.timetoQuit.set()
    
    def run(self):    
        self.com.openCom()
        
        self.window.showCom()
        while True:
            self.timetoQuit.wait(1)
            if self.timetoQuit.isSet():
                break
            msg = self.com.comread()
            msg = msg.encode('hex')+'\n'

            msg_chg = ''
            for i in range(0,len(msg)):
                msg_chg +=msg[i]
                if i%2==1 & i!=0:
                    msg_chg += '    '
            msg = msg_chg
            
                # TODO process data
            wx.CallAfter(self.window.LogMessage,msg)
        


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title='comm',size = (400,600))
        
        
        self.threads = []
        self.count = 0
        self.com = Comm()
        
        panel = wx.Panel(self)
        font = wx.Font(15,wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        startBtn = wx.Button(panel,-1,'start')
        stopBtn = wx.Button(panel,-1,'stop')
        self.tc = wx.StaticText(panel,-1,'None')
        self.tc.SetFont(font)
        self.tc2 = wx.TextCtrl(panel,-1,'0',style = wx.TE_READONLY)
        self.tc2.SetFont(font)
#         comList = wx.Choice(panel,-1,choices = self.com.getcom())
           
        self.log = wx.TextCtrl(panel,-1,'',style = wx.TE_MULTILINE)
        self.log.SetBackgroundColour('gray')
        inner = wx.BoxSizer(wx.HORIZONTAL)
        inner.Add(startBtn,0,wx.RIGHT,15)
        inner.Add(stopBtn,0,wx.RIGHT,15)
        inner.Add(self.tc,0,wx.RIGHT,15)
        inner.Add(self.tc2,0,wx.RIGHT,5)
        
        
        
#         inner.Add(comList)
        
        self.sendtext = wx.TextCtrl(panel,-1,'',size = (280,30))
        
        sendBtn = wx.Button(panel,-1,'send') 
        sendBtn.SetFont(font)
        sendbox = wx.BoxSizer(wx.HORIZONTAL)
        sendbox.Add(self.sendtext,0,wx.EXPAND|wx.LEFT|wx.RIGHT,5)
        sendbox.Add(sendBtn,0,border = 5)
        
        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(inner, 0, wx.ALL, 5)
        main.Add(sendbox)
        main.Add(self.log, 1, wx.EXPAND|wx.ALL, 5)
        panel.SetSizer(main)
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, startBtn)
        self.Bind(wx.EVT_BUTTON, self.OnStopButton, stopBtn)
        self.Bind(wx.EVT_BUTTON, self.OnSendButton,sendBtn)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        
        
    def OnStartButton(self,evt):
        if self.count == 0:
            self.count+=1
            thread = WorkThread(self.count,self,self.com)
            self.threads.append(thread)
        

            thread.start()
    def OnStopButton(self, evt):
        self.StopThreads()
        self.tc.SetLabel('None')
        
    def OnSendButton(self,evt):
        sendmsg = self.sendtext.GetValue().split()

        for i in range(0,len(sendmsg)):
            sendmsg_hex = binascii.a2b_hex(sendmsg[i])
            self.com.senddata(sendmsg_hex)
       
    def OnCloseWindow(self, evt):
        self.StopThreads()
        self.Destroy()   
        if self.com.serialFd.isOpen():
            self.com.serialFd.close()

    def StopThreads(self):
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)  
            print -1
    def showCom(self):
        self.tc.SetLabel(self.com.getcom())          
    def LogMessage(self, msg):
        self.log.AppendText(msg)
        
 
class App(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.frame.Show()
        
        return True

    
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
   
    