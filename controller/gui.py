from tkinter import *
import tkinter as tk
from api import Traffects, Pin

background = "black"

root = Tk()
root.wm_title("Traffects GUI Controller")
root.bind("<Escape>", lambda event: event.widget.quit())

api = Traffects("COM4")

class Button(tk.Canvas):
    def __init__(self, activeColor, offColor, pin, width=200, height=200, cornerradius=100, padding=0):
        tk.Canvas.__init__(self, root, borderwidth=0, relief="flat", highlightthickness=0, bg=background)
        self.pin = pin
        self.activeColor = activeColor
        self.offColor = offColor
        self.background = background
        self.width = width
        self.height = height
        self.cornerradius = cornerradius
        self.padding = padding

        if cornerradius > width*.5:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > height*.5:
            print("Error: cornerradius is greater than height.")
            return None

        self.rad = cornerradius*2


        self.shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = (x1 - x0)
        height = (y1 - y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def shape(self):
        self.create_polygon((self.padding,self.height-self.cornerradius-self.padding,self.padding,self.cornerradius+self.padding,self.padding+self.cornerradius,self.padding,self.width-self.padding-self.cornerradius,self.padding,self.width-self.padding,self.cornerradius+self.padding,self.width-self.padding,self.height-self.cornerradius-self.padding,self.width-self.padding-self.cornerradius,self.height-self.padding,self.padding+self.cornerradius,self.height-self.padding), fill=self.get_color(), outline=self.get_color())
        self.create_arc((self.padding,self.padding+self.rad,self.padding+self.rad,self.padding), start=90, extent=90, fill=self.get_color(), outline=self.get_color())
        self.create_arc((self.width-self.padding-self.rad,self.padding,self.width-self.padding,self.padding+self.rad), start=0, extent=90, fill=self.get_color(), outline=self.get_color())
        self.create_arc((self.width-self.padding,self.height-self.rad-self.padding,self.width-self.padding-self.rad,self.height-self.padding), start=270, extent=90, fill=self.get_color(), outline=self.get_color())
        self.create_arc((self.padding,self.height-self.padding-self.rad,self.padding+self.rad,self.height-self.padding), start=180, extent=90, fill=self.get_color(), outline=self.get_color())

    def get_color(self):
        return self.activeColor if api.get(self.pin) else self.offColor

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.pin is not None:
            api.set(self.pin, not api.get(self.pin))
        self.shape()

canvas = Canvas(root, height=800, width=300, background=background)
canvas.pack()

button1 = Button(activeColor="#E84444", offColor="#851010", pin=Pin.RED)
button1.place(relx=.2, rely=.1)

button2 = Button(activeColor="#F09F19", offColor="#7c5008", pin=Pin.YELLOW)
button2.place(relx=.2, rely=.4)

button3 = Button(activeColor="#40AC7B", offColor="#20563d", pin=Pin.GREEN)
button3.place(relx=.2, rely=.7)

root.mainloop()
