# -*- coding: utf-8 -*-
import pymel.core as pm
import common_utils as utils


def loadNodes():
    import os
    nodes_path = utils.expand_path('nodes')
    for nodeName in os.listdir(nodes_path):
        # try:
        #     pm.loadPlugin(os.path.join(nodes_path, nodeName))
        # except ImportError:
        #     pass
        pm.loadPlugin(os.path.join(nodes_path, nodeName))


def computeOffset(src, dst):
    '''
    #function for computing rotation offset
    between two transforms
    :param src: str source transform node name
    :param dst: str destiny transform node name
    :return: MMatrix offset matrix
    '''
    import pymel.core as pm
    src = pm.PyNode(src)
    dst = pm.PyNode(dst)
    worldMtxDst = src.worldMatrix.get()
    worldInvMtxSrc = dst.worldInverseMatrix.get()
    offsetMtx = worldInvMtxSrc * worldMtxDst
    return offsetMtx



def sPoleConstraint(leg, knee, foot, kneeCtrl):
    import os
    leg = pm.PyNode (leg)
    knee = pm.PyNode (knee)
    foot = pm.PyNode (foot)
    kneeCtrl = pm.PyNode (kneeCtrl)
    # load poleVector node
    # nodeName = 'computePoleVector.py'
    # path = os.path.join (os.path.dirname (__file__), 'nodes', nodeName)
    # if pm.pluginInfo ('computePoleVector_1.py', l=True, q=True) != True:
    #     pm.loadPlugin (path)

    decompLegNode = pm.createNode ('decomposeMatrix')
    decompKneeNode = pm.createNode ('decomposeMatrix')
    decompFootNode = pm.createNode ('decomposeMatrix')
    computePoleNode = pm.createNode ('computePoleVector')
    poleLoc = pm.spaceLocator (n='poleLoc')
    # connections
    leg.worldMatrix.connect (decompLegNode.inputMatrix)
    knee.worldMatrix.connect (decompKneeNode.inputMatrix)
    foot.worldMatrix.connect (decompFootNode.inputMatrix)

    decompLegNode.outputTranslate.connect (computePoleNode.legPosition)
    decompKneeNode.outputTranslate.connect (computePoleNode.kneePosition)
    decompFootNode.outputTranslate.connect (computePoleNode.footPosition)
    computePoleNode.poleVector.connect (poleLoc.translate)

    ptCstr = pm.pointConstraint (poleLoc, kneeCtrl)
    #return [poleLoc, decompFootNode, decompKneeNode, decompLegNode, computePoleNode, ptCstr]


def connect_fk_body_parts(**kwargs):
    import math
    try:
        cstr = pm.parentConstraint(kwargs.get('src'), kwargs.get('tgt'))
        cstr.rename('mocapCstr')

        #apply offset matrix if exists
        offset_mtx = kwargs.get('offset_mtx')
        if offset_mtx:
            rotation = offset_mtx.rotate.asEulerRotation()
            rotation_offset = pm.datatypes.Vector(math.degrees(rotation.x), math.degrees(rotation.y), math.degrees(rotation.z))
            # print rotation_offset
            translation_offset = offset_mtx.translate.get()
            cstr.target.target[0].targetOffsetRotate.set(rotation_offset)
            # cstr.target.target[0].targetOffsetTranslate.set(translation_offset)
    except Exception as err:
        print err
    #return cstr


def connect_ik_body_parts(**kwagrs):
    # #connect start part
    # connect_fk_body_parts(src = kwagrs.get('srcStart'),
    #                       tgt = kwagrs.get('tgtStart'),
    #                       offset_mtx =kwagrs.get('offset_mtx_start'))

    #connect middle
    sPoleConstraint(kwagrs.get('srcStart'),
                    kwagrs.get('srcMid'),
                    kwagrs.get('srcEnd'),
                    kwagrs.get('tgtMid'))

    #connect end part
    # print '_________________________________________'
    # print kwagrs.get('offsetEnd')
    connect_fk_body_parts(src = kwagrs.get('srcEnd'),
                          tgt = kwagrs.get('tgtEnd'),
                          offset_mtx =kwagrs.get('offset_mtx_end'))


