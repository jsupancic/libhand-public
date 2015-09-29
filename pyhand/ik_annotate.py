#!/usr/bin/python2.7
from visual import * #import the visual module
import code
import numpy as np
from scaledimage import *
import itertools
import math
import sympy as sp
import random
from sympy.utilities.codegen import codegen
#from autodiff import function, gradient
import iksolver
import os
from oni_video import *
import cv2
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('wxAgg')
from multiprocessing import Process, Queue
from hand import *

class ImShower:
    def worker(self):
        im = None
        cv2.waitKey(15)        
        while True:
            #print "work!"
            if not self.q.empty():
                im = self.q.get()
            if im is not None:
                cv2.imshow("RGB",im)
                cv2.waitKey(15)        
    
    def __init__(self):
        self.q = Queue()
        self.p = Process(target=self.worker)
        self.p.start()

    def kill(self):
        self.p.terminate()
        
    def __del__(self):
        self.p.terminate()
        
    def show(self,im):
        self.q.put(im)

def clamp(mi,f,mx):
    return max(mi,min(mx,f))

def toWorld(i,j,depth ):
    return (j - depth.shape[1]/2,-i + depth.shape[0]/2, -clamp(0,float(depth[i,j]),2000)/5.0)

def draw_frame(depth):
    # now visulize the depth points?
    W = depth.shape[1]
    H = depth.shape[0]
    pts = [toWorld(i[0],i[1],depth) for i in itertools.product(range(H),range(W)) if 2000 > depth[i[0],i[1]] > 0 ]
    colors = [(float(depth[i[0],i[1]])/2000,0,1) for i in itertools.product(range(H),range(W)) if 2000 > depth[i[0],i[1]] > 0]
    pts = points(pos=pts,size=5,color=colors,size_units="world",shape="square")
    #rod = cylinder(pos=(0,2,1), axis=(5,0,0), radius=1)
    return pts
    
