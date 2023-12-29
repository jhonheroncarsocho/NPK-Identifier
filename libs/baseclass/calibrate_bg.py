from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from graph_generator import GraphGenerator
import numpy as np
import pandas as pd

import RPi.GPIO as GPIO


Builder.load_file('./libs/kv/calibrate_bg.kv')


class CalibrateBG(Screen):
    figure_wgt2 = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_enter(self, *args):
        # set the lights to high
        GPIO.output(12, GPIO.LOW)

        # access the NIR
        self.spec = MDApp.get_running_app().spec

        mygraph = GraphGenerator()
        
        self.figure_wgt2.figure = mygraph.fig
        self.figure_wgt2.axes = mygraph.ax1

        # get initial spectral data
        self.figure_wgt2.xmin= np.min(self.spec.wavelengths())
        self.figure_wgt2.xmax = np.max(self.spec.wavelengths())
        self.figure_wgt2.ymin=np.min(self.spec.intensities(False,True))
        self.figure_wgt2.ymax = np.max(self.spec.intensities(False,True))
        self.figure_wgt2.line1=mygraph.line1
        self.home()
        self.figure_wgt2.home()

        
       
        Clock.schedule_interval(self.update_graph,.1)

    def set_touch_mode(self,mode):
        self.figure_wgt2.touch_mode=mode

    def home(self):
        self.figure_wgt2.home()
        
    def update_graph(self,_):
        xdata= self.spec.wavelengths()
        intensities = self.spec.intensities(False,True)
        self.figure_wgt2.line1.set_data(xdata,intensities)
        self.figure_wgt2.ymax = np.max(intensities)
        self.figure_wgt2.ymin = np.min(intensities)
        self.figure_wgt2.xmax = np.max(xdata)
        self.figure_wgt2.xmin = np.min(xdata)
        self.home()
        self.figure_wgt2.figure.canvas.draw_idle()
        self.figure_wgt2.figure.canvas.flush_events() 
    
    def activate_capture(self):
        self.ids['capture_bg'].disabled = not self.ids['capture_bg'].disabled
        self.ids['next_bg'].disabled = not self.ids['next_bg'].disabled
        self.ids['rescan_bg'].disabled = not self.ids['rescan_bg'].disabled
    
    def activate_rescan(self):
        self.ids['rescan_bg'].disabled = not self.ids['rescan_bg'].disabled
        self.ids['next_bg'].disabled = not self.ids['next_bg'].disabled
        self.ids['capture_bg'].disabled = not self.ids['capture_bg'].disabled

    def disable_clock(self):
        Clock.unschedule(self.update_graph)
    
    def on_leave(self, *args):
        self.ids['next_bg'].disabled = not self.ids['next_bg'].disabled
        self.ids['capture_bg'].disabled = not self.ids['capture_bg'].disabled
        self.ids['rescan_bg'].disabled = not self.ids['rescan_bg'].disabled
        return super().on_leave(*args)