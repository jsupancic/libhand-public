#!/usr/bin/python
import numpy as np
import sympy as sp
import random
from visual import *
from transform import *
from primitives import *

class Bone:
    def __init__(self,length,color,name):
        self.length = length
        self.color = color
        self.parts = []
        self.bend = float(0)
        self.side = float(0)
        self.arrow = None
        self.name = name
        pass
    
    def bend_mat(self):
        bend = math.radians(self.bend)
        bend = bend_mat_sym().subs({sp.symbols('bend') : bend})
        return sp2np(bend)
    
    def side_mat(self):
        side = float(math.radians(float(self.side)))
        side =  side_mat_sym().subs({sp.symbols('side') : side})
        return sp2np(side)

    def draw_fast(self,T,scale_in,do_draw):
        T = T.dot(self.side_mat())
        T = T.dot(self.bend_mat())

        p1 = T.dot(np.array([[0],[0],[0],[1]]))[0:3]

        TM = trans_mat_sym().subs({
            sp.symbols('tx') : self.length  * scale_in,
            sp.symbols('ty') : 0,
            sp.symbols('tz') : 0})
        T = T.dot(sp2np(TM))

        p2 = T.dot(np.array([[0],[0],[0],[1]]))[0:3]

        a = p2 - p1
        
        # draw self
        if do_draw:
            print("drawing part: {0} at {1} -- {2}",self.name,p1,p2)
            if self.arrow and self.arrow in scene.objects:
                self.arrow.position = p1
                self.arrow.pos = p1
                self.arrow.axis = a            
            else:
                self.arrow = arrow(pos=p1,axis=a,color=self.color,shaftwidth=2,fixedwidth=True)
        
        # recurse
        pts = {self.name : (p1,p2,T)}
        for i in range(0,len(self.parts)):
            part = self.parts[i]
            pts.update(part.draw_fast(T,scale_in,do_draw))

        return pts
    
    def draw(self,T,symbol_defs):
        #if type(T) is not sp.matrices.dense.MutableDenseMatrix:
        #T = T.as_mutable().simplify()
        T = T * (side_mat_sym().subs({sp.symbols('side') : sp.symbols(self.name + "_side")}))
        T = T * (bend_mat_sym().subs({sp.symbols('bend') : sp.symbols(self.name + "_bend")}))

        p1 = T * sp.Matrix([[0],[0],[0],[1]])
        T1 = T
        p1 = sp2np(p1.subs(symbol_defs).evalf()).flatten()[0:3]

        T = T * trans_mat_sym().subs({
            sp.symbols('tx') : sp.symbols(self.name + '_length') * sp.symbols('root_scale'),
            sp.symbols('ty') : 0,
            sp.symbols('tz') : 0})

        p2 = T * sp.Matrix([[0],[0],[0],[1]])
        fn = T * sp.Matrix([[sp.symbols('local_x')],[sp.symbols('local_y')],[sp.symbols('local_z')],[1]])
        p2 = sp2np(p2.subs(symbol_defs).evalf()).flatten()[0:3]

        a = p2 - p1
        
        # draw self
        print("drawing part: {0} at {1} -- {2}",self.name,p1,p2)
        if self.arrow:
            self.arrow.position = p1
            self.arrow.pos = p1
            self.arrow.axis = a            
        else:
            self.arrow = arrow(pos=p1,axis=a,color=self.color,shaftwidth=2,fixedwidth=True)
        
        # recurse
        pt_funcs = {self.name : fn}
        transforms = {self.name : T1}
        for i in range(0,len(self.parts)):
            part = self.parts[i]
            ik_fns, sub_transforms = part.draw(T,symbol_defs)
            pt_funcs.update(ik_fns)
            transforms.update(sub_transforms)

        #if "prox" in self.name:
        #    code.interact(local=locals())
            
        return pt_funcs, transforms

    def get_bones(self):
        bones = [self]

        for part in self.parts:
            bones = bones + part.get_bones()
        
        return bones
    
    def get_syms(self):
        syms =  {
            sp.symbols(self.name + "_side") : math.radians(self.side),
            sp.symbols(self.name + "_bend") : math.radians(self.bend),
            sp.symbols(self.name + "_length") : self.length,
            sp.symbols('local_x') : 0,
            sp.symbols('local_y') : 0,
            sp.symbols('local_z') : 0}
        for i in range(0,len(self.parts)):
            syms.update(self.parts[i].get_syms())
        return syms

    def set_syms(self,syms):
        if self.name + "_side" in syms:
            self.side = math.degrees(syms[self.name + "_side"])
        else:
            assert False
        if self.name + "_bend" in syms:
            self.bend = math.degrees(syms[self.name + "_bend"])
        else:
            assert False
        if self.name + "_length" in syms:
            self.length = syms[self.name + "_length"]
        else:
            assert False
        for i in range(0,len(self.parts)):
            self.parts[i].set_syms(syms)
    
    def find(self,arrow):
        if (self.arrow is arrow) or (self.name == arrow):
            return self
        else:
            for i in range(0,len(self.parts)):
                part = self.parts[i]
                found = part.find(arrow)
                if not found is None:
                    return found
        return None

