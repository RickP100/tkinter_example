from vidgear.gears.asyncio import NetGear_Async
import asyncio, cv2, time, PIL
import tkinter as tk
from PIL import Image, ImageTk

# define connection parameters for NetGear_Async
clientInitOptions = {'address': '192.168.X.XXX', 'port': 'XXXX', 'protocol': 'tcp', 'pattern': 2, 'receive_mode': True, 'logging': True}

class NetGearAsyncClient():
    def __init__(self, initOptions, updateRate=100):
        self.client = NetGear_Async(**initOptions)
        self.stopLoop = False
        self.frame = None
        self.interval = (1.0/updateRate)
                    
    async def frame_receiver(self):
        async for frame in self.client.recv_generator():

            if self.stopLoop:
                break
           
            self.frame = frame
            # print('grabbed a frame from the network!')
    
            await asyncio.sleep(self.interval)

    def read(self):
        return self.frame
            
    def start(self):
        self.client.launch()
        asyncio.set_event_loop(self.client.loop)
        
        print('*** calling run until complete')
        self.client.loop.run_until_complete(self.frame_receiver())
        print('*** returned from calling run until complete')
        
    def stop(self):
        self.stopLoop = True
        
class VideoWidget(tk.Label):
    def __init__(self, attachedto, vs, fps):
        tk.Label.__init__(self, attachedto, text='')
        self.vs = vs
        self.frame = self.vs.read()
        self.stopped = False
        self.frameRate = fps
        self.frameInterval = int(1000/self.frameRate)

    def start(self):
        self.vs.start()
        time.sleep(1)
        self.update_displayed_frame()

    def update_displayed_frame(self):

        # get current frame from video source
        self.frame = self.vs.read()
        
        # convert and display the image in the tk label widget
        if self.frame is not None:
            self.imgtk = self.frame2imgtk(self.frame)
            self.configure(image=self.imgtk)
        
        # schedule the next update to run 1/fps seconds later
        if not self.stopped:
            self.after(self.frameInterval, self.update_displayed_frame)

    def stop(self):
        self.stopped = True
        self.vs.stop()
        
    def frame2imgtk(self, frame):
        frm = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frm, cv2.COLOR_BGR2RGBA)
        img = PIL.Image.fromarray(cv2image)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        return imgtk
        
def show_messagebox():
    tk.messagebox.showinfo(message='GUI still responding')

root = tk.Tk()

# an object that opens a NetGear_Async object and tries to receive frames from the network at up to 100Hz        
vidSource = NetGearAsyncClient(clientInitOptions, updateRate=100)

# an object that polls vidSource for its latest frame at 10Hz and displays it in the GUI 
vw = VideoWidget(root, vs=vidSource, fps=10)

# GUI
tk.Button(master=root, text='Start Video', command=vw.start).pack()
tk.Button(master=root, text='Stop Video', command=vw.stop).pack()
tk.Button(master=root, text='Check if GUI is responding', command=show_messagebox).pack()
vw.pack()
root.mainloop()
    
     
