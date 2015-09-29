#!/usr/bin/python
import numpy as np
import code
from primesense import openni2

def get_number_of_frames(vid_name):
    openni2.initialize('/usr/lib64/')
    dev = openni2.Device.open_file(vid_name)
    # get and start the streams
    depth_stream = dev.create_depth_stream()
    # seek
    pbs = openni2.PlaybackSupport(dev)
    return pbs.get_number_of_frames(depth_stream)

def load_video(vid_name):
    depths = []
    rgbs = []
    
    # get the oni frame
    openni2.initialize('/usr/lib64/')
    dev = openni2.Device.open_file(vid_name)
    print (dev.get_device_info())
    # get and start the streams
    rgb_stream = dev.create_color_stream()
    depth_stream = dev.create_depth_stream()
    depth_stream.start()
    rgb_stream.start()
    # seek
    pbs = openni2.PlaybackSupport(dev)
    n_frames = pbs.get_number_of_frames(depth_stream)
    print("total frames = " + str(n_frames))
    pbs.set_repeat_enabled(True)
    pbs.set_speed(0)

    # read the frame
    for i in range(0,n_frames):
        print("Depth {0} of {1}".format(i,n_frames))
        frame = depth_stream.read_frame()
        frame_data = frame.get_buffer_as_uint16()
        #depth_stream.stop()
        # to numpy!
        depth = np.array(frame_data)
        depth = np.reshape(depth,[frame.height,frame.width])
        depths.append(depth)

        print("RGB {0} of {1}".format(i,n_frames))
        rgb = rgb_stream.read_frame()
        rgb = np.array(rgb.get_buffer_as_uint8())
        rgb = np.reshape(rgb,[frame.height,frame.width,3])
        rgbs.append(rgb)
                
    #code.interact(local=locals())
    return depths, rgbs
    

def get_frame(vid_name,frame_id):
    # get the oni frame
    openni2.initialize('/usr/lib64/')
    dev = openni2.Device.open_file(vid_name)
    print (dev.get_device_info())
    # get and start the streams
    rgb_stream = dev.create_color_stream()
    depth_stream = dev.create_depth_stream()
    depth_stream.start()
    rgb_stream.start()
    # seek
    pbs = openni2.PlaybackSupport(dev)
    print("total frames = " + str(pbs.get_number_of_frames(depth_stream)))
    pbs.set_repeat_enabled(True)
    pbs.set_speed(0)

    # read the frame
    for i in range(0,frame_id+1):
        frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    depth_stream.stop()
    # to numpy!
    depth = np.array(frame_data)
    depth = np.reshape(depth,[frame.height,frame.width])

    # read the rgb
    for i in range(0,frame_id+1):
        rgb = rgb_stream.read_frame()
    rgb = np.array(rgb.get_buffer_as_uint8())
    rgb = np.reshape(rgb,[frame.height,frame.width,3])
        
    #code.interact(local=locals())
    return depth, rgb
