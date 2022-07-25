import tkinter as tk
import tkinter.ttk as ttk

import cv2 as cv2

from PIL import Image, ImageTk

class Interface(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # call the init function of the inherited class
        
        ###################
        # tkinter widgets #
        ###################

        self.frame_main = tk.Frame(self)

        self.label_video = tk.Label(self.frame_main)
        self.label_video.grid(row=0, column=0)

        self.butt_scan = ttk.Button(self.frame_main, text="Scan Image", command=self.scan)
        self.butt_scan.grid(row=1, column=0)

        self.frame_main.grid(row=0, column=0)

        self.frame_settings = tk.Frame(self)

        self.label_preprocess = tk.Label(self.frame_settings, text="Preprocess")
        self.label_preprocess.grid(row=1, column=0)

        self.var_preprocess = tk.BooleanVar(value=True)
        self.check_preprocess = ttk.Checkbutton(self.frame_settings, variable=self.var_preprocess)
        self.check_preprocess.grid(row=1, column=1)

        self.label_saveimg = tk.Label(self.frame_settings, text="Save Image")
        self.label_saveimg.grid(row=2, column=0)

        self.var_saveimg = tk.BooleanVar(value=False)
        self.check_saveimg = ttk.Checkbutton(self.frame_settings, variable=self.var_saveimg)
        self.check_saveimg.grid(row=2, column=1)

        self.label_savetxt = tk.Label(self.frame_settings, text="Save Text")
        self.label_savetxt.grid(row=3, column=0)

        self.var_savetxt = tk.BooleanVar(value=False)
        self.check_savetxt = ttk.Checkbutton(self.frame_settings, variable=self.var_savetxt)
        self.check_savetxt.grid(row=3, column=1)

        self.label_saveaudio = tk.Label(self.frame_settings, text="Save Audio")
        self.label_saveaudio.grid(row=4, column=0)

        self.var_saveaudio = tk.BooleanVar(value=False)
        self.check_saveaudio = ttk.Checkbutton(self.frame_settings, variable=self.var_saveaudio)
        self.check_saveaudio.grid(row=4, column=1)

        self.frame_settings.grid(row=0, column=1)

        #################
        # image capture #
        #################

        self.__video_feed = True
        self.cv_cam = cv2.VideoCapture(0)
        self.after(1, self.update_video)

    def update_video(self):
        if self.__video_feed:
            result, img = self.cv_cam.read()

            img_arr = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_arr)
            img_tk = ImageTk.PhotoImage(img_pil)

            self.label_video.config(image=img_tk)
            self.label_video.image = img_tk
            
            self.after(1, self.update_video)


    def scan(self):
        '''
        called when the user presses the 'scan image' button
        '''
        pass

if __name__ == '__main__':
    app = Interface()
    app.mainloop()