# export PYTHONPATH=/home/jsupanci/workspace/pyautodiff/
class IkAnnotator:
    def draw_annotation(self,xyz,selection):
        # if updating old annotation
        if selection in self.annotations:
            obj = self.annotations[selection]['obj']
            obj.position = xyz
            obj.pos = xyz                    
            #code.interact(local=locals())
            # otherwise, add new annotation
        else:
            color = self.hand.find(selection).color
            obj = sphere(pos=xyz,radius=2.5,color=color,material=materials.unshaded)        
            
        # update the annotation position :-)
        self.annotations[selection] = { 'pos' : xyz,
                                             'color' : obj.color,
                                             'obj' : obj}
        print self.annotations

    def onPtPlace(self,xyz):
        print("point selected!")
        if not self.selection is None:            
            scene.center = xyz
            self.draw_annotation(xyz,self.selection)        
        
    def onMouse(self,ev):
        print('click!' + str(ev.pick) + " " + str(ev.pickpos))
        if (type(ev.pick) is visual.vis.primitives.arrow) or (type(ev.pick) is visual.vis.primitives.box):            
            self.selection = self.hand.find(ev.pick).name
            if self.selection is None:
                print("Couldn't find selection!")
                return
            self.selected_color = ev.pick.color
            # set self.selection
            print('self.selection = ' + self.selection)
        elif ev.pick is self.pts:
            # add annotation
            self.onPtPlace(ev.pickpos)
            
            # re-construct the scene...
            print self.annotations            
        elif ev.pick is None:
            # ev.ray and ev.camera define the ray: { camera + t*ray for t>0}.
            # self.pts.pos define the points
            # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Vector_formulation
            a = ev.camera
            n = ev.ray
            ps = self.pts.pos
            # distance along line
            n = n / np.linalg.norm(n)
            projs = ((ps - a).dot(n) * np.array(n)[None].T).T # project ps onto n
            dist_along = np.sum(np.abs(projs)**2,axis=-1)**(1./2)
            # sort by distance along the line
            ps = ps[np.argsort(dist_along)]
            # distance to line
            dists = (a - ps) - ((a - ps).dot(n) * np.array(n)[None].T).T
            dists = np.sum(np.abs(dists)**2,axis=-1)**(1./2)
            match_idxs = np.where(dists < 5)[0]

            if len(match_idxs > 0):
                match = ps[match_idxs[0],:]
                self.onPtPlace(match)
            #code.interact(local=locals())            

    def compile_ik_solver(self):
        params = self.hand.get_syms()
        derivs = {}
        # generate evaluation functions
        for pt_name, pt_function in self.ik_fns.iteritems():
            # print the function
            print("{0} {1}".format(pt_name,pt_function))
            # generate a routine
            codegen((pt_name,pt_function),'C',to_files=True,prefix='kinematics/'+pt_name,header=True,empty=True)

            # generate partial derivatives
            for param in params.keys():
                for i in range(0,4):
                    name = pt_name + "_" + param + '_' + str(i)
                    #code.interact(local=locals())
                    deriv = sp.diff(pt_function[i],param)
                    #code.interact(local=locals())
                    derivs[name] = deriv
                    codegen((name,deriv),'C',to_files=True,prefix='kinematics/'+name,header=True,empty=True)
        #
            
        # generate the function
        # double sq_diff(const string&name,Vec4d&target,map<string,double>&solution)
        with open('eval_ik.cpp','w') as f:
            for pt_name, pt_function in self.ik_fns.iteritems():
                f.write("#include \"kinematics/{0}.h\"\n".format(pt_name))
                f.write("#include \"kinematics/{0}.c\"\n".format(pt_name))

                for param in params.keys():
                    for i in range(0,4):                        
                        f.write("#include \"kinematics/{0}_{1}_{2}.h\"\n".format(pt_name,param,i))
                        f.write("#include \"kinematics/{0}_{1}_{2}.c\"\n".format(pt_name,param,i))

            # define the forward proejction function
            f.write("Vec4d joint_position(const string&name,map<string,double>&solution) {")
            for pt_name, pt_function in self.ik_fns.iteritems():
                f.write("if(name == \"{0}\") ".format(pt_name) + "{\n")
                f.write("Vec4d cur;\n")
                #code.interact(local=locals())
                arguments = ["solution.at(\"{0}\")".format(s) for s in pt_function.free_symbols]
                arguments.sort()
                arg_list = ','.join(arguments)
                f.write("{0}({1},{2});\n".format(pt_name,arg_list,"cur.values"))
                f.write("return cur;")
                f.write("}\n")
            f.write("throw std::runtime_error(\"bad name\");\n")
            f.write("}\n")

            # write the ik function caller
            f.write("double diff(const string&target,const string&param,int i,map<string,double>&solution) {")
            for target_name, pt_function in self.ik_fns.iteritems():
                for param_name in params:
                    for i in range(0,4):
                        fn_name = "{0}_{1}_{2}".format(target_name,param_name,i)
                        f.write("if(target == \"{0}\" && param == \"{1}\" && i == {2}) ".format(target_name,param_name,i) + "{\n")
                        #f.write("Vec4d cur;\n")
                        #code.interact(local=locals())
                        arguments = ["solution.at(\"{0}\")".format(s) for s in derivs[fn_name].free_symbols]
                        arguments.sort()
                        arg_list = ','.join(arguments)
                        f.write("return {0}({1});\n".format(fn_name,arg_list))
                        #f.write("return cur;")
                        f.write("}\n")

            f.write("throw std::runtime_error(\"bad name\");\n")
            f.write("}\n")
            
            # define the gradient function
        print '=====     IK SOLVER COMPILED      ======'

    def get_regularizer(self,var_name):        
        if "length" in var_name:
            if ('root' in var_name) or ('hind_arm' in var_name) or ('fore_arm' in var_name):
                return .95
            else:
                return 1.4
        elif "bend" in var_name:
            if ('root' in var_name) or ('hind_arm' in var_name) or ('fore_arm' in var_name):
                return 0
            else:
                return 500
        elif "side" in var_name:
            if ('root' in var_name) or ('hind_arm' in var_name) or ('fore_arm' in var_name):
                return 0
            elif ('thumb' in var_name):
                return 100
            else:
                return 800
        elif 'local' in var_name:
            return 1000000000000000
        else:
            return 0

    def ensure_ik_solver_ready(self):
        all_symbols = self.hand.get_syms()
        if self.iksolver == None:
            self.iksolver = iksolver.iksolver()            
            self.iksolver.set_grad_step_size(1e-3);
            self.iksolver.set_regularizers({key : self.get_regularizer(key) for key,value in all_symbols.iteritems()})
        
    def resolve_ik_c(self):
        print("++resolve_ik_c")
        # get current solution
        all_symbols = self.hand.get_syms()
        print all_symbols
        if 'root' in self.annotations:
            all_symbols['root_x'] = self.annotations['root']['pos'][0]
            all_symbols['root_y'] = self.annotations['root']['pos'][1]
            all_symbols['root_z'] = self.annotations['root']['pos'][2]
        
        self.ensure_ik_solver_ready()
        # find target positions
        note_positions = {name : [
            value['pos'][0],
            value['pos'][1],
            value['pos'][2],1] for name,value in self.annotations.iteritems()}
        print("note_positions = " + str(note_positions))
        
        # solve in C++ (VERY SLOW)
        self.iksolver.set_null_solution(self.hand.get_null_solution())
        solution = self.iksolver.solve(note_positions,all_symbols)
        self.ik_queue.put(solution)
        
    def receive_ik_c(self):
        # parse the solution
        solution = self.ik_queue.get()
        solution = {str(key) : float(value) for key,value in solution.iteritems()}
        print("solution = " + str(solution))
        
        # output the variables
        self.hand.set_syms(solution)
        #self.hand.draw()        
        self.hand.draw_fast()
        scene.center = self.hand.find('fore_arm').arrow.pos
        print("--resolve_ik_c " + str(self.frame_number))
    
    def notes_path(self):
        filename = 'annotation-database/' + os.path.basename(self.vid_name) + '/params_{0}.csv'.format(self.frame_number)
        return filename
    
    def save_notes(self):
        direc = 'annotation-database/' + os.path.basename(self.vid_name)
        if not os.path.exists(direc):
            os.makedirs(direc)

        with open(direc + '/params_{0}.csv'.format(self.frame_number),'w') as f:
            f.write(self.hand.side + '\n')
            for name, annotation in self.annotations.iteritems():
                pos = annotation['pos']
                f.write('{0},{1},{2},{3}\n'.format(name,pos[0],pos[1],pos[2]))

        print("SAVED FRAME ANNOTATIONS")

        # export the joint labels
        pts = self.hand.draw_fast()

        # save the joint positions.
        # code.interact(local=locals())
        with open(direc + '/points_{0}.csv'.format(self.frame_number),'w') as f:
            #code.interact(local=locals())
            for name, pos in pts.iteritems():                
                p1 = pos[0]
                p2 = pos[1]
                try:
                    f.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(name,float(p1[0]),float(p1[1]),float(p1[2]),float(p2[0]),float(p2[1]),float(p2[2])))
                except:
                    f.write('{0},{1},{2},{3}\n'.format(name,float(pos[0]),float(pos[1]),float(pos[2])))
                    #code.interact(local=locals())
                
        
    def load_notes(self):
        filename = self.notes_path()
        if not os.path.exists(filename):
            print("LOAD: file not found: " + filename)
            return

        with open(filename,'r') as f:
            for line in f:
                name,x,y,z = line.split(',')
                xyz = [float(x),float(y),float(z)]
                print("Loaded: " + name)
                self.draw_annotation(xyz,name)

        print("LOAD: SUCCESS")
        
    def onKb(self,key):
        if key == 'i':
            #self.resolve_ik()
            self.save_notes()
            #self.resolve_ik_c()
        elif key == 's':
            self.save_notes()
        elif key == 'l':
            self.load_notes()
        elif key == 'l' or key == 'r':            
            self.hand.toggle_lr()
            self.hand.draw_fast()
            
    def set_frame(self,vid_name,frame_number):
        self.vid_name = vid_name
        self.frame_number = frame_number        

    def __init__(self,vid_name,frame,D,RGB):
        self.Compile = False
        self.iksolver = None
        self.D = D
        self.RGB = RGB
        self.ik_queue = Queue()
        self.ik_process = None
        
        self.set_frame(vid_name,frame)
        
    def main(self):
        self.pts = draw_frame(self.D)
        #plt.imshow(self.RGB)
        #plt.show()
        self.hand = Hand()
        if self.Compile:
            self.ik_fns = self.hand.draw()
        self.hand.draw_fast()

        if self.Compile:
            self.compile_ik_solver()
        
        print(scene.objects)
        #code.interact(local=locals())
        #
        self.selection = None
        self.annotations = {}
        self.selected_color = None
        self.load_notes()
        while True:            
            #print "pumping event loop"
            # handle the IK worker thread
            if not self.ik_queue.empty():
                self.receive_ik_c()
            elif len(self.annotations) > 7 and ((self.ik_process is None) or (not self.ik_process.is_alive())):
                self.ik_process = Process(target=self.resolve_ik_c)
                self.ik_process.start()

            # handle UI    
            if scene.mouse.events:
                ev = scene.mouse.getclick()
                self.onMouse(ev)
            elif scene.kb.keys:
                k = scene.kb.getkey()
                if k == 'n' or k == 'p':
                    self.save_notes()
                    return k
                else:
                    self.onKb(k)
            else:
                #print("++Draw")
                rate(120)
                #print("--Draw")

