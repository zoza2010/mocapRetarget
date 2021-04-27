"""
Drag and drop for Maya 2018+
"""
import os
import sys
from posixpath import join

try:
    import maya.mel
    import maya.cmds

    # import maya.OpenMaya as api

    isMaya = True
except ImportError:
    isMaya = False


def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""

    # srcPath = os.path.dirname(__file__)
    # get latest script version folder
    from posixpath import join
    setup_folder = os.path.dirname(__file__)
    # script_versions = filter(lambda i: os.path.isdir(join(setup_folder, i)) and i.startswith('setupTool'), os.listdir(setup_folder))
    # last_version = max(script_versions)
    srcPath = setup_folder.replace('\\', '/')  # join(setup_folder, last_version).replace('\\', '/')
    iconPath = os.path.join(srcPath, 'icon', 'icon.png')

    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)

    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)

    command = '''
# -----------------------------------
# Setup Tools
# -----------------------------------

import os, sys

import maya.OpenMayaUI as apiUI
import shiboken2 as shiboken
from PySide2.QtWidgets import QWidget

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

def getMayaWindow():
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QWidget)

qMayaWindow = getMayaWindow()

import core.batch_retarget as br
reload(br)
br.go_batch()
'''.format(path=srcPath, title='actual')

    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)
    maya.cmds.shelfButton(
        command=command,
        annotation='sceneOpen',
        sourceType='Python',
        image=iconPath,
        image1=iconPath,
        parent=parent
    )

    # print("\n// Studio Library has been added to current shelf.")


if isMaya:
    # maya.mel.eval('putenv "ENOTKI" "%s"' % os.environ['ENOTKI'])
    _onMayaDropped()
