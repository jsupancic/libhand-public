import sympy as sp
import code
from transform import *
from visual import *
from ctypes import *
from sympy.utilities.codegen import codegen

class Plane:
    def __init__(self,p1,p2,p3):
        self.p = p1
        # calculate normal
        v1 = p2 - p1
        v2 = p3 - p1
        self.n = np.cross(v1,v2)

    def __init__(self,p,n):
        self.p = p
        self.n = n
        
    def intersect(self,ray,world_state):
        # unpack the plane
        p0 = self.p
        n = self.n
        # unpack the ray
        l0 = np.squeeze(ray[0])
        l = np.squeeze(ray[1])
        l = l/np.linalg.norm(l)

        #code.interact(local=locals())
        # #d = (p0 - l0).dot(n)/(l.dot(n))
        num = sp.Transpose(sp.Matrix(p0[0:3] - l0)) * (sp.Matrix(n[0:3]))
        den = sp.Transpose(sp.Matrix(l)) * (sp.Matrix(n[0:3]))
        num = num.as_explicit()
        den = den.as_explicit()
        d = num[0]/den[0]
        return d

class Circle:
    def __init__(self,p,n,r):
        self.radius = r
        self.p = p
        self.plane = Plane(p,n)

    def intersect(self,ray,world_state):
        # unpack the ray
        l0 = np.squeeze(ray[0])
        l = np.squeeze(ray[1])
        l = l/np.linalg.norm(l)

        # project ray to plane
        t = self.plane.intersect(ray,world_state)
        #code.interact(local=locals())
        #p = t * l + l0
        p = t * sp.Transpose(sp.Matrix(l)) + sp.Transpose(sp.Matrix(l0))

        #if np.linalg.norm(p - self.p) < self.radius:
        #    return t
        #else:
        #    return float('inf')
        #code.interact(local=locals())
        d = (p - sp.Transpose(sp.Matrix(self.p[0:3])))
        dt = sp.Transpose(d)
        d = sp.sqrt((d.as_mutable() * dt).as_explicit()[0])
        return Piecewise( (t , d < self.radius) , (float('inf'),True))

class Face:
    # l = f(v1,v2,...)
    # if mesh vertex v = w1*j1 + w2*j2 + ...
    # given dl/dv
    # find dl/dj_n
    # dl/dj_n = dl/dv * dv/dj_n
    # dv/dj_n = wn <- we backprop this.
    # vector form (total derivitive?, caps) partial lowercase
    # loss, l, is a function of all j_n
    # ++Dl/Dj_n = dl/dj_n + sum_{i\neqn} dl/dj_i * Dj_i/Dj_n
    # chain rule in multiple variables
    # dl/dj_n = \sum_l dl/dv_l * dv_l/dj_n
    # https://en.wikipedia.org/wiki/Chain_rule#Higher_dimensions
    # where l is number of vertexes
    
    def __init__(self,v1Fn, v2Fn, v3Fn):
        self.v1Fn = v1Fn
        self.v2Fn = v2Fn
        self.v3Fn = v3Fn
        self.color = (1,1,1)

    def barycenter(self):
        return (self.v1Fn + self.v2Fn + self.v3Fn)/3.0
        
    def draw(self,ctx):
        #faces(self.v1Fn(),self.v2Fn(),self.v3Fn())
        v1 = vector(self.v1Fn.subs(ctx)[0:3])
        v2 = vector(self.v2Fn.subs(ctx)[0:3])
        v3 = vector(self.v3Fn.subs(ctx)[0:3])
        self.f = faces(color=self.color)
        #code.interact(local=locals())
        self.f.append(pos=v1)
        self.f.append(pos=v2)
        self.f.append(pos=v3)
        self.f.make_twosided()
        self.f.make_normals()

    # https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    def intersect(self,ray,ctx):
        # unpack the ray
        if ray is None:
            o = sp.Matrix([symbols('ray_pos_x'),symbols('ray_pos_y'),symbols('ray_pos_z')])
            d = sp.Matrix([symbols('ray_dir_x'),symbols('ray_dir_y'),symbols('ray_dir_z')])
        else:
            o = sp.Matrix(ray[0])
            d = sp.Matrix(ray[1])
        
        # unpack the face
        v1 = sp.Matrix(self.v1Fn[0:3]).subs(ctx)
        v2 = sp.Matrix(self.v2Fn[0:3]).subs(ctx)
        v3 = sp.Matrix(self.v3Fn[0:3]).subs(ctx)
        e1 = v2 - v1
        e2 = v3 - v1

        # test if ray in triangle
        #code.interact(local=locals())
        p = d.cross(e2)
        det = e1.dot(p)
        eps = 1e-5
        #if det > -eps && det < eps:
        #    return 0
        inv_det = 1.0/det

        # check u side
        t = o - v1
        u = t.dot(p) * inv_det
        # if(u < 0.f || u > 1.f) return 0;

        # check v side
        q = t.cross(e1)
        v = d.dot(q)*inv_det
        #if(v < 0.f || u + v  > 1.f) return 0;

        #
        dist = e2.dot(q) * inv_det;
        #code.interact(local=locals())
        
        dist = sp.Piecewise(
            (float('inf'), sp.Abs(det) < eps),
            (float('inf'), u < 0),
            (float('inf'), u > 1),
            (float('inf'), v < 0),
            (float('inf'), u + v > 1),
            (float('inf'), dist < eps),
            (dist,True))
        dist.subs(ctx)
        return dist

