import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, simpledialog

import threading

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

        self.frame_butts = tk.Frame(self.frame_main)

        self.butt_scan = ttk.Button(self.frame_butts, text="Scan Image", command=lambda: self.scan(self.current_img))
        self.butt_scan.grid(row=1, column=0)

        self.butt_import = ttk.Button(self.frame_butts, text="Import Image ⭳", command=self.import_image)
        self.butt_import.grid(row=1, column=1)

        self.frame_butts.grid(row=1, column=0)
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

        # sets if the preprocessed image gets displayed to the user
        self.label_showimg = tk.Label(self.frame_settings, text="Display Processed Image")
        self.label_showimg.grid(row=2, column=0)

        self.var_showimg = tk.BooleanVar(value=True)
        self.check_showimg = ttk.Checkbutton(self.frame_settings, variable=self.var_showimg)
        self.check_showimg.grid(row=2, column=1)

        # sets whether the captured image is saved and where it is saved
        self.label_saveimg = tk.Label(self.frame_settings, text="Save Image")
        self.label_saveimg.grid(row=3, column=0)

        self.var_saveimg = tk.BooleanVar(value=False)
        self.check_saveimg = ttk.Checkbutton(self.frame_settings, variable=self.var_saveimg)
        self.check_saveimg.grid(row=3, column=1)
        
        dir_width = 50
        self.saveimg_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.saveimg_dir.grid(row=3, column=2)

        self.butt_saveimg_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_saveimg_dir)
        self.butt_saveimg_changedir.grid(row=3, column=3)

        # sets whether the scanned text is saved and where it is saved
        self.label_savetxt = tk.Label(self.frame_settings, text="Save Text")
        self.label_savetxt.grid(row=4, column=0)

        self.var_savetxt = tk.BooleanVar(value=False)
        self.check_savetxt = ttk.Checkbutton(self.frame_settings, variable=self.var_savetxt)
        self.check_savetxt.grid(row=4, column=1)

        self.savetxt_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.savetxt_dir.grid(row=4, column=2)

        self.butt_savetxt_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_savetxt_dir)
        self.butt_savetxt_changedir.grid(row=4, column=3)

        # sets whether the tts audio file is saved and where it is saved
        self.label_saveaudio = tk.Label(self.frame_settings, text="Save Audio")
        self.label_saveaudio.grid(row=5, column=0)

        self.var_saveaudio = tk.BooleanVar(value=False)
        self.check_saveaudio = ttk.Checkbutton(self.frame_settings, variable=self.var_saveaudio)
        self.check_saveaudio.grid(row=5, column=1)

        self.saveaudio_dir = ttk.Entry(self.frame_settings, width=dir_width)
        self.saveaudio_dir.grid(row=5, column=2)

        self.butt_saveaudio_changedir = ttk.Button(self.frame_settings, text="...", width=3, command=self.change_saveaudio_dir)
        self.butt_saveaudio_changedir.grid(row=5, column=3)

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
            img_tk = self.__cv_to_tk(img)

            self.label_video.config(image=img_tk)
            self.label_video.image = img_tk

            self.after(150, self.update_video) # repeat function after 1 millisecond

    ###################################################################################################################################################################
    # Image Scanning Related Methods                                                                                                                                  #
    #                                                                                                                                                                 #                  
    # A lot of callbacks and threads are used here. Basically, the scan function gathers all the initial data before calling on a thread to                           #  
    # preprocess the image. This method stores the scanned image and text to an immutable object (list) so the rest of the program can still                          #
    # access the same data. A separate callback then checks this immutable object every second to see if the preprocessing has finished. If it has                    #  
    # It carries out any file operations it needs to and then calls on the tts method in classes.py to vocalise the text. This happens in a separate process          #  
    # as well, so the time that the TTS should take to finish is calculated and Tkinter is told to wait that amount of time before re-enabling the buttons            #  
    #                                                                                                                                                                 #  
    # All of this happens because any blocking functions would break the GUI and cause it to not respond. Therefore, long winded operations need to occur             #  
    # in a separate process or thread.                                                                                                                                #
    ###################################################################################################################################################################
             
    def scan(self, img):
        '''
        called when the user presses the 'scan image' button
        '''
        # deactivate buttons
        self.butt_scan.state(['disabled'])
        self.butt_import.state(['disabled'])
        
        self.stop_video()

        preprocess = self.var_preprocess.get()
        showimg = self.var_showimg.get()
        saveimg = self.var_saveimg.get()
        savetxt = self.var_savetxt.get()

        self.img_result_var = [None, None, False] # [image, text, finished:boolean], the finished value is used to check if the preprocessing has finished
        preprocess_thread = threading.Thread(target=self.scan_thread_callback, args=(img, preprocess, self.img_result_var))
        preprocess_thread.start()

        self.scan_processed_img_callback(showimg, saveimg, savetxt)
    
    def scan_thread_callback(self, img, preprocess, result_var:list):
        '''
        Processes the image with Tesseract and OpenCV in a separate thread
        '''
        processed_img, txt = self.ocr.scan_image(img, preprocess)
        result_var[0] = processed_img
        result_var[1] = txt
        result_var[2] = True

    def scan_processed_img_callback(self, showimg, saveimg, savetxt):
        '''
        Carries out file I/O and tts operations when the captured image has been preprocessed
        '''
        if not self.img_result_var[2]:
            self.after(100, self.scan_processed_img_callback, showimg, saveimg, savetxt)
            return

        processed_img = self.img_result_var[0]
        txt = self.img_result_var[1]

        if showimg:
            self.display_image(processed_img)

        # save the image if the user specified to do so
        if saveimg:
            filename = simpledialog.askstring('Image Name', 'Enter image file name')
            cv2.imwrite(f'{self.saveimg_dir.get()}/{filename}.jpg', processed_img)

        # save the text if the user specified to do so
        if savetxt:
            filename = simpledialog.askstring('Text File Name', 'Enter text file name')
            with open(f'{self.savetxt_dir.get()}/{filename}.jpg', 'w') as f:
                f.write(txt)

        self.img_result_var = [None, None, False]

        tts_time = int((len(txt.split())/self.ocr.tts_rate)*60000) + 3500 # calculate how long the TTS should take in milliseconds
        self.ocr.tts(txt)
        
        self.after(tts_time, self.scan_finished) # wait the amount of time the TTS should take to reactive buttons
        
    def scan_finished(self):
        self.start_video()

        # reactivate buttons
        self.butt_scan.state(['!disabled'])
        self.butt_import.state(['!disabled'])

    #####################################################

    def import_image(self):
        '''
        Import an image and scan it
        '''
        filedir = filedialog.askopenfilename(filetypes=[('JPEG Image', '.jpg'), ('PNG Image', '.png')])
        img = cv2.imread(filedir)
        self.scan(img)

    def display_image(self, cv_img, msg='Preprocessed Image'):
        '''
        Displays an image to the user in a seperate window. 

        This is used to show a preprocessed image if the user selects to do so
        '''
        img_tk = self.__cv_to_tk(cv_img)
        window = tk.Toplevel()
        window.title(msg)
        label_img = tk.Label(window, image=img_tk)
        label_img.image = img_tk
        label_img.pack()
    
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

    def __cv_to_tk(self, cv_img):
        '''
        converts an opencv image object to a tkinter image object
        '''
        img_arr = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_arr)
        img_tk = ImageTk.PhotoImage(img_pil)

        return img_tk

if __name__ == '__main__':
    app = Interface()
    app.mainloop()