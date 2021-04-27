import sys
import math
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


nodeName = "computePoleVector"
nodeId = OpenMaya.MTypeId(0x100fff)
import maya.OpenMaya as om


def normalize(vec):
    norm = om.MVector (vec)
    om.MVector.normalize (norm)
    return norm



class computePoleVector(OpenMayaMPx.MPxNode):

    #inString = OpenMaya.MObject()
    #inParam = OpenMaya.MObject()
    #outString = OpenMaya.MObject()

    inLegPosition = OpenMaya.MObject()
    inKneePosition = OpenMaya.MObject()
    inFootPosition = OpenMaya.MObject()
    poleVector = OpenMaya.MObject()


    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == computePoleVector.poleVector:
            '''
            dataHandleInString = dataBlock.inputValue(computePoleVector.inString)
            dataHandleInParam = dataBlock.inputValue(computePoleVector.inParam)

            inStringVal = dataHandleInString.asString()
            inParamVal = dataHandleInParam.asInt()

            outVal = inStringVal.replace('<param>', str(inParamVal).zfill(3))

            dataHandleOutString = dataBlock.outputValue(computePoleVector.outString)
            dataHandleOutString.setString(outVal)
            dataBlock.setClean(plug)
            '''

            dataHandle = OpenMaya.MDataHandle(dataBlock.inputValue(computePoleVector.inLegPosition))
            legPositionValue = dataHandle.asVector()
            dataHandle = OpenMaya.MDataHandle (dataBlock.inputValue (computePoleVector.inKneePosition))
            kneePositionValue = dataHandle.asVector()
            dataHandle = OpenMaya.MDataHandle (dataBlock.inputValue (computePoleVector.inFootPosition))
            footPositionValue = dataHandle.asVector()


            #computations
            #find start of vector
            pt0 = legPositionValue
            pt1 = kneePositionValue
            pt2 = footPositionValue

            res1 = OpenMaya.MVector (pt1.x - pt0.x, pt1.y - pt0.y, pt1.z - pt0.z)
            res1Raw = res1
            res2 = OpenMaya.MVector (pt2.x - pt0.x, pt2.y - pt0.y, pt2.z - pt0.z)
            res2Raw = res2

            thetaCos = normalize (res2) * normalize (res1)
            thetaSin = math.sqrt(1-math.sqrt(thetaCos))

            vectorProject = thetaCos * res1.length ()
            poleStartPos = (normalize (res2) * vectorProject) + pt0

            #find pole vector
            poleVector = OpenMaya.MVector(pt1.x - poleStartPos.x,
                                          pt1.y - poleStartPos.y,
                                          pt1.z - poleStartPos.z)

            #vectorCrossProduct = res1 ^ res2

            offset = 10
            polePos = normalize (poleVector) * offset + pt1
            result = polePos

            dataHandle = OpenMaya.MDataHandle(dataBlock.outputValue (computePoleVector.poleVector))
            dataHandle.set3Double(result.x, result.y, result.z)
            dataBlock.setClean(plug)

        else:
            return OpenMaya.kUnknownParameter




def nodeCreator():
    return OpenMayaMPx.asMPxPtr(computePoleVector())

def nodeInitializer():
    # 1 creating function set
    mFnAttr = OpenMaya.MFnNumericAttribute()
    mFsAttr = OpenMaya.MFnTypedAttribute()

    #mMtxAttr = OpenMaya.MFnMatrixAttribute()  #matrix

    #for vector attributes
    mNAttr = OpenMaya.MFnNumericAttribute()


    #2  CREATE_ATTRIBUTES
    mNAttr = OpenMaya.MFnNumericAttribute()
    computePoleVector.inLegPosition = mNAttr.create ('legPosition', 'lp', OpenMaya.MFnNumericData.k3Double)


    # create inKneePosition attribute (vector param)
    # _________________________________________________________________________________________________
    computePoleVector.inKneePosition = mNAttr.create ('kneePosition', 'kp', OpenMaya.MFnNumericData.k3Double)



    #create inFootPosition attribute (vector param)
    #_________________________________________________________________________________________________
    computePoleVector.inFootPosition = mNAttr.create ('footPosition', 'fp', OpenMaya.MFnNumericData.k3Double)

    #________________________________________________________________________________________________


    #create poleVector attribute (vector param)
    #_________________________________________________________________________________________________
    computePoleVector.poleVector = mNAttr.create ('poleVector', 'pv', OpenMaya.MFnNumericData.k3Double)
    #________________________________________________________________________________________________


    #3 ATTACHING_ATTRIBUTES TO THE NODE
    #in
    computePoleVector.addAttribute(computePoleVector.inLegPosition)
    computePoleVector.addAttribute(computePoleVector.inKneePosition)
    computePoleVector.addAttribute(computePoleVector.inFootPosition)
    #out
    computePoleVector.addAttribute (computePoleVector.poleVector)

    #4 Design circularity
    computePoleVector.attributeAffects (computePoleVector.inLegPosition, computePoleVector.poleVector)
    computePoleVector.attributeAffects (computePoleVector.inKneePosition, computePoleVector.poleVector)
    computePoleVector.attributeAffects(computePoleVector.inFootPosition, computePoleVector.poleVector)




def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 'I.Zuikov',  "0.1")
    try:
        mplugin.registerNode(nodeName,nodeId ,nodeCreator, nodeInitializer)
    except:
        sys.stderr.write("Failed to register command: " + nodeName)

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(nodeName,nodeId ,nodeCreator, nodeInitializer)
    except:
        sys.stderr.write("Failed to de-register command: " + nodeName)