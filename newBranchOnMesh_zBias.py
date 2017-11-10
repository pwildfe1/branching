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
    def __init__(self,MESH,SRC,VEC,ANG):
        self.mesh = MESH
        self.path = SRC
        self.start = rs.CurveStartPoint(self.path)
        self.vec = VEC
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
        rs.DeleteObjects(crvs)
    def grow(self,side):
        newBranches = []
        if len(self.branches)==0:
            self.startBranch()
        for i in range(len(self.branches)):
            self.pullBranch(self.branches[i])
            axis01 = self.findAxis(self.branches[i].end01)
            axis02 = self.findAxis(self.branches[i].end02)
            if rs.VectorAngle(self.branches[i].axis,axis01)<60:
                param = rs.CurveClosestPoint(self.path,self.branches[i].end01)
                dist = rs.Distance(self.branches[i].end01,rs.EvaluateCurve(self.path,param)) 
                tan = rs.CurveTangent(self.path,param)
                vecAng = rs.VectorAngle(self.branches[i].vec01,tan)
                vec = rs.VectorRotate(self.branches[i].vec01,-vecAng/5,axis01)
                unitized = rs.VectorUnitize(self.branches[i].vec01)
                dot = .25#abs(rs.VectorDotProduct(unitized,[0,0,1]))
                if dot>1:
                    vec = rs.VectorScale(self.branches[i].vec01,dot*2)
                    rs.AddLayer("pipe",[255,0,0])
                    rs.CurrentLayer("pipe")
                else:
                    vec = self.branches[i].vec01
                    rs.AddLayer("branch",[0,0,255])
                    rs.CurrentLayer("branch")
                newBranches.append(branch(self.branches[i].end01,vec,self.ang,axis01))
            if rs.VectorAngle(self.branches[i].axis,axis02)<60:
                param = rs.CurveClosestPoint(self.path,self.branches[i].end02)
                dist = rs.Distance(self.branches[i].end02,rs.EvaluateCurve(self.path,param)) 
                tan = rs.CurveTangent(self.path,param)
                vecAng = rs.VectorAngle(self.branches[i].vec02,tan)
                vec = rs.VectorRotate(self.branches[i].vec02,-vecAng/5,axis02)
                unitized = rs.VectorUnitize(self.branches[i].vec02)
                dot = .25#abs(rs.VectorDotProduct(unitized,[0,0,1]))
                if dot>1:
                    vec = rs.VectorScale(self.branches[i].vec02,dot*2)
                    rs.AddLayer("pipe",[255,0,0])
                    rs.CurrentLayer("pipe")
                else:
                    vec = self.branches[i].vec02
                    rs.AddLayer("branch",[0,0,255])
                    rs.CurrentLayer("branch")
                newBranches.append(branch(self.branches[i].end02,vec,self.ang,axis02))        
        self.branches = []
        self.branches.extend(newBranches)
        return self.branches



def Main():
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    srcs = rs.GetObjects("please select path",rs.filter.curve)
    ang = rs.GetReal("please enter angle",20)
    length = rs.GetReal("please enter length",20)
    gen = rs.GetInteger("please enter number of generations",10)
    for i in range(len(srcs)):
        src = srcs[i]
        end = rs.CurveEndPoint(src)
        start = rs.CurveStartPoint(src)
        param = rs.CurveClosestPoint(src,start)
        vec = rs.VectorUnitize(rs.CurveTangent(src,param))
        vec = vec*length
        tree = vine(mesh,src,vec,ang)
        for i in range(gen):
            """
            if i%2==0:
                side=1
            else:
                side=2
            if i%3==0 and i!=0:
                side=1
            tree.grow(side)
            #
            if i%2==0:
                side=2
            else:
                side=1
            if i%3==0 and i!=0:
                side=1
            """
            tree.grow(1)
            #

Main()