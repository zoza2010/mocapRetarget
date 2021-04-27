# paths to maya characters
import pymel.core as pm
import retarget as rt
import maya.mel as mel
import common_utils as utils
reload(utils)
reload(rt)


def getTopGroups(search_pattern):
    import pymel.core as pm
    # sources = pm.ls('*|*:char_*|*:rig_gr|*:Group|*:Main|*:DeformationSystem', type='transform')
    sources = pm.ls(search_pattern, type='transform')
    charTopGroups = []
    for src in sources:
        top_grp = pm.PyNode((src.fullPath()).split('|')[1])
        charTopGroups.append(top_grp)
    return charTopGroups


def getName(topCharGroup):
    charName = ''
    if topCharGroup:
        try:
            charName = topCharGroup.split(':')[-1]
        except IndexError:
            charName = topCharGroup
    return charName



def preBake():
    pm.currentUnit(t = 'pal')
    pm.select("all_ctrls_set*")
    mel.eval('ogs - pause;')


def postBake():
    pm.delete('mocap*')
    mel.eval('delete -staticChannels -unitlessAnimationCurves false -hierarchy 0 -controlPoints 0 -shape 0;')
    mel.eval('ogs - pause;')


def bake():
    preBake()
    pm.bakeResults(simulation=True, t= "{}:{}".format(pm.playbackOptions(min=True, q=True),
                                                pm.playbackOptions(max=True, q=True)))
    postBake()


def go_batch():
    assets_config = "asset_configs/enotki.json"
    import json
    import os
    APP_ROOT = os.path.dirname(__file__)
    # get maya character data
    batch_data = None
    with open(utils.expand_path(assets_config), 'r') as f:
        file_data =f.read()
        batch_data = json.loads(file_data)

    asset_search_patterns = batch_data.get('search_patterns')
    assets_data = batch_data.get('assets')

    topCharGrps = getTopGroups(asset_search_patterns)
    if topCharGrps:
        for topGrp in topCharGrps:
            mocapNamespace = topGrp.namespace()
            mocapCharName = getName(topGrp)
            char_data = assets_data[mocapCharName]
            config_path =utils.expand_path(char_data.get('config_path'))
            pathToCharacter = char_data['asset_path']

            pm.system.createReference(pathToCharacter, namespace=mocapCharName)
            rt.connect_skels(mocapNamespace, '{}:'.format(mocapCharName), config_path)
        bake()
    else:
        pm.warning('no valid characters found in this scene')