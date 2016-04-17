#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Séverin Lemaignan, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Implements the command-line version of MakeHuman.
"""

from core import G
import guicommon
import log
from human import Human
import files3d
import getpath
import humanmodifier
import material
import proxy


import sys
sys.path.append("./plugins")
MhxConfig = (__import__("9_export_mhx", fromlist = ["MhxConfig"])).MhxConfig
MHXExporter = (__import__("9_export_mhx", fromlist = ["mhx_main"])).mhx_main
OBJExporter = (__import__("9_export_obj", fromlist = ["mh2obj"])).mh2obj
import exportutils


class ConsoleApp():
    def __init__(self):
        self.selectedHuman = Human(files3d.loadMesh(getpath.getSysDataPath("3dobjs/base.obj"), maxFaces = 5))
        self.log_window = None
        self.splash = None
        self.statusBar = None

    def progress(self, *args, **kwargs):
        pass

def run(args):
    G.app = ConsoleApp()
    human = G.app.selectedHuman

    import humanargparser
    humanargparser.applyModelingArguments(human, args)


    if args["output"]:
        save(human, args["output"])


    # # A little debug test
    # if 'PyOpenGL' in sys.modules.keys():
    #     log.warning("Debug test detected that OpenGL libraries were imported in the console version! This indicates bad separation from GUI.")
    # if 'PyQt4' in sys.modules.keys():
    #     log.warning("Debug test detected that Qt libraries were imported in the console version! This might indicate bad separation from GUI, but is currently normal because MH uses Qt as (only) back-end for loading images.")

def save(human, filepath):
    if filepath.endswith("mhx"):
        ## Export
        exportCfg = MhxConfig()
        exportCfg.scale = 0.1
        exportCfg.unit = "meter"
        exportCfg.feetOnGround = True
        exportCfg.useRotationLimits = True
        exportCfg.useRigify = False
        exportCfg.setHuman(human)
        MHXExporter.exportMhx(filepath, exportCfg)
    elif filepath.endswith("obj"):
        exportCfg = exportutils.config.Config()
        exportCfg.setHuman(human)
        OBJExporter.exportObj(filepath, config=exportCfg)
    else :
        raise RuntimeError("Only MHX and OBJ export is currently supported")
