#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Thomas Larsson

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

TODO
"""

import algos3d
import gui3d
import humanmodifier
import modifierslider
import warpmodifier
import os
import mh
import gui
import filechooser as fc
import log

class GroupBoxRadioButton(gui.RadioButton):

    def __init__(self, task, group, label, groupBox, selected=False):
        super(GroupBoxRadioButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.groupBox.showWidget(self.groupBox)


class ExpressionSimpleModifier(humanmodifier.SimpleModifier):

    def __init__(self, template):
        humanmodifier.SimpleModifier.__init__(self, 'expression', template)
        self.eventType = 'expression'

    def getMax(self):
        return 2.0

    def getMin(self):
        return -1.0


class ExpressionWarpModifier(warpmodifier.WarpModifier):

    def __init__(self, targetName):
        # Macro variables which are fixed and on which the warptargets were modeled
        referenceVariables = { 'gender': 'female',
                               'age':    'young' }
        super(ExpressionWarpModifier, self).__init__('expression-units', targetName, "face", referenceVariables)
        self.eventType = 'expression'

    def getMax(self):
        return 2.0

    def getMin(self):
        return -1.0


#----------------------------------------------------------
#   class ExpressionTaskView
#----------------------------------------------------------

class ExpressionTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Expression tuning')

        self.expressions = [
            ('eyebrows-left', ['down', 'extern-up', 'inner-up', 'up']),
            ('eyebrows-right', ['down', 'extern-up', 'inner-up', 'up']),
            ('eye-left', ['closure', 'opened-up', 'slit']),
            ('eye-right', ['closure', 'opened-up', 'slit']),
            ('mouth', ['compression', 'corner-puller', 'depression', 'depression-retraction', 'elevation', 'eversion', 'parling', 'part-later', 'protusion', 'pursing', 'retraction', 'upward-retraction', 'open']),
            ('nose', ['depression', 'left-dilatation', 'left-elevation', 'right-dilatation', 'right-elevation', 'compression']),
            ('neck', ['platysma']),
            ]

        self.include = "All"

        self.groupBoxes = []
        self.radioButtons = []
        self.sliders = []

        self.modifiers = {}
        self.targets = {}

        self.categoryBox = self.addRightWidget(gui.GroupBox('Category'))
        self.groupBox = self.addLeftWidget(gui.StackedBox())

        for name, subnames in self.expressions:
            # Create box
            box = self.groupBox.addWidget(gui.SliderBox(name.capitalize()))
            self.groupBoxes.append(box)

            # Create sliders
            for subname in subnames:
                if _UseWarping:
                    targetName = name + "-" + subname
                    modifier = ExpressionWarpModifier(targetName)
                else:
                    template = 'data/targets/expression/units/caucasian/%s-%s.target' % (name, subname)
                    modifier = ExpressionSimpleModifier(template)

                modifier.setHuman(gui3d.app.selectedHuman)
                slider = box.addWidget(modifierslider.ModifierSlider(modifier=modifier, label=subname.capitalize()))
                @slider.mhEvent
                def onChange(event):
                    slider = event
                    for target in slider.modifier.targets:
                        self.addTarget(target)
                slider.modifier = modifier
                self.modifiers[name + '-' + subname] = modifier
                self.sliders.append(slider)
                modifier.slider = slider
            # Create radiobutton
            self.categoryBox.addWidget(GroupBoxRadioButton(self, self.radioButtons, name.capitalize(), box, selected=len(self.radioButtons) == 0))

        self.groupBox.showWidget(self.groupBoxes[0])

        # self.hideAllBoxes()
        # self.groupBoxes[0].show()


    def hideAllBoxes(self):
        for box in self.groupBoxes:
            box.hide()


    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        for slider in self.sliders:
            slider.update()
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setFaceCamera()


    def onHumanChanging(self, event):
        if event.change not in ['expression', 'material']:
            self.resetTargets()
            warpmodifier.resetWarpBuffer()


    def addTarget(self, target):
        trgpath,_ = target
        #log.debug("ADD TARGET %s" % trgpath)
        self.targets[trgpath] = True


    def resetTargets(self):
        #log.debug("EXPRESSION RESET %d targets" % len(self.targets))
        if self.targets:
            human = gui3d.app.selectedHuman
            for target in self.targets:
                human.setDetail(target, 0)
            try:
                del algos3d._targetBuffer[target]
            except KeyError:
                pass
            self.targets = {}
            human.applyAllTargets()


    def onHumanChanged(self, event):
        for slider in self.sliders:
            slider.update()


    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        modifier = self.modifiers.get(values[1], None)
        if modifier:
            value = float(values[2])
            modifier.setValue(value)
            modifier.updateValue(value)  # Force recompilation


    def saveHandler(self, human, file):
        for name, modifier in self.modifiers.iteritems():
            value = modifier.getValue()
            if value:
                file.write('expression %s %f\n' % (name, value))


    def loadExpression(self, filename, include):
        human = gui3d.app.selectedHuman
        warpmodifier.resetWarpBuffer()

        if filename:
            from codecs import open
            f = open(filename, 'rU', encoding="utf-8")
            for data in f.readlines():
                lineData = data.split()
                if len(lineData) > 0 and not lineData[0] == '#':
                    if lineData[0] == 'expression':
                        modifier = self.modifiers.get(lineData[1], None)
                        if modifier:
                            value = float(lineData[2])
                            modifier.setValue(value)
                            modifier.updateValue(value)  # Force recompilation


#----------------------------------------------------------
#   class ExpressionAction
#----------------------------------------------------------

class ExpressionAction(gui3d.Action):

    def __init__(self, human, filename, taskView, include):
        super(ExpressionAction, self).__init__('Load expression')
        self.human = human
        self.filename = filename
        self.taskView = taskView
        self.include = include
        self.before = {}

        for name, modifier in self.taskView.modifiers.iteritems():
            self.before[name] = modifier.getValue()

    def do(self):
        task = self.taskView
        task.resetTargets()
        task.loadExpression(self.filename, self.include)
        self.human.applyAllTargets(gui3d.app.progress, True)
        for name in task.modifiers:
            modifier = task.modifiers[name]
            for target in modifier.targets:
                task.addTarget(target)
        for slider in task.sliders:
            slider.update()
        return True

    def undo(self):
        task = self.taskView
        task.resetTargets()
        for name, value in self.before.iteritems():
            modifier = task.modifiers[name]
            modifier.setValue(value)
            task.addTarget(modifier.target)
        self.human.applyAllTargets(gui3d.app.progress, True)
        for slider in task.sliders:
            slider.update()
        return True


#----------------------------------------------------------
#   class ExpressionLoadTaskView
#   class VisemeLoadTaskView
#----------------------------------------------------------

class MhmLoadTaskView(gui3d.TaskView):

    def __init__(self, category, mhmTaskView, mhmLabel, folder):
        gui3d.TaskView.__init__(self, category, mhmLabel, label=mhmLabel)

        self.mhmTaskView = mhmTaskView
        self.include = "All"

        self.globalMhmPath = mh.getSysDataPath(folder)
        self.mhmPath = mh.getPath(os.path.join('data', folder))
        self.paths = [self.globalMhmPath, self.mhmPath]

        if not os.path.exists(self.mhmPath):
            os.makedirs(self.mhmPath)

        #self.filechooser = self.addTopWidget(fc.FileChooser(self.paths, 'mhm', 'thumb'))
        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, 'mhm', 'thumb', notFoundImage=mh.getSysDataPath('notfound.thumb'), name=mhmLabel, noneItem=True, clearImage=os.path.join(self.globalMhmPath, 'clear.thumb')))
        self.filechooser.setIconSize(50,50)
        self.addLeftWidget(self.filechooser.createSortBox())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            gui3d.app.do(ExpressionAction(gui3d.app.selectedHuman, filename, self.mhmTaskView, self.include))

    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setFaceCamera()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)


class ExpressionLoadTaskView(MhmLoadTaskView):

    def __init__(self, category, expressionTaskView):
        MhmLoadTaskView.__init__(self, category, expressionTaskView, 'Expressions', 'expressions')


class VisemeLoadTaskView(MhmLoadTaskView):

    def __init__(self, category, visemeTaskView):
        MhmLoadTaskView.__init__(self, category, visemeTaskView, 'Visemes', 'visemes')

        self.include = []
        for (cat, names) in visemeTaskView.expressions:
            if cat == "mouth":
                for name in names:
                    self.include.append("mouth-" + name)
                break



# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


_UseWarping = True

def load(app):
    category = app.getCategory('Pose/Animate')
    expressionTuning = ExpressionTaskView(category)
    expressionTuning.sortOrder = 8.5
    category.addTask(expressionTuning)

    app.addLoadHandler('expression', expressionTuning.loadHandler)
    app.addSaveHandler(expressionTuning.saveHandler)

    expressionView = ExpressionLoadTaskView(category, expressionTuning)
    expressionView.sortOrder = 8
    category.addTask(expressionView)

    visemeView = VisemeLoadTaskView(category, expressionTuning)
    visemeView.sortOrder = 9
    category.addTask(visemeView)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
