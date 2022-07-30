import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, simpledialog

import cv2 as cv2

from PIL import Image, ImageTk

import classes
class Interface(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # call the init function of the inherited class

        self.ocr = classes.OCR()
        
        self.current_img = None

        ###################
        # tkinter widgets #
        ###################

        self.frame_main = tk.Frame(self)

        self.label_video = tk.Label(self.frame_main)
        self.label_video.grid(row=0, column=0)

        self.butt_scan = ttk.Button(self.frame_main, text="Scan Image", command=self.scan)
        self.butt_scan.grid(row=1, column=0)

        self.frame_main.grid(row=0, column=0)

        ############
        # settings #
        ############

        self.frame_settings = tk.Frame(self)

        # sets whether preprocessing happens on a captured image
        self.label_preprocess = tk.Label(self.frame_settings, text="Preprocess")
        self.label_preprocess.grid(row=1, column=0)

        self.var_preprocess = tk.BooleanVar(value=True)
        self.check_preprocess = ttk.Checkbutton(self.frame_settings, variable=self.var_preprocess)
        self.check_preprocess.grid(row=1, column=1)

        # sets whether the captured image is saved and where it is saved
        self.label_saveimg = tk.Label(self.frame_settings, text="Save Image")
        self.label_saveimg.grid(row=2, column=0)

        self.var_saveimg = tk.BooleanVar(value=False)
        self.check_saveimg = ttk.Checkbutton(self.frame_settings, variable=self.var_saveimg)
        self.check_saveimg.grid(row=2, column=1)
        
        dir_width = 50
        self.saveimg_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.saveimg_dir.grid(row=2, column=2)

        self.butt_saveimg_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_saveimg_dir)
        self.butt_saveimg_changedir.grid(row=2, column=3)

        # sets whether the scanned text is saved and where it is saved
        self.label_savetxt = tk.Label(self.frame_settings, text="Save Text")
        self.label_savetxt.grid(row=3, column=0)

        self.var_savetxt = tk.BooleanVar(value=False)
        self.check_savetxt = ttk.Checkbutton(self.frame_settings, variable=self.var_savetxt)
        self.check_savetxt.grid(row=3, column=1)

        self.savetxt_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.savetxt_dir.grid(row=3, column=2)

        self.butt_savetxt_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_savetxt_dir)
        self.butt_savetxt_changedir.grid(row=3, column=3)

        # sets whether the tts audio file is saved and where it is saved
        self.label_saveaudio = tk.Label(self.frame_settings, text="Save Audio")
        self.label_saveaudio.grid(row=4, column=0)

        self.var_saveaudio = tk.BooleanVar(value=False)
        self.check_saveaudio = ttk.Checkbutton(self.frame_settings, variable=self.var_saveaudio)
        self.check_saveaudio.grid(row=4, column=1)

        self.saveaudio_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.saveaudio_dir.grid(row=4, column=2)

        self.butt_saveaudio_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_saveaudio_dir)
        self.butt_saveaudio_changedir.grid(row=4, column=3)

        self.frame_settings.grid(row=0, column=1)

        #################
        # image capture #
        #################

        self.__video_feed = True # determines whether the video feed should be updated or not
        self.cv_cam = cv2.VideoCapture(0)
        self.start_video()

    def stop_video(self):
        self.__video_feed = False

    def start_video(self):
        self.__video_feed = True
        self.after(150, self.update_video)

    def update_video(self):
        if self.__video_feed:
            result, img = self.cv_cam.read()

            self.current_img = img
            img_arr = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_arr)
            img_tk = ImageTk.PhotoImage(img_pil)

            self.label_video.config(image=img_tk)
            self.label_video.image = img_tk

            self.after(150, self.update_video) # repeat function after 1 millisecond


    def scan(self):
        '''
        called when the user presses the 'scan image' button
        '''
        img = self.current_img

        if self.var_saveimg.get():
            filename = simpledialog.askstring('Image Name', 'Enter image file name')
            cv2.imwrite(f'{self.saveimg_dir.get()}/{filename}.jpg', img)

        txt = self.ocr.scan_image(img)

        if self.var_savetxt.get():
            filename = simpledialog.askstring('Text File Name', 'Enter text file name')
            with open(f'{self.savetxt_dir.get()}/{filename}.jpg', 'w') as f:
                f.write(txt)

        self.ocr.tts(txt)
    
    def change_saveimg_dir(self):
        '''
        allows the user to change what directory the captured image is saved to
        '''

        new_dir = filedialog.askdirectory()
        self.saveimg_dir.delete(0, tk.END)
        self.saveimg_dir.insert(0, new_dir)

    def change_savetxt_dir(self):
        '''
        allows the user to change what directory the scanned text is saved to
        '''

        new_dir = filedialog.askdirectory()
        self.savetxt_dir.delete(0, tk.END)
        self.savetxt_dir.insert(0, new_dir)

    def change_saveaudio_dir(self):
        '''
        allows the user to change what directory the tts audio is saved to
        '''

        new_dir = filedialog.askdirectory()
        self.saveaudio_dir.delete(0, tk.END)
        self.saveaudio_dir.insert(0, new_dir)

if __name__ == '__main__':
    app = Interface()
    app.mainloop()