def bone_chain(lengths,color,color_inc,names,sides,bend):
    #print names
    #print lengths
    #print sides
    b = Bone(lengths.pop(0),color,names.pop(0))
    b.side = sides.pop(0)
    b.bend = bend
    if len(lengths) > 0:
        b.parts.append(bone_chain(lengths,color+color_inc,color_inc,names,sides,bend))
    return b
    
class Hand:
    def __init__(self):
        self.faces = []
        self.root_x = 0
        self.root_y = 0
        self.root_z = 0
        self.root_scale = 1
        self.root_obj = None
        self.name = 'root'
        self.color = (1,1,1)
        
        BASE_ARM_LENGTH = 30
        self.root = self.hind_arm = Bone(BASE_ARM_LENGTH,(255/255.0,192/255.0,192/255.),'hind_arm')
        fore_arm = Bone(BASE_ARM_LENGTH,(0,255/255.,255/255.),'fore_arm')
        self.hind_arm.parts.append(fore_arm)

        BASE_FINGER_LENGTH = 5
        finger_lengths = [2*BASE_FINGER_LENGTH,BASE_FINGER_LENGTH,BASE_FINGER_LENGTH,BASE_FINGER_LENGTH]        
        finger_bones   = ['metacarpal','prox','inter','dist']
        
        # fingers - pinky
        sides = [50,-50,0,0]
        finger = bone_chain(finger_lengths[:],
                            np.array([1,0,0]),np.array([0,1/4.0,0]),
                            ['pinky_' + p for p in finger_bones],sides[:],9.5)
        fore_arm.parts.append(finger)
        # fingers - ring
        sides = [25,-25,0,0]
        finger = bone_chain(finger_lengths[:],
                            np.array([0,1,0]),np.array([1/4.0,0,0]),
                            ['ring_' + p for p in finger_bones],sides[:],9.5)        
        fore_arm.parts.append(finger)        
        # fingers - middle
        sides = [0,0,0,0]
        finger = bone_chain(finger_lengths[:],
                            np.array([0,0,1]),np.array([1/4.0,0,0]),
                            ['middle_' + p for p in finger_bones],sides[:],7.5)
        fore_arm.parts.append(finger)        
        # fingers - index
        sides = [-20,20,0,0]
        finger = bone_chain(finger_lengths[:],
                            np.array([1,1,0]),np.array([0,0,1/4.0]),
                            ['index_' + p for p in finger_bones],sides[:],7.5)
        fore_arm.parts.append(finger)        
        # fingers - thumb
        del finger_lengths[-1]
        del finger_bones[-1]
        sides = [-30,+30,0]
        finger_lengths[0] = 2*BASE_FINGER_LENGTH
        finger = bone_chain(finger_lengths[:],
                            np.array([0,1,1]),np.array([1/4.0,0,0]),
                            ['thumb_' + p for p in finger_bones],sides[:],12.5)
        fore_arm.parts.append(finger)        

        #self.load_mesh(self.draw_fast(False))
        self.side = 'left'
        self.null_solution = self.get_syms()

    def toggle_lr(self):
        def mirrored_joint(name,param):
            if any(bone in name for bone in ['meta','prox','inter','dist']):
                if any(bone in name for bone in ['pinky','ring','middle','index','thumb']):
                    return -param
            return param

        # mirror null
        self.null_solution = {n:mirrored_joint(n,p) for n,p in self.null_solution.iteritems()}
        all_symbols = self.get_syms()
        all_symbols = {n:mirrored_joint(n,p) for n,p in all_symbols.iteritems()}

        # mirror current values
        self.set_syms(all_symbols)

        # mirror side
        if self.side == 'left':
            self.side = 'right'
        else:
            self.side = 'left'

    def get_null_solution(self):
        return self.null_solution
    
    def find(self,obj):
        if (self.root_obj is obj) or (self.name == obj):
            return self
        else:
            return self.root.find(obj)
    
    def draw_base(self):
        xyz = (self.root_x,self.root_y,self.root_z)
        if self.root_obj == None:
            self.root_obj = box(pos=xyz,color=self.color,length=5,width=5,height=5)
        else:
            self.root_obj.pos = xyz
    
    def draw_fast(self,do_draw=True):
        T = np.array([[1,0,0,self.root_x],
                      [0,1,0,self.root_y],
                      [0,0,1,self.root_z],
                      [0,0,0,1]])
        if do_draw:
            self.draw_base()        
        pts = {'root' : [self.root_x, self.root_y, self.root_z, 1]}
        pts.update(self.root.draw_fast(T,self.root_scale,do_draw))
        return pts

    def T0(self):
        symbol_defs = {sp.symbols('root_x'):self.root_x,
                       sp.symbols('root_y'):self.root_y,
                       sp.symbols('root_z'):self.root_z,
                       sp.symbols('root_scale'):self.root_scale}
        symbol_defs.update(self.root.get_syms())
        T = sp.Matrix([
            [1,0,0,sp.symbols('root_x')],
            [0,1,0,sp.symbols('root_y')],
            [0,0,1,sp.symbols('root_z')],
            [0,0,0,1]])
        return T, symbol_defs
    
    def draw(self):
        self.draw_base()
        T, symbol_defs = self.T0()
        root_fn = {'root' : sp.Matrix([[sp.symbols('root_x')],[sp.symbols('root_y')],[sp.symbols('root_z')],[1]])}
        ik_fns, transforms = self.hind_arm.draw(T,symbol_defs)
        transforms.update({'root':T})
        ik_fns.update(root_fn)

        self.ik_fns = ik_fns
        self.transforms = transforms
        
        return ik_fns

    def load_mesh(self,pts):
        # set a null transform
        #T = scale_matrix_sym().subs({'sx':-10,'sy':10,'sz':10})
        scale = 7.4
        tx = 60
        ty = -3
        tz = -13
        T = sp.Matrix([
            [-7.2, 0,    0,  tx],
            [0,   0,   -scale, ty],
            [0,   scale,  0,  tz],
            [0,   0,       0,  1]])
        scene.center = (tx,ty,tz)
        
        # load the mesh
        self.vertexes = []
        self.faces = []
        with open('meshes/hand.obj') as f:
            for line in f:
                #print('line = ' + line)
                first, rest = line.split(' ',1)
                if first == 'v':                    
                    x, y, z = rest.split(' ')
                    xyz = (float(x),float(y),float(z),1.0)
                    xyz = T*sp.Matrix(xyz)

                    try:
                        min_dist, best_bone = self.closest_bone(pts,xyz[0:3])
                        bne = self.find(best_bone)                    
                        #sphere(pos=(xyz[0],xyz[1],xyz[2]),radius=1,color=bne.color)
                    except:
                        code.interact(local=locals())
                        
                    # compute position in bone space...
                    # wrld = T * lcl
                    # lcl = T-1 * wrld
                    T_NULL = pts[best_bone][2]
                    lcl = np.linalg.inv(T_NULL).dot(sp2np(xyz)).astype(float)
                    #xyzw = T_bone * lcl
                    #if 'dist' in best_bone:
                    #    code.interact(local=locals())
                    
                    #self.vertexes.append(xyz)
                    self.vertexes.append([lcl,best_bone])
                elif first == 'f':
                    i1,i2,i3 = rest.split(' ')
                    i1,i2,i3 = [int(d.split('/')[0])-1 for d in [i1,i2,i3]]
                    #print("indexes = " + str((i1,i2,i3)))
                    #print('vertex size = ' + str(len(vertexes)))
                    #face_vtxs = [vertexes[i] for i in [i1,i2,i3]]
                    #faces.append(Face(*face_vtxs))
                    self.faces.append([i1,i2,i3])

        print("loaded {0} vertexes and {1} faces".format(len(self.vertexes),len(self.faces)))

    def draw_mesh(self):
        pts = self.draw_fast(False)
        for face in self.faces:
            lcl_v1 = self.vertexes[face[0]][0]
            bne_v1 = self.vertexes[face[0]][1]
            trn_v1 = pts[bne_v1][2]
            lcl_v2 = self.vertexes[face[1]][0]
            bne_v2 = self.vertexes[face[1]][1]
            trn_v2 = pts[bne_v2][2]
            lcl_v3 = self.vertexes[face[2]][0]
            bne_v3 = self.vertexes[face[2]][1]
            trn_v3 = pts[bne_v3][2]

            wrld_coords = [trn_v1.dot(lcl_v1), trn_v2.dot(lcl_v2), trn_v3.dot(lcl_v3)]
            #code.interact(local=locals())            
            f = Face(*[sp.Matrix(v) for v in wrld_coords])
            f.color = (.75,1,.75)
            f.draw({})            

    def get_bones(self):
        return self.root.get_bones()

    def dist_pt_2_bone(self,p2,p1,face_pos):
        # get the info[
        face_pos = np.array(face_pos).astype(float)
        
        # compute the distances
        n = p2 - p1
        n_len = np.linalg.norm(n)
        n = n/n_len
        try:
            t_face = n.T.dot((face_pos - p1.T).T)
            t_end  = n.T.dot(p2 - p1)
        except:
            code.interact(local=locals())

        # point to line case
        dist = float('inf')
        dist1 = np.linalg.norm(p1.T - face_pos)
        dist2 = np.linalg.norm(p2.T - face_pos)
        #code.interact(local=locals())
        print('dist1 = {0} dist2 = {1}'.format(dist1,dist2))
        if 0 < t_face and t_face < n_len:
            #code.interact(local=locals())
            min_pt = (t_face*n + p1).T.astype(float)
            dist = np.linalg.norm(min_pt - face_pos)
            assert(dist < dist1 and dist < dist2)
        else:
            dist = min(dist1,dist2)

        return dist

    def closest_bone(self,pts,face_pos):
        min_dist = float('inf')
        best_bone = None
        for bone,pt in pts.iteritems():
            if bone == "root":
                continue
            
            p1 = pt[0]
            p2 = pt[1]
            dist = self.dist_pt_2_bone(p1,p2,face_pos)

            if dist < min_dist:
                min_dist = dist
                best_bone = bone

        return min_dist, best_bone
    
    def color_mesh(self,faces,pts):
        T, symbol_defs = self.T0()
        T = sp2np(T.subs(symbol_defs))
        
        for face in faces:
            # find the cloest bone
            face_pos = face.barycenter()[0:3]
            min_dist, best_bone = self.closest_bone(pts,face_pos)

            # mark the result
            bne = self.find(best_bone)
            color = bne.color
            #print("bone match = {0} dist = {1} color = {2} name = {3}",best_bone,min_dist,color,bne.name)
            face.color = color            
                
    def get_syms(self):
        all_symbols = self.root.get_syms()
        all_symbols.update({'root_x' : self.root_x, 'root_y' : self.root_y, 'root_z' : self.root_z, 'root_scale' : self.root_scale})
        all_symbols = {str(key) : float(value) for key,value in all_symbols.iteritems()}
        return all_symbols

    def set_syms(self,solution):
        self.root_x = solution['root_x']
        self.root_y = solution['root_y']
        self.root_z = solution['root_z']
        self.root_scale = solution['root_scale']
        self.root.set_syms(solution)

    def perturb(self):
        pass

    def randomize(self):
        syms = self.get_syms()
        for sym_var in syms.keys():
            if 'bend' in sym_var:
                syms[sym_var] = math.radians(70*random.random())
            elif 'side' in sym_var and 'thumb' in sym_var:
                syms[sym_var] = math.radians(40*random.random()-20)
        self.set_syms(syms)
        
        return self

