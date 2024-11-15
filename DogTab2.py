from build123d import *
import math
from enum import Enum, auto
from typing import Union, Iterable

av,ap = [Align.CENTER,Align.MIN,Align.MAX],[]
for x in av:
    for y in av: ap.append((x,y))
centre,bottom,top,left,bottomleft,topleft,right,bottomright,topright = ap
center = centre
nil_rot = (0, 0, 0)
sub = Mode.SUBTRACT

# Creates slots and tabs for CNC cut parts

def offsets(length: float, width: float, radius: float, ang: float, inner: bool = True):
    offsets = list((radius * math.sin(ang), radius * math.cos(ang)))
    offsets.sort()
    if length < width: offsets.reverse()
    if inner: return length/2 - offsets[1], width/2 - offsets[0]
    return length/2 + offsets[1], width/2 - offsets[0]

def corner_locs(length: float, width: float, radius: float, ang: float, inner: bool = True, corners: (Align,Align) = centre):
    locs = []
    x,y = offsets(length,width,radius,ang,inner)
    if corners[0] != Align.MIN:
        if corners[1] != Align.MIN: locs.append( ( x, y) )
        if corners[1] != Align.MAX: locs.append( ( x,-y) )
    if corners[0] != Align.MAX:
        if corners[1] != Align.MIN: locs.append( (-x, y) )
        if corners[1] != Align.MAX: locs.append( (-x,-y) )
    return locs

def shifted(w: float,h:float,align: (Align,Align)):
    def centre_shift(d: float, ax: Align):
        if ax == Align.MIN: return d/2
        elif ax == Align.MAX: return -d/2
        else: return 0
    return ((centre_shift(w,align[0]),centre_shift(h,align[1])))

def Tab(
        length,
        width,
        radius=3,
        angle=0,
        align:(Align,Align) = bottom,
        optimal: bool = False,
        nanny: bool = True,
        mode: Mode = Mode.ADD,
        rotation: RotationLike = (0, 0, 0),
        ):

    with Locations(Location((0,0,0),rotation)) as loc:
        Rectangle(length,width,align=align)
        if radius > 0:
            θ = math.radians(angle)
            if optimal:
                θ = math.atan(width/length)
            corners = corner_locs(length,width,radius,θ,inner=False,corners=(align[0],Align.MIN))
            with Locations(shifted(length,width,align)), Locations(corners):
                Circle(radius,mode=sub)

def Slot(
        length,
        width,
        radius = 3,
        angle = 0,
        mode: Mode = sub,
        rotation: RotationLike = nil_rot,
        corners:  (Align,Align) = centre,
        align: (Align,Align) = centre,
        optimal: bool = False,
        nanny: bool = True,
    ):
    with Locations(Location((0,0,0),rotation)):
        Rectangle( length, width, align=align, mode=mode )
        if radius > 0:
            θ = math.radians(angle)
            if optimal:
                θ = math.atan(width/length)
            corners = corner_locs(length,width,radius,θ,inner=True,corners=corners)
            with Locations(shifted(length,width,align)), Locations(corners):
                Circle(radius,mode=mode)

