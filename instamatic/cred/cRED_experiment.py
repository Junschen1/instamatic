import os
import datetime
import logging
from Tkinter import *
import numpy as np
import glob
import time
import ImgConversion
from TEMController import config

class cRED_experiment(object):
    def __init__(self, ctrl,expt,camtyp,t,path=None,log=None, flatfield=None):
        super(cRED_experiment,self).__init__()
        self.ctrl=ctrl
        self.path=path
        self.expt=expt
        self.logger=log
        self.camtyp=camtyp
        self.t=t
        self.flatfield = flatfield
        
    def report_status(self):
        self.image_binsize=self.ctrl.cam.default_binsize
        self.magnification=self.ctrl.magnification.get()
        self.image_spotsize=self.ctrl.spotsize
        
        self.diff_binsize=self.image_binsize
        self.diff_exposure=self.expt
        self.diff_brightness=self.ctrl.brightness
        self.diff_spotsize=self.image_spotsize
        print ("Output directory:\n{}".format(self.path))
        print "Imaging     : binsize = {}".format(self.image_binsize)
        print "              exposure = {}".format(self.expt)
        print "              magnification = {}".format(self.magnification)
        print "              spotsize = {}".format(self.image_spotsize)
        print "Diffraction : binsize = {}".format(self.diff_binsize)
        print "              exposure = {}".format(self.diff_exposure)
        print "              brightness = {}".format(self.diff_brightness)
        print "              spotsize = {}".format(self.diff_spotsize)        
        
    def start_collection(self):
        
        curdir = os.path.dirname(os.path.realpath(__file__))

        pxd=config.diffraction_pixeldimensions
        a0=self.ctrl.stageposition.a
        a=a0
        ind_set=[]
        ind=10001
        ind_set.append(ind)
        
        self.pathtiff=os.path.join(self.path,"tiff")
        self.pathsmv=os.path.join(self.path,"SMV")
        self.pathred=os.path.join(self.path,"RED")
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(self.pathtiff):
            os.makedirs(self.pathtiff)
        if not os.path.exists(self.pathsmv):
            os.makedirs(self.pathsmv)
        if not os.path.exists(self.pathred):
            os.makedirs(self.pathred)
        
        self.logger.info("Data recording started at: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.logger.info("Data saving path: {}".format(self.path))
        self.logger.info("Data collection exposure time: {} s".format(self.expt))
        camlen = int(self.ctrl.magnification.get())
        self.logger.info("Data collection camera length: {} mm".format(camlen))
        self.logger.info("Data collection spot size: {}".format(self.ctrl.spotsize))
        
        if self.camtyp == 1:
            while abs(a-a0)<0.5:
                a=self.ctrl.stageposition.a
                if abs(a-a0)>0.5:
                    break
            print "Data Recording started."
            self.startangle=a
            
            self.ctrl.cam.block()
            
            while not self.t.is_set():
                self.ctrl.getImage(self.expt,1,out=os.path.join(self.pathtiff,"{}.tiff".format(ind)),header_keys=None)
                ind=ind+1
                #self.root.update()
            self.ctrl.cam.unblock()
            self.endangle=self.ctrl.stageposition.a
            ind_set.append(ind)
            
        else:
            self.startangle=a
            camlen=300
            self.ctrl.cam.block()
            while not self.t.is_set():
                self.ctrl.getImage(self.expt,1,out=os.path.join(self.pathtiff,"{}.tiff".format(ind)),header_keys=None)
                print (self.ctrl.stageposition.a)
                print ("Generating random images...")
                time.sleep(self.expt)
                ind=ind+1
                #self.root.update()
            self.ctrl.cam.unblock()
            self.endangle=self.startangle+10
            ind_set.append(ind)
        
        self.ind=ind
        
        self.logger.info("Data collected from {} degree to {} degree.".format(self.startangle,self.endangle))
        
        listing=glob.glob(os.path.join(self.pathtiff,"*.tiff"))
        numfr=len(listing)
        osangle=(self.endangle-self.startangle)/numfr
        if osangle>0:
            self.logger.info("Oscillation angle: {}".format(osangle))
        else:
            self.logger.info("Oscillation angle: {}".format(-osangle))
        
        self.logger.info("Pixel size and actual camera length updated in SMV file headers for DIALS processing.")
        
        RA = config.camera_rotation_vs_stage_xy
        buf=ImgConversion.ImgConversion(expdir=self.path, flatfield=self.flatfield)
        pb=buf.TiffToIMG(self.pathtiff,self.pathsmv,camlen,self.startangle,osangle)
        pxs=pxd[camlen]
        buf.ED3DCreator(self.pathtiff,self.pathred,pxs,self.startangle,self.endangle,RA)
        buf.MRCCreator(self.pathtiff,self.pathred,header=buf.mrc_header,pb=pb)
        
        buf.XDSINPCreator(self.pathsmv,self.ind,self.startangle,20,0.8,pb,camlen,osangle,RA)
        self.logger.info("XDS INP file created as usual.")

        print "Data Collection and Conversion Done."