import rhinoscriptsyntax as rs
import math as m
import random as r

def setAttractor(attPt,testPt,thres,min):
    dist=rs.Distance(attPt,testPt)
    if dist/thres>1:
        return 1
    elif dist/thres>min and dist/thres<1:
        return dist/thres
    elif dist/thres<min:
        return min

def angAttractor(attPt,testPt,baseVec,baseAng,thres,max):
    compare=rs.VectorCreate(attPt,testPt)
    editAng=rs.VectorAngle(baseVec,compare)
    ang=baseAng+(1-setAttractor(attPt,testPt,thres,0))*(editAng-baseAng)
    if ang>max:
        ang=max
    return ang

def testAlign(crv1,crv2):
    start=rs.CurveStartPoint(crv2)
    crv1Start=rs.CurveStartPoint(crv1)
    pts=rs.PolylineVertices(crv1)
    index=rs.PointArrayClosestPoint(pts,start)
    crv1Pt=pts[index]
    if index!=0:
        return False
    else:
        return True

def align(crv1,crv2,origin,axis):
    count=0
    vert=rs.PolylineVertices(crv1)
    while testAlign(crv1,crv2)==False or count>len(vert):
        count=count+1
        crv1=rs.RotateObject(crv1,origin,360/len(vert),axis)
    return crv1

def squareSect(crv,width,height):
    sections=[]
    divPts=rs.DivideCurve(crv,10)
    keep=True
    for i in range(len(divPts)):
        param=rs.CurveClosestPoint(crv,divPts[i])
        tan=rs.CurveTangent(crv,param)
        plane=rs.PlaneFromNormal(divPts[i],tan)
        sect=rs.AddRectangle(plane,width,height)
        cpt=rs.CurveAreaCentroid(sect)[0]
        vec=rs.VectorCreate(divPts[i],cpt)
        sect=rs.MoveObject(sect,vec)
        if i>0:
            if testAlign(sect,oldSect)==False:
                sect=align(sect,oldSect,divPts[i],tan)
        oldSect=sect
        sections.append(sect)
    branch=rs.AddLoftSrf(sections,None,None,2,0,0,False)
    edges=rs.DuplicateEdgeCurves(branch)
    if width>height:
        testVal=height
    else:
        testVal=width
    for i in range(len(edges)):
        testPt=rs.CurveMidPoint(edges[i])
        for j in range(len(edges)):
            param=rs.CurveClosestPoint(edges[j],testPt)
            pt=rs.EvaluateCurve(edges[j],param)
            if rs.Distance(pt,testPt)<testVal/6:
                keep=False
    rs.DeleteObjects(sections)
    rs.DeleteObjects(edges)
    return branch

def baseBranch(mesh,start,vec,ang,length,gen):
    end=rs.PointAdd(start,vec*length)
    end=rs.MeshClosestPoint(mesh,end)[0]
    branch1=rs.AddLine(start,end)
    projBranch1=rs.PullCurveToMesh(mesh,branch1)
    branches=[projBranch1]
    stored=branches
    newBranches=[]
    i=0
    count=0
    while i < gen:
        i=i+1
        for branch in branches:
            end=rs.CurveEndPoint(branch)
            param=rs.CurveClosestPoint(branch,end)
            vec=rs.CurveTangent(branch,param)
            vec=rs.VectorUnitize(vec)
            index=rs.MeshClosestPoint(mesh,end)[1]
            norm=rs.MeshFaceNormals(mesh)[index]
            vec=rs.VectorRotate(vec,ang,norm)
            start=rs.PointAdd(end,vec*length)
            start=rs.MeshClosestPoint(mesh,start)[0]
            newBranch=rs.AddLine(end,start)
            pulledBranch=rs.PullCurveToMesh(mesh,newBranch)
            rs.DeleteObject(newBranch)
            newBranches.append(pulledBranch)
            vec=rs.VectorRotate(vec,-2*ang,norm)
            start=rs.PointAdd(end,vec*length)
            start=rs.MeshClosestPoint(mesh,start)[0]
            newBranch=rs.AddLine(end,start)
            pulledBranch=rs.PullCurveToMesh(mesh,newBranch)
            rs.DeleteObject(newBranch)
            if rs.Distance(start,rs.CurveEndPoint(pulledBranch))<length/2:
                newBranches.append(pulledBranch)
        branches=newBranches
        stored.extend(branches)
        newBranches=[]
        count=count+1
    #for i in range(len(stored)):
    #    squareSect(stored[i],1,1)
    print count
    return stored


def tanVec(crv,point):
    param=rs.CurveClosestPoint(crv,point)
    tangent=rs.CurveTangent(crv,param)
    tangent=rs.VectorUnitize(tangent)
    return tangent

def Main():
    mesh=rs.GetObjects("select mesh",rs.filter.mesh)
    start=rs.GetObject("select start points",rs.filter.point)
    refVec = rs.GetObject("select crv direction",rs.filter.curve)
    ang=rs.GetReal("enter branching angle",30)
    length=rs.GetReal("enter branch length",15)
    gen=rs.GetInteger("enter number of generations",3)
    lines=rs.AddLayer("branch",[255,0,0])
    rs.EnableRedraw(False)
    rs.CurrentLayer(lines)
    vec=tanVec(refVec,start)
    centers=rs.MeshFaceCenters(mesh)
    index=rs.PointArrayClosestPoint(centers,start)
    norm=rs.MeshFaceNormals(mesh)[index]
    vec=rs.VectorRotate(vec,0,norm)
    branches=baseBranch(mesh,start,vec,ang,length,gen)
    return branches

Main()