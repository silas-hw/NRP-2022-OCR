import tkinter as tk
import tkinter.ttk as ttk

class Interface(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # call the init function of the inherited class

    def scan(self):
        pass

if __name__ == '__main__':
    app = Interface()
    app.mainloop()