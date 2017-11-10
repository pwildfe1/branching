import rhinoscriptsyntax as rs
import math as m
import random as r

class branch:
    def __init__(self,PT,VEC,ANG,AXIS):
        self.start = PT
        self.vec = VEC
        self.ang = ANG
        self.axis = AXIS
        self.defined = False
    def defineEnds(self):
        self.vec01 = rs.VectorRotate(self.vec,self.ang,self.axis)
        self.vec02 = rs.VectorRotate(self.vec,-self.ang,self.axis)
        self.end01 = rs.PointAdd(self.start,self.vec01)
        self.end02 = rs.PointAdd(self.start,self.vec02)
        self.defined = True
        return [self.end01,self.vec01,self.end02,self.vec02]
    def draw(self):
        if self.defined:
            branch01 = rs.AddCurve([self.start,self.end01])
            branch02 = rs.AddCurve([self.start,self.end02])
            return [branch01,branch02]

class vine:
    def __init__(self,MESH,PT,VEC,ANG):
        self.mesh = MESH
        self.start = PT
        self.vec = VEC
        self.len = rs.VectorLength(self.vec)
        self.drawn = []
        self.ang = ANG
        self.branches = []
    def findAxis(self,point):
        norms = rs.MeshVertexNormals(self.mesh)
        verts = rs.MeshVertices(self.mesh)
        param = rs.PointArrayClosestPoint(verts,point)
        axis = norms[param]
        return axis
    def startBranch(self):
        axis = self.findAxis(self.start)
        firstBranch = branch(self.start,self.vec,self.ang,axis)
        self.branches.append(firstBranch)
    def pullBranch(self,stick):
        traits = stick.defineEnds()
        stick.end01 = rs.PullPoints(self.mesh,[traits[0]])[0]
        stick.end02 = rs.PullPoints(self.mesh,[traits[2]])[0]
        crvs = stick.draw()
        branch01 = rs.PullCurveToMesh(self.mesh,crvs[0])
        branch02 = rs.PullCurveToMesh(self.mesh,crvs[1])
        self.drawn.append(branch01)
        self.drawn.append(branch02)
        rs.DeleteObjects(crvs)
    def grow(self):
        newBranches = []
        print(self.ang)
        first = False
        if len(self.branches)==0:
            self.startBranch()
            first = True
        for i in range(len(self.branches)):
            self.pullBranch(self.branches[i])
            axis01 = self.findAxis(self.branches[i].end01)
            axis02 = self.findAxis(self.branches[i].end02)
            b01 = r.random()
            b02 = r.random()
            if rs.VectorAngle(self.branches[i].axis,axis01)<60 and b01<.5:
                ang = self.ang*r.random()
                self.branches[i].vec01 = rs.VectorUnitize(self.branches[i].vec01)
                self.branches[i].vec01 = self.branches[i].vec01*self.len
                sc = r.random()+.25
                if sc>1:
                    sc = 1
                v = self.branches[i].vec01*sc
                newBranches.append(branch(self.branches[i].end01,v,ang,axis01))
            if rs.VectorAngle(self.branches[i].axis,axis02)<60 and b02<.5:
                ang = self.ang*r.random()
                self.branches[i].vec02 = rs.VectorUnitize(self.branches[i].vec02)
                self.branches[i].vec02 = self.branches[i].vec02*self.len
                sc = r.random()+.25
                if sc>1:
                    sc = 1
                v = self.branches[i].vec02*sc
                newBranches.append(branch(self.branches[i].end02,v,self.ang,axis02))
        self.branches = []
        self.branches.extend(newBranches)
        return self.branches



def Main():
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    srcs = rs.GetObjects("please select paths",rs.filter.curve)
    end = rs.MeshAreaCentroid(mesh)
    length = 6
    ang = 20
    gen = 12
    for i in range(len(srcs)):
        nParam = r.random()
        start = rs.EvaluateCurve(srcs[i],rs.CurveParameter(srcs[i],nParam))
        vec = rs.VectorCreate(end,start)
        vec = rs.VectorUnitize(vec)
        vec = vec*length
        tree = vine(mesh,start,vec,ang)
        for n in range(gen):
            tree.grow()

Main()