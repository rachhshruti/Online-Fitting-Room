#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
PIL (Pyhon Imaging Library) back-end for image loading.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

Alternative to the default Qt image loader.
"""

import PIL.Image as img
import numpy as np

_modes = {
    'L': 1,
    'LA': 2,
    'RGB': 3,
    'RGBA': 4
    }
         
def load(path):
    image = img.open(path)
    return fromPILImage(image)

def save(path, data):
    h, w, d = data.shape
    mode = [None,'L','LA','RGB','RGBA'][d]
    image = img.fromstring(mode, (w, h), data.tostring())
    image.save(path)

def toPILImage(imgobj):
    if not hasattr(img, 'fromstring'):
        raise RuntimeError('Failed to use PIL "fromstring". Requires PIL version 1.1.4 or higher.')
    if imgobj.components == 4:
        mode = 'RGBA'
    else:
        mode = 'RGB'
    print len (imgobj.data.tostring()), imgobj.width, imgobj.height, imgobj.components 
    return img.fromstring(mode, (imgobj.width, imgobj.height), 
                          imgobj.data.tostring())

def fromPILImage(pilImg):
    if pilImg.mode not in ("L", "RGB", "RGBA"):
        pilImg = pilImg.convert("RGBA")

    w, h = pilImg.size
    d = _modes[pilImg.mode]
    pixels = pilImg.tostring("raw", pilImg.mode)
    data = np.fromstring(pixels, dtype=np.uint8).reshape((h,w,d))
    return data

def resized(imgobj, width, height, filter=filter):
    pImg = toPILImage(imgobj)
    if filter == 0:
        transform = img.NEAREST
    elif filter == 1:
        transform = img.BILINEAR
    elif filter == 2:
        transform = img.BICUBIC
    else:
        transform = img.ANTIALIAS
    pImg = pImg.resize((width, height), transform)
    return fromPILImage(pImg)