class Quad:
    def __init__(self,v1,v2,v3,v4):
        self.f1 = Face(v1,v2,v3)
        self.f2 = Face(v4,v3,v2)

    def draw(self,ctx):
        self.f1.draw(ctx)
        self.f2.draw(ctx)

    def intersect(self,ray,ctx):
        return sp.Min(self.f1.intersect(ray,ctx),
                      self.f2.intersect(ray,ctx))
    
class Cylinder:
    def __init__(self,posFn,axisFn,radius):
        self.posFn = posFn
        self.axisFn = axisFn
        self.radius = radius
        pass

    def draw(self,world_state):
        pos  = sp2np(self.posFn.subs(world_state))[0:3]
        axis = sp2np(self.axisFn.subs(world_state))[0:3]
        #
        cylinder(pos=pos,axis=axis,radius=self.radius)
        pass

    # https://www.cl.cam.ac.uk/teaching/1999/AGraphHCI/SMAG/node2.html
    def intersect_cylinder(self,ray,world_state):
        # Cylinder parameters
        pa  = np.squeeze(sp2np(self.posFn.subs(world_state))[0:3])
        va = np.squeeze(sp2np(self.axisFn.subs(world_state))[0:3])
        h = np.linalg.norm(va)
        va = va/h
        # ray parameters
        p = np.squeeze(ray[0])
        v = np.squeeze(ray[1])
        v = v/np.linalg.norm(v)

        # compute intersection with infinite cylinder
        dp = p - pa.T
        A = np.linalg.norm(np.squeeze(v - v.dot(va)*va.T))**2 
        B = 2*float((v - v.dot(va)*va.T).dot((dp - (dp.dot(va)*va.T)).T))
        C = np.linalg.norm(np.squeeze(dp - dp.dot(va)*va))**2 - self.radius**2
        #code.interact(local=locals())
        det = B**2 - 4*A*C
        #print("{3} = {0} - 4*{1}*{2}".format(B**2,A,C,det))
        if det < 0:
            return float('Inf')
        #code.interact(local=locals())
        t1 = (-B + det**(.5))/(2*A)
        candidate1 = p + t1*v
        t2 = (-B - det**(.5))/(2*A)
        candidate2 = p + t2*v
        
        # account for cylinder caps.
        # project onto the bottom cap plane
        height = np.linalg.norm(va)
        ortho_comp1 = va.dot(candidate1 - pa)
        ortho_comp2 = va.dot(candidate2 - pa)
        #print("ocs = {0} {1}".format(ortho_comp1,ortho_comp2))
        if ortho_comp1 < 0 or h < ortho_comp1 :
            t1 = float('inf')
        if ortho_comp2 < 0 or h < ortho_comp2:
            t2 = float('inf')
            
        return min(t1,t2)

    def intersect_caps(self,ray,world_state):
        top = Circle(self.posFn,self.axisFn,self.radius)
        bottom = Circle(self.posFn+self.axisFn,self.axisFn,self.radius)
        
        return sp.Min(top.intersect(ray,world_state),bottom.intersect(ray,world_state))
    
    def intersect(self,ray,world_state):
        cap_dist = self.intersect_caps(ray,world_state).subs(world_state)
        cyl_dist = self.intersect_cylinder(ray,world_state)
        
        return min(cyl_dist,cap_dist)

