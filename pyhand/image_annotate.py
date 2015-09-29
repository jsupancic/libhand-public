#!/usr/bin/python2.7
from oni_video import *
import Tkinter

def annotate_frame(vid_name,frame):
    depth = get_frame(vid_name,frame)

def main():
    vid_name = '/home/jsupanci/data/sargis2.oni'
    max_frame = get_number_of_frames(vid_name)
    frame = 0
    while 0 <= frame and frame < max_frame:
        print("frame {0} of {1}".format(frame,max_frame))
        frame = frame + 20
    
if __name__ == "__main__":
    main()