def prepareBodyPartData(srcNmsp, tgtNmsp, part):
    body_part = {}
    srcFullName = srcNmsp + part.get('source')
    tgtFullName = tgtNmsp + part.get('target')
    offsetFullName = tgtNmsp + part.get('offset_object') if part.get('offset_object') else None

    if offsetFullName:
        offsetMtx = computeOffset(tgtFullName, offsetFullName)
    else:
        offsetMtx = pm.datatypes.Matrix()  # set identity matrix

    body_part['source'] = srcFullName
    body_part['target'] = tgtFullName
    body_part['offset_mtx'] = offsetMtx
    return body_part


def connect_skels(srcNmsp, tgtNmsp, pathToConf):
    import json
    import os

    loadNodes()
    if not os.path.exists(pathToConf):
        raise Exception('cannot find config with given path: {}'.format(pathToConf))

    with open(pathToConf, 'r') as f:
        conf = json.loads(f.read())

        ik_parts_data = []
        fk_parts_data = []
        ctrlSet = pm.sets(n = 'all_ctrls_set')
        #prepare fk parts
        for part in conf['fk_parts']:
            fk_parts_data.append(prepareBodyPartData(srcNmsp, tgtNmsp, part))


        #prepare ik parts
        for ik_object in conf['ik_parts']:
            resolved_ik_object = {}
            resolved_ik_object['start_part'] = prepareBodyPartData(srcNmsp, tgtNmsp, ik_object.get('start_part'))
            resolved_ik_object['mid_part'] = prepareBodyPartData(srcNmsp, tgtNmsp, ik_object.get('mid_part'))
            resolved_ik_object['end_part'] = prepareBodyPartData(srcNmsp, tgtNmsp, ik_object.get('end_part'))
            ik_parts_data.append(resolved_ik_object)


        #connect fk objects:
        for part in fk_parts_data:
            #connect fk body parts
            connect_fk_body_parts(src = part.get('source'),
                                  tgt = part.get('target'),
                                  offset_mtx = part.get('offset_mtx'))
            ctrlSet.add(part.get('target'))


        for part in ik_parts_data:
            # print (part.get('end_part')).get('offset_mtx')
            #connect ik parts
            connect_ik_body_parts(srcStart = part.get('start_part').get('source'),
                                  tgtStart = part.get('start_part').get('target'),
                                  offset_mtx_start = part.get('start_part').get('offset_mtx'),

                                  srcMid= part.get('mid_part').get('source'),
                                  tgtMid = part.get('mid_part').get('target'),
                                  offset_mtx_mid = part.get('mid_part').get('offset_mtx'),

                                  srcEnd =  part.get('end_part').get('source'),
                                  tgtEnd=part.get('end_part').get('target'),
                                  offset_mtx_end = (part.get('end_part')).get('offset_mtx'))
            ctrlSet.add(part.get('start_part').get('target'))
            ctrlSet.add(part.get('mid_part').get('target'))
            ctrlSet.add(part.get('end_part').get('target'))


if __name__=='__main__':
    pass
    # pathToConf = r'D:\my_python_tools\mocapRetarget\mapping_configs\enotki_mapping.json'
    # srcNmsp = 'test'
    # tgtNmsp = 'test_01'
    # connect_skels('srcNmsp:', 'tgtNmsp:', pathToConf)

# import sys
#
# path = r'D:\my_python_tools\mocapRetarget'
# if not path in sys.path:
#     sys.path.append(path)
# import retarget as rt
#
# reload(rt)
#
# pathToConf = r'D:\my_python_tools\mocapRetarget\mapping_configs\enotki_mapping.json'
# rt.connect_skels('char_faf_01:', 'char_faf_rig:',pathToConf)