class Compass:
    def __init__(self):
        pass

    def draw(self):
        scale = 20
        arrow(pos=(0,0,0),axis=(scale,0,0),color=(1,0,0))
        arrow(pos=(0,0,0),axis=(0,scale,0),color=(0,1,0))
        arrow(pos=(0,0,0),axis=(0,0,scale),color=(0,0,01))
        arrow(pos=(0,0,0),axis=(-scale,0,0),color=(1,0,0))
        arrow(pos=(0,0,0),axis=(0,-scale,0),color=(0,1,0))
        arrow(pos=(0,0,0),axis=(0,0,-scale),color=(0,0,01))        

def simp_heaviside(arg):
    #code.interact(local=locals())        
    return sp.Piecewise((0,arg < 0),(1,True))
    
class Cube:
    def get_syms(self):
        return {'cube_theta':0,'cube_tx':0,'cube_ty':0,'cube_tz':0}
    
    def __init__(self):
        # rotation
        transform = bend_mat_sym().subs({'bend':'cube_theta'})
        transform = trans_mat_sym().subs({'tx':'cube_tx','ty':'cube_ty','tz':'cube_tz'}) * transform
        # translation        
        
        # back and front
        q1 = Quad(*[transform*sp.Matrix([[x],[y],[1],[1]]) for x in [-1,1] for y in [-1,1]])
        q2 = Quad(*[transform*sp.Matrix([[x],[y],[-1],[1]]) for x in [-1,1] for y in [-1,1]])

        # top and bottom
        q3 = Quad(*[transform*sp.Matrix([[x],[1],[z],[1]]) for x in [-1,1] for z in [-1,1]])
        q4 = Quad(*[transform*sp.Matrix([[x],[-1],[z],[1]]) for x in [-1,1] for z in [-1,1]])
        
        # left and right
        q5 = Quad(*[transform*sp.Matrix([[1],[y],[z],[1]]) for y in [-1,1] for z in [-1,1]])
        q6 = Quad(*[transform*sp.Matrix([[-1],[y],[z],[1]]) for y in [-1,1] for z in [-1,1]])

        self.faces = [q1,q2,q3,q4,q5,q6]
        
    # fill the dr_cube subdirectory.
    def compile(self):
        #code.interact(local=locals())

        # define the render function
        dist = float('inf')
        for face in self.faces:
            dist = sp.Min(dist,face.intersect(None,{}))

        # print the render function        
        codegen(('distance',dist),'C',to_files=True,prefix='dr_cube/distance',header=True,empty=True)
            
        # print the derivitives
        for var in self.get_syms():
            deriv = sp.diff(dist,var)
            name = 'diff_{0}'.format(var)
            deriv = deriv.replace(sp.Heaviside,simp_heaviside)
            codegen((name,deriv),'C',to_files=True,prefix='dr_cube/' + name,header=True,empty=True)            

        #code.interact(local=locals())

    # return d Dist / d Theta where variable = theta evaluated at symbols
    def diff(self,variable,symbols):        
        # from ctypes import *
        cube_lib = cdll.LoadLibrary("dr_cube/cube_lib.so")
        if variable == 'cube_theta':
            fn = cube_lib.__getattr__('_Z15diff_{0}dddddddddd'.format(variable))
        else:
            fn = cube_lib.__getattr__('_Z12diff_{0}dddddddddd'.format(variable))
        fn.restype = c_double
        #code.interact(local=locals())
        d = fn(*[c_double(symbols[key]) for key  in sorted(symbols)])
        #print("d Dist/d{0} = {1}".format(variable,d))
        return d

class Mesh:
    def __init__(self,filepath,color,T=None):
        self.vertexes = []
        self.faces = []
        with open(filepath) as f:
            for line in f:
                #print('line = ' + line)
                first, rest = line.split(' ',1)
                if first == 'v':                    
                    x, y, z = rest.split(' ')
                    xyz = (float(x),float(y),float(z),1.0)
                    if not T is None:
                        xyz = T.dot(np.array([[x],[y],[z],[1]]).astype(float))
                    self.vertexes.append(sp.Matrix(xyz))
                elif first == 'f':
                    i1,i2,i3 = rest.split(' ')
                    i1,i2,i3 = [int(d.split('/')[0])-1 for d in [i1,i2,i3]]
                    face_vtxs = [self.vertexes[i] for i in [i1,i2,i3]]
                    f = Face(*face_vtxs)
                    f.color = color
                    self.faces.append(f)
                    

        print("loaded {0} vertexes and {1} faces".format(len(self.vertexes),len(self.faces)))
    
    def draw(self):
        [face.draw({}) for face in self.faces]