class HandDemo:
    def on_keyboard(self):
        k = scene.kb.getkey()
        if k == 'p':
            # perturb
            print "perturbing"

            syms = self.hand.get_syms()
            #perturb_var = random.choice([v for v in syms.keys() if 'bend' in v])
            delta = random.uniform(-1, +1)           
            #syms[perturb_var] = syms[perturb_var] + delta
            for sym in syms:
                if ('bend' in sym) and (not 'thumb' in sym):
                    syms[sym] = syms[sym] 
                elif 'thumb' in sym:
                    #syms[sym] = syms[
                    pass
            self.hand.set_syms(syms)
            
            self.draw()
            #print("{0}: {1} => {2}".format(perturb_var,syms[perturb_var]-delta,syms[perturb_var]))

    def draw(self):
        # clear the scene
        [scene.remove_renderable(obj) for obj in scene.objects]

        Compass().draw()
        #hand.draw()
        pts = self.hand.draw_fast(False)
        #[scene.remove_renderable(obj) for obj in scene.objects]
    
        # draw the hand's mesh
        self.hand.draw_mesh()
        scene.center = pts['thumb_metacarpal'][0]
        #hand.color_mesh(faces,pts)        

        
    def main(self):
        scene.background = (1,1,1)
        scene.width = 640
        scene.height = 640

        # make a hand
        self.hand = Hand()

        # draw first frame
        self.draw()

        while True:
            rate(120)

            # keyboard
            if scene.kb.keys:
                self.on_keyboard()        
        
def main():
    hd = HandDemo()
    hd.main()

if __name__ == '__main__':
    main()
