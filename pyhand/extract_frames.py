from oni_video import *
import scipy
import os
import cv2
import sys

def main():
    vid_name = sys.argv[1]
    path = 'frames/{0}/'.format(os.path.basename(vid_name))
    if not os.path.exists(path):
        os.makedirs(path)
    max_frame = get_number_of_frames(vid_name)
    frame = 0
    rgbs, depths = load_video(vid_name)
    while 0 <= frame and frame < max_frame:
        print("frame {0} of {1}".format(frame,max_frame))
        depth = depths[frame]
        rgb = rgbs[frame]
        print("saving {0}/{1}_color.png".format(path,frame))
        cv2.imwrite("{0}/{1}_color.png".format(path,frame),rgb)
        print("saving {0}/{1}_depth.png".format(path,frame))
        cv2.imwrite("{0}/{1}_depth.png".format(path,frame),depth)
        frame = frame + 20

if __name__ == "__main__":
    main()
