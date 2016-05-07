#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Argument parser for advanced commandline options, intended to modify the human


**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier, Séverin Lemaignan

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

Adds extra arguments to the arg parser and allows parsing and effecting them on
the human.
"""

import getpath
import sys
import os
import log
import math
import numpy as np

def addModelingArguments(argparser):
    """
    Add commandline options dealing with modeling the human to an existing
    argparse parser object.
    """

    # TODO add range validation on numeric values
    # Macro properties
    macroGroup = argparser.add_argument_group('Macro properties', description="Optional macro properties to set on human")
    macroGroup.add_argument("--age", default=None, type=float, help="Human age, in years")
    macroGroup.add_argument("--gender", default=None, type=float, help="Human gender (0.0: female, 1.0: male)")
    macroGroup.add_argument("--male", action="store_true", help="Produces a male character (overrides the gender argument)")
    macroGroup.add_argument("--female", action="store_true", help="Produces a female character (overrides the gender argument)")
    macroGroup.add_argument("--race", default=None, help="One of [caucasian, asian, african]")
    ##ADD NEW INPUT ARGUMRNTS HERE
    macroGroup.add_argument("--target_height_cm", default=None, type=float, help="Target Height in cms")
    macroGroup.add_argument("--target_waist_cm", default=None, type=float, help="Target Waist in cms")
    macroGroup.add_argument("--target_chest_cm", default=None, type=float, help="Target Chest in cms")
    macroGroup.add_argument("--target_hips_cm", default=None, type=float, help="Target Hips in cms")



    # Modifier parameters
    modGroup = argparser.add_argument_group('Modifiers loading')
    modGroup.add_argument("--listmodifiers", action="store_true", help="List all modifier names")
    modGroup.add_argument("-m","--modifier", nargs=2, metavar=("modifierName","value"), action="append", help="Specify a modifier and its value to apply to the human")

    # Proxies
    proxyGroup = argparser.add_argument_group('Proxy mesh specification')
    proxyGroup.add_argument("--listproxytypes", action="store_true", help="List the available proxy type names")
    modGroup.add_argument("--listproxies", metavar="proxyType", help="List all proxy files of specified proxy type")
    proxyGroup.add_argument("-p","--proxy", nargs=2, metavar=("proxyType","proxyFile"), action="append", help="Load a proxy of a specific type")

    # Rig parameters
    rigGroup = argparser.add_argument_group('Rig settings')
    rigGroup.add_argument("--listrigs", action="store_true", help="List the available rig types")
    rigGroup.add_argument("--rig", metavar="rigType", default=None, help="Setup a rig. (default: none)")

    # Material properties
    matGroup = argparser.add_argument_group('Material settings')
    matGroup.add_argument("--listmaterials", action="store_true", help="List the available skin materials")
    matGroup.add_argument("--material", metavar="materialFile", default=None, help="Specify a skin material to apply to the human")
    # TODO
    matGroup.add_argument("--listproxymaterials", metavar=("proxyType"), help="List the available materials for the specified proxy")
    matGroup.add_argument("--proxymaterial", metavar=("proxyType","materialFile"), nargs=2, default=None, help="Specify a material to apply to the proxy")

    return argparser


def validate(argOptions):
    """
    Perform some validation on the input, print preliminary output and exit if
    required.
    """
    if argOptions.get("male", None):
        argOptions["gender"] = 0.9
    elif argOptions.get("female", None):
        argOptions["gender"] = 0.1

    if argOptions.get('listmodifiers', False):
        import humanmodifier
        modifiers = _loadModifiers(human=None)
        print "Available modifier names:"
        print "\n".join(['  %s\t%s' % (m.fullName, m.description) for m in modifiers])
        sys.exit()

    if argOptions.get('listproxytypes', False):
        import proxy
        print "Available proxy types:"
        for pType in proxy.ProxyTypes:
            if pType == "Proxymeshes":
                desc = "Attach a proxy with an alternative body topology"
                multi = False
            else:
                desc = "Attach %s proxy" % pType.lower()
                multi = not(pType in proxy.SimpleProxyTypes)
            desc = desc + " (%s)" % ("Multiple allowed" if multi else "Only one")
            spacing = '\t' if len(pType) > 5 else '\t\t'
            print "  %s%s%s" % (pType.lower(), spacing, desc)
        sys.exit()

    def _listDataFiles(foldername, extensions, onlySysData=False, recursive=True):
        import getpath
        if onlySysData:
            paths = [getpath.getSysDataPath(foldername)]
        else:
            paths = [getpath.getDataPath(foldername), 
                     getpath.getSysDataPath(foldername)]

        return getpath.search(paths, extensions, recursive)
        

    if argOptions.get('listproxies', None):
        # TODO list and allow loading by UUID too
        import proxy
        proxyType = argOptions['listproxies']
        if proxyType not in [p.lower() for p in proxy.ProxyTypes]:
            raise RuntimeError("Unknown proxy type (%s) passed to --listproxies argument. See --listproxytypes for valid options." % proxyType)
        files = _listDataFiles(proxyType, ['.proxy', '.mhclo'])
        print "Available %s proxies:" % proxyType
        print "\n".join(['  %s' % fname for fname in files])
        sys.exit()

    if argOptions.get('listrigs', False):
        files = _listDataFiles('rigs', ['.json'], onlySysData=True, recursive=False)
        print "Available rigs:"
        print "\n".join(['  %s' % r for r in files])
        sys.exit()

    if argOptions.get('listmaterials', False):
        files = _listDataFiles('skins', ['.mhmat'])
        print "Available materials:"
        print "\n".join(['  %s' % r for r in files])
        sys.exit()

    # TODO
    #if argOptions.get('listproxymaterials', False):
    #    proxyFilePath = ...
    #    files = _listDataFiles(proxyFilePath, ['.mhmat'])
    #    print "Available materials:"
    #    print "\n".join(['  %s' % r for r in files])
    #    sys.exit()


def getMeasure1(human, measure_dict, mode):    
        measure = 0
        vindex1 = measure_dict[0]
        for vindex2 in measure_dict:
            vec = human.meshData.coord[vindex1] - human.meshData.coord[vindex2]
            measure += math.sqrt(vec.dot(vec))
            vindex1 = vindex2

        if mode == 'metric':
            return 10.0 * measure
        else:
            return 10.0 * measure * 0.393700787



def height_conversion(inp_height,height_abs_list):
    min_height = float(height_abs_list[0])
    mid_height = float(height_abs_list[1])
    max_height = float(height_abs_list[2])
    ans = -1

    if inp_height < min_height:
        ans = 0
    elif inp_height >= min_height and inp_height <= mid_height:
        ans = 0.5 * float(inp_height - min_height)/float(mid_height - min_height)
    elif inp_height > mid_height and inp_height <= max_height:
        ans = 0.5 + 0.5*float(inp_height -mid_height)/float(max_height - mid_height)        
    elif inp_height > max_height:
        ans = 1
    return ans        

def waist_conversion(inp_height,height_abs_list):
    min_height = float(height_abs_list[0])
    mid_height = float(height_abs_list[1])
    max_height = float(height_abs_list[2])
    ans = -1
    if inp_height < min_height:
        ans = -1
    elif inp_height >= min_height and inp_height <= mid_height:
        ans = -1 + float(inp_height - min_height)/float(mid_height - min_height)
    elif inp_height > mid_height and inp_height <= max_height:
        ans = float(inp_height -mid_height)/float(max_height - mid_height)        
    elif inp_height > max_height:
        ans = 1
    return ans 


def applyModelingArguments(human, argOptions):
    """
    Apply the commandline argument options parsed by argparse to the human.
    Does nothing if no advanced commandline args were specified.
    """
    ### Macro properties
    if argOptions.get("age", None):
        _selectivelyLoadModifiers(human)
        human.setAgeYears(argOptions["age"])
    if argOptions.get("gender", None):
        _selectivelyLoadModifiers(human)
        human.setGender(argOptions["gender"])
    if argOptions.get("race", None) is not None:
        if argOptions["race"] == "caucasian":
            _selectivelyLoadModifiers(human)
            human.setCaucasian(0.9)
        elif argOptions["race"] == "african":
            _selectivelyLoadModifiers(human)
            human.setAfrican(0.9)
        elif argOptions["race"] == "asian":
            _selectivelyLoadModifiers(human)
            human.setAsian(0.9)
        else:
            raise RuntimeError('Unknown race "%s" specified on commandline. Must be one of [caucasian, african, asian]' % argOptions["race"])

    ### Modifiers (can override some macro parameters set above)
    _selectivelyLoadModifiers(human)
    if argOptions.get("modifier", None) is not None:
        modifiersChanged = False
        alreadyLoaded = human.modifierNames
        

        for mName, value in argOptions["modifier"]:
            for nmx in human.modifierNames:
                if mName in nmx:
                    mName = nmx
                    break
            if mName not in alreadyLoaded:
                # Attempt to load missing modifiers without loading doubles
                _selectivelyLoadModifiers(human)
                alreadyLoaded = human.modifierNames
            try:
                mod_list = human.getModifiers()
                human.getModifier(mName).setValue(value)
                modifiersChanged = True
            except:
                raise RuntimeError('No modifier named "%s" as specified by --modifier command. See --listmodifiers for list of acceptable options.' % mName)
            
        # Update human
        if modifiersChanged:
            human.applyAllTargets()




    


    #ADDED CODE

    my_Measures = {}
    my_Measures['waist'] = [4121,10760,10757,10777,10776,10779,10780,10778,10781,10771,10773,10772,10775,10774,10814,10834,10816,10817,10818,10819,10820,10821,4181,4180,4179,4178,4177,4176,4175,4196,4173,4131,4132,4129,4130,4128,4138,4135,4137,4136,4133,4134,4108,4113,4118,4121]
    my_Measures['chest']=[8439,8455,8462,8446,8478,8494,8557,8510,8526,8542,10720,10601,10603,10602,10612,10611,10610,10613,10604,10605,10606,3942,3941,3940,3950,3947,3948,3949,3938,3939,3937,4065,1870,1854,1838,1885,1822,1806,1774,1790,1783,1767,1799,8471]
    my_Measures['neckcirc'] = [7514,10358,7631,7496,7488,7489,7474,7475,7531,7537,7543,7549,7555,7561,7743,7722,856,1030,1051,850,844,838,832,826,820,756,755,770,769,777,929,3690,804,800,808,801,799,803,7513,7515,7521,7514]
    my_Measures['hips'] = [4341,10968,10969,10971,10970,10967,10928,10927,10925,10926,10923,10924,10868,10875,10861,10862,4228,4227,4226,4242,4234,4294,4293,4296,4295,4297,4298,4342,4345,4346,4344,4343,4361,4341]



    target_height_cm = argOptions["target_height_cm"]  
    # ['macrodetails-height/Height','measure/measure-waist-decrease','measure/measure-bust-decrease']      
    height_modifier = 'macrodetails-height/Height'

    height_list = [0,0.5,1]
    height_abs_list = []
    
    
        
    for cur_height in height_list:
        _selectivelyLoadModifiers(human) ##maatiki unchutunna
        human.getModifier(height_modifier).setValue(cur_height)
        human.applyAllTargets()
        height_abs_list.append(human.getHeightCm())
        
   
    height_value = height_conversion(target_height_cm,height_abs_list)


    human.getModifier(height_modifier).setValue(height_value)
    human.applyAllTargets()

    print(human.getHeightCm(),target_height_cm)

    
    target_waist_cm = argOptions["target_waist_cm"]  
    # ['macrodetails-height/Height','measure/measure-waist-decrease','measure/measure-bust-decrease']      
    waist_modifier = 'measure/measure-waist-decrease' ## what is decrease and increase ?

    waist_list = [-1,0,1]
    waist_abs_list = []
    
    for nmx in human.modifierNames:
        if waist_modifier in nmx:
            waist_modifier = nmx
            break

    if waist_modifier not in human.modifierNames:
        _selectivelyLoadModifiers(human)


    for cur_waist in waist_list:
        human.getModifier(waist_modifier).setValue(cur_waist)
        human.applyAllTargets()
        waist_abs_list.append(getMeasure1(human,my_Measures['waist'],'metric'))
        
    waist_value = waist_conversion(target_waist_cm,waist_abs_list)


    human.getModifier(waist_modifier).setValue(waist_value)
    human.applyAllTargets()
    
    print(getMeasure1(human,my_Measures['waist'],'metric'),target_waist_cm)


    ##CHEST 
    target_chest_cm = argOptions["target_chest_cm"]  
    # ['macrodetails-height/Height','measure/measure-waist-decrease','measure/measure-bust-decrease']      
    chest_modifier = 'measure/measure-bust-decrease' ## what is decrease and increase ?

    chest_list = [-1,0,1]
    chest_abs_list = []
    
    for nmx in human.modifierNames:
        if chest_modifier in nmx:
            chest_modifier = nmx
            break

    if chest_modifier not in human.modifierNames:
        _selectivelyLoadModifiers(human)


    for cur_chest in chest_list:
        human.getModifier(chest_modifier).setValue(cur_chest)
        human.applyAllTargets()
        chest_abs_list.append(getMeasure1(human,my_Measures['chest'],'metric'))
        
    chest_value = waist_conversion(target_chest_cm,chest_abs_list)


    human.getModifier(chest_modifier).setValue(chest_value)
    human.applyAllTargets()

    
    print(getMeasure1(human,my_Measures['chest'],'metric'),target_chest_cm)

    target_hips_cm = argOptions["target_hips_cm"]  
    # ['macrodetails-height/Height','measure/measure-waist-decrease','measure/measure-bust-decrease']      
    hips_modifier = 'measure/measure-hips-decrease' ## what is decrease and increase ?

    hips_list = [-1,0,1]
    hips_abs_list = []
    
    for nmx in human.modifierNames:
        if hips_modifier in nmx:
            hips_modifier = nmx
            break

    if hips_modifier not in human.modifierNames:
        _selectivelyLoadModifiers(human)


    for cur_hips in hips_list:
        human.getModifier(hips_modifier).setValue(cur_hips)
        human.applyAllTargets()
        hips_abs_list.append(getMeasure1(human,my_Measures['hips'],'metric'))
        
    hips_value = waist_conversion(target_hips_cm,hips_abs_list)


    human.getModifier(hips_modifier).setValue(hips_value)
    human.applyAllTargets()
    
    print(getMeasure1(human,my_Measures['hips'],'metric'),target_hips_cm)



        

    




    # ### Skeleton
    # if argOptions.get("rig", None):
    #     addRig(human, argOptions['rig'])

    # def _isMultiProxy(proxyType):
    #     if proxyType == "Proxymeshes":
    #         return False
    #     import proxy
    #     return not(proxyType in proxy.SimpleProxyTypes)

    # ### Proxies
    # proxies = argOptions.get("proxy", None)
    # if proxies is not None:
    #     appliedSimpleTypes = []
    #     for proxyType, proxyFile in proxies:
    #         import proxy
    #         if proxyType not in [p.lower() for p in proxy.ProxyTypes]:
    #             raise RuntimeError('Error in --proxy argument! Proxy type "%s" unknown, see --listproxytypes for the allowed options.' % proxyType)
    #         if not _isMultiProxy(proxyType):
    #             if proxyType in appliedSimpleTypes:
    #                 raise RuntimeError('Error in --proxy argument! Only one instance of proxy type "%s" is allowed.' % proxyType)
    #             appliedSimpleTypes.append(proxyType)
    #         addProxy(human, proxyFile, proxyType)
    #     del appliedSimpleTypes


    # ### Material
    # if argOptions.get("material", None):
    #     applyMaterial(argOptions["material"], human)


    # ### Proxy material
    # # TODO
    # #if argOptions.get("proxymaterial", None):
    # #    applyMaterial(argOptions["material"], proxyObj)


    # # TODO perhaps allow disabling this option (default to off?)
    # # Set a suiting default material based on predominant gender and ethnic properties
    # if not argOptions.get('material', None) and human.getDominantGender() and human.getEthnicity():
    #     matFile = 'data/skins/young_%(race)s_%(gender)s/young_%(race)s_%(gender)s.mhmat' % {
    #         "race": human.getEthnicity(), 
    #         "gender": human.getDominantGender() }

    #     try:
    #         applyMaterial(matFile, human)
    #     except:
    #         log.error('Auto-apply Material file "%s" does not exist.', matFile)


def addProxy(human, mhclofile, type):
    # TODO if eyes proxy is loaded, the one loaded by default should be removed

    if not os.path.isfile(mhclofile):
        mhclofile = getpath.findFile(mhclofile, 
                                     searchPaths = [getpath.getDataPath(), 
                                                    getpath.getSysDataPath(),
                                                    getpath.getPath(),
                                                    getpath.getSysPath()])
        if not os.path.isfile(mhclofile):
            #log.error("Proxy file %s does not exist (%s).", mhclofile, type)
            #return
            raise RuntimeError('Proxy file "%s" does not exist (%s).' % (mhclofile, type))

    import proxy
    _proxy = proxy.readProxyFile(human, mhclofile, type=type.capitalize())

    if type == "proxymeshes":
        human.setProxy(_proxy)
        return

    mesh,obj = _proxy.loadMeshAndObject(human)

    if not mesh:
        raise RuntimeError('Failed to load proxy mesh "%s"', _proxy.obj_file)

    def _adaptProxyToHuman(pxy, obj):
        mesh = obj.getSeedMesh()
        pxy.update(mesh)
        mesh.update()
        # Update subdivided mesh if smoothing is enabled
        if obj.isSubdivided():
            obj.getSubdivisionMesh()

    _adaptProxyToHuman(_proxy, obj)

    # TODO oh so tedious...
    if type == "hair":
        human.hairProxy = _proxy
        human.hairObj = obj
    elif type == "eyes":
        human.eyesProxy = _proxy
        human.eyesObj = obj
    elif type == "genitals":
        human.genitalsProxy = _proxy
        human.genitalsObj = obj
    elif type == "eyebrows":
        human.eyebrowsProxy = _proxy
        human.eyebrowsObj = obj
    elif type == "eyelashes":
        human.eyelashesProxy = _proxy
        human.eyelashesObj = obj
    elif type == "teeth":
        human.teethProxy = _proxy
        human.teethObj = obj
    elif type == "tongue":
        human.tongueProxy = _proxy
        human.tongueObj = obj
    elif type == "clothes":
        human.clothesProxies[_proxy.uuid] = _proxy
        human.clothesObjs[_proxy.uuid] = obj

def addRig(human, rigfile):
    if not os.path.isfile(rigfile):
        rigfile = getpath.findFile(rigfile, 
                                   searchPaths = [getpath.getSysDataPath(),
                                                  getpath.getSysPath()])
        if not os.path.isfile(rigfile):
            #log.error("Rig file %s does not exist.", mhclofile)
            #return
            raise RuntimeError('Rig file "%s" does not exist.' % mhclofile)

    import skeleton
    from armature.options import ArmatureOptions

    armature_options = ArmatureOptions()

    descr = armature_options.loadPreset(rigfile, None)    # TODO update skeleton library when in gui mode
    # Load skeleton definition from options
    human._skeleton, boneWeights = skeleton.loadRig(armature_options, human.meshData)
    human._skeleton.options = armature_options

    # TODO this should be resolved in the future
    def skeleton_getter():
        return human._skeleton
    human.getSkeleton = skeleton_getter

def applyMaterial(matFile, obj):
    if not os.path.isfile(matFile):
        matFile = getpath.findFile(matFile, 
                                   searchPaths = [getpath.getDataPath(), 
                                                  getpath.getSysDataPath(),
                                                  getpath.getPath(),
                                                  getpath.getSysPath()])
    if not os.path.isfile(matFile):
        raise RuntimeError('Material file "%s" does not exist.', matFile)
    else:
        import material
        obj.material = material.fromFile( matFile )


def _loadModifiers(human):
    """
    Load modifiers from file. Set human to None to not assign them to a human.
    """
    import humanmodifier
    modifiers = humanmodifier.loadModifiers(getpath.getSysDataPath('modifiers/modeling_modifiers.json'), human)
    ## COMMENT - adds measurement modifiers - earlier 207 now 226 because of the extension
    modifiers.extend(humanmodifier.loadModifiers(getpath.getSysDataPath('modifiers/measurement_modifiers.json'), human))
    return modifiers

mods_loaded = False
def _selectivelyLoadModifiers(human):
    """
    Load modifiers if they're not already loaded.
    Only add missing ones.
    """
    global mods_loaded
    if mods_loaded:
        return
    modifiers = _loadModifiers(human=None)
    alreadyLoaded = human.modifierNames
    for m in modifiers:
        if m.fullName not in alreadyLoaded:
            m.setHuman(human)
    mods_loaded = True

