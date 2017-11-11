import rhinoscriptsyntax as rs
import math as m

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
        self.cVec = self.vec
        self.length = rs.VectorLength(self.vec)
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
        ####
        stick.end01 = rs.PullPoints(self.mesh,[traits[0]])[0]
        stick.end02 = rs.PullPoints(self.mesh,[traits[2]])[0]
        crvs = stick.draw()
        branch01 = rs.PullCurveToMesh(self.mesh,crvs[0])
        branch02 = rs.PullCurveToMesh(self.mesh,crvs[1])
        rs.DeleteObjects(crvs)
    def grow(self):
        newBranches = []
        if len(self.branches)==0:
            self.startBranch()
        for i in range(len(self.branches)):
            self.pullBranch(self.branches[i])
            axis01 = self.findAxis(self.branches[i].end01)
            axis02 = self.findAxis(self.branches[i].end02)
            if rs.VectorAngle(self.branches[i].axis,axis01)<60:
                v = rs.VectorCreate(self.branches[i].end01,self.branches[i].start)
                v = rs.VectorScale(v,self.length/rs.VectorLength(v))
                newBranches.append(branch(self.branches[i].end01,v,self.ang,axis01))
            if rs.VectorAngle(self.branches[i].axis,axis02)<60:
                v = rs.VectorCreate(self.branches[i].end02,self.branches[i].start)
                v = rs.VectorScale(v,self.length/rs.VectorLength(v))
                newBranches.append(branch(self.branches[i].end02,v,self.ang,axis02))
        self.branches = []
        self.branches.extend(newBranches)
        return self.branches



def Main():
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    src = rs.GetObject("please select path",rs.filter.curve)
    ang = rs.GetReal("please enter angle",20)
    length = rs.GetReal("please enter length",6)
    gen = rs.GetInteger("please enter number of generations",6)
    end = rs.CurveEndPoint(src)
    start = rs.CurveStartPoint(src)
    vec = rs.VectorCreate(end,start)
    vec = rs.VectorUnitize(vec)
    vec = vec*length
    tree = vine(mesh,start,vec,ang)
    for i in range(gen):
        tree.grow()

Main()