def main():
    imshower = ImShower()
    scene.height=2*480
    scene.width =2*640
    scene.background=(1,1,1)
    stride = 40
    scene.show_rendertime = True
    vid_name = '/home/jsupanci/data/bailey2-sputnik2.oni'    
    depths, rgbs = load_video(vid_name)

    # find where to start annotation
    frame = 0    
    max_frame = get_number_of_frames(vid_name)    
    while frame < max_frame:
        imshower.show(rgbs[frame])
        ikAnnotator = IkAnnotator(vid_name,frame,depths[frame],rgbs[frame])
        if not os.path.exists(ikAnnotator.notes_path()):
            break
        else:
            frame = frame + stride
    
    #vid_name = '/home/jsupanci/data/greg.oni'
    while 0 <= frame and frame < max_frame:
        imshower.show(rgbs[frame])
        ikAnnotator = IkAnnotator(vid_name,frame,depths[frame],rgbs[frame])        
        label(pos=(0,50),text="frame {0} of {1}".format(frame,max_frame))
        k = ikAnnotator.main()        
        [scene.remove_renderable(obj) for obj in scene.objects] # clear the scene :-)
        if k == 'n':
            frame = frame + stride
        elif k == 'p':
            frame = frame - stride

    print "DONE"
    imshower.kill()
                
if __name__ == "__main__":
    main()
