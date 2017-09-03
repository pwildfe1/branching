import rhinoscriptsyntax as rs
import math as m
import sys


def vecRotate(vec,ang,axis):
    cos = m.cos(m.pi/180*ang)
    sin = m.sin(m.pi/180*ang)
    v = vec
    u = vecUnitize(axis)
    R1,R2,R3 = [] , [] , []
    c = 1-cos

    R1.append(cos+m.pow(u[0],2)*c)
    R1.append(u[0]*u[1]*c-u[2]*sin)
    R1.append(u[0]*u[2]*c+u[1]*sin)
    
    R2.append(u[1]*u[0]*c+u[2]*sin)
    R2.append(cos+m.pow(u[1],2)*c)
    R2.append(u[1]*u[2]*c-u[0]*sin)
    
    R3.append(u[2]*u[0]*c-u[1]*sin)
    R3.append(u[2]*u[1]*c+u[0]*sin)
    R3.append(cos+m.pow(u[2],2)*c)
    
    x = vecDot(v,R1)
    y = vecDot(v,R2)
    z = vecDot(v,R3)
    
    return [x,y,z]


def vecMag(vec):
    sum = 0    
    for i in range(len(vec)):
        sum = sum+m.pow(vec[i],2)
    sum = m.pow(sum,.5)
    return sum


def transpose(matrix):
    transpose = []    
    for i in range(len(matrix[0])):
        for j in range(len(matrix)):
            transpose.append(matrix[j][i])
    return transpose


def vecUnitize(vec):
    mag = vecMag(vec)
    for i in range(len(vec)):
        vec[i] = vec[i]/mag
    return vec


def vecDot(v1,v2):
    sum = 0    
    for i in range(len(v1)):
        sum = v1[i]*v2[i] + sum
    return sum


def vecCross(v1,v2):
    x = v1[1]*v2[2]-v1[2]*v2[1]
    y = v1[2]*v2[0]-v1[0]*v2[2]
    z = v1[0]*v2[1]-v1[1]*v2[0]
    return [x,y,z]


def vecAng(v1,v2):
    v1 = vecUnitize(v1)
    v2 = vecUnitize(v2)
    val = vecDot(v1,v2)
    ang = m.acos(val)
    return ang


def vecDiff(v1,v2):
    nV = []
    for i in range(len(v1)):
        nV.append(v1[i]-v2[i])
    return nV


def vecAdd(v1,v2):
    nV = []
    for i in range(len(v1)):
        nV.append(v1[i]+v2[i])
    return nV

def vecScale(v,f):
    nV = []
    for i in range(len(v)):
        nV.append(v[i]*f)
    return nV


class lineEq:
    def __init__(self,START,END):
        self.st = START
        self.en = END
        self.vec = vecDiff(self.en,self.st)
    def updateVec(self):
        self.vec = vecDiff(self.en,self.st)
    def rotate(self,ang,axis):
        self.updateVec()
        vector = vecRotate(self.vec,ang,axis)
        self.en = vecAdd(self.st,vector)
        self.updateVec()
    def evalParam(self,pt):
        t = (pt[0]-self.st[0])/self.vec[0]
        return t
    def closePt(self,pt):
        vec01 = vecDiff(self.st,pt)
        vec02 = vecDiff(self.en,pt)
        axis = vecCross(vec01,vec02)
        #
        v1 = self.vec
        v2 = vecRotate(self.vec,90,axis)
        st = self.st
        #
        t = v2[1]*(st[0]-pt[0]) + v2[0]*(pt[1]-st[1])
        t = t/(v2[0]*v1[1]-v2[1]*v1[0])
        #
        x = v1[0]*t+st[0]
        y = v1[1]*t+st[1]
        z = v1[2]*t+st[2]
        close = [x,y,z]
        #
        stDist = vecMag(vecDiff(pt,self.st))
        enDist = vecMag(vecDiff(pt,self.en))
        enParam = self.evalParam(self.en)
        #
        if t<0 or t>enParam:
            if stDist<enDist:
                close = self.st
            else:
                close = self.en
        return close

class branch:
    def __init__(self,PT,VEC,ANG,AXIS):
        self.start = PT
        self.vec = VEC
        self.ang = ANG
        self.axis = AXIS
        self.defined = False
    def defineEnds(self):
        self.vec01 = vecRotate(self.vec,self.ang,self.axis)
        self.vec02 = vecRotate(self.vec,-self.ang,self.axis)
        self.end01 = vecAdd(self.start,self.vec01)
        self.end02 = vecAdd(self.start,self.vec02)
        self.defined = True
        return [self.end01,self.vec01,self.end02,self.vec02]
    def draw(self):
        if self.defined:
            branch01 = rs.AddCurve([self.start,self.end01])
            branch02 = rs.AddCurve([self.start,self.end02])
            return [branch01,branch02]

class vine:
    def __init__(self,PT,VEC,ANG):
        self.start = PT
        self.vec = VEC
        self.ang = ANG
        self.branches = []
    def startBranch(self):
        axis = [0,0,1]#self.findAxis(self.start)
        firstBranch = branch(self.start,self.vec,self.ang,axis)
        self.branches.append(firstBranch)
    def grow(self):
        newBranches = []
        if len(self.branches)==0:
            self.startBranch()
        for i in range(len(self.branches)):
            self.branches[i].defineEnds()
            axis01 = [0,0,1] #self.findAxis(self.branches[i].end01)
            axis02 = [0,0,1] #self.findAxis(self.branches[i].end02)
            newBranches.append(branch(self.branches[i].end01,self.branches[i].vec01,self.ang,axis01))
            newBranches.append(branch(self.branches[i].end02,self.branches[i].vec02,self.ang,axis02))
            self.branches[i].draw()
        self.branches = []
        self.branches.extend(newBranches)
        return self.branches


def Main():
    start = rs.GetObject("please select start",rs.filter.point)
    start = rs.PointCoordinates(start)
    ang = 20
    length = 100
    gen = 8
    vec = [1,0,0]
    vec = vecScale(vec,length);
    tree = vine(start,vec,ang)
    for i in range(gen):
        tree.grow()

Main()