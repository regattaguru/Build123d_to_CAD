from build123d import *
import math
import json
import sys
import copy
import DogTab2 as dt
from types import SimpleNamespace

sheet_thickness = 6
tab_len = 20
bit_radius = 3

beam_len = 800
beam_height = 150
beam_width = 150

side_inset = sheet_thickness
end_web_inset = sheet_thickness * 2

min_tab_spacing = 150
min_web_spacing = 200

# Some calculated vars to make the rest read more clearly
side_height = beam_height - sheet_thickness * 2
web_width = beam_width - side_inset * 2 - sheet_thickness * 2

tabs = int(beam_len / min_tab_spacing)

webs = int((beam_len - end_web_inset * 2) / min_web_spacing)
web_spacing = (beam_len - end_web_inset * 2 - sheet_thickness) / (webs - 1)

web_locs = GridLocations(web_spacing,0,webs,1)

exporter = ExportDXF(unit=Unit.MM, version='AC1032', line_weight=0.15)
exporter.add_layer("Profiles", line_type=LineType.CONTINUOUS)
exporter.add_layer("Interior", line_type=LineType.CONTINUOUS)

dxf_x = beam_len/2
dxf_y = beam_width/2

comp = Compound(label="Box beam")

# Separate sketch of holes - will be 'added' to profile in next step
with BuildSketch() as top_inners:
    with GridLocations(beam_len / tabs, beam_width - side_inset * 2 - sheet_thickness,tabs,2):
        dt.Slot(tab_len,sheet_thickness,mode=Mode.ADD,radius=bit_radius,rotation=0,optimal=True)
    with web_locs:
        dt.Slot(tab_len,sheet_thickness,mode=Mode.ADD,radius=bit_radius,rotation=90,optimal=True)

with BuildPart() as top_builder:
    with BuildSketch() as top_sketch:
        # Profile is just a rectangle in this case
        Rectangle(beam_len,beam_width)
        for i in range(2):
            # Place sketch of profile and sketch of holes on separate layers for easier processing
            exporter.add_shape(top_sketch.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Profiles")
            exporter.add_shape(top_inners.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Interior")
            # Using an incrementing x and y counter makes placement easier
            dxf_y += beam_width + 20
        # Finally, subtract the holes from the profile before extruding into a part
        add(top_inners,mode=Mode.SUBTRACT)

    extrude(amount=sheet_thickness)
    # Add to componenet
    top_builder.part.parent = comp
    # Copy to reproduce in the 3d model
    copy.copy(top_builder.part).located(Location((0,0,beam_height - sheet_thickness),(0,0,0))).parent = comp

# Create sketch of holes for the side. Note setting mode to ADD.
with BuildSketch() as side_inners:
    with web_locs:
        dt.Slot(tab_len,sheet_thickness,mode=Mode.ADD,radius=bit_radius,rotation=90,optimal=True)

with BuildPart() as side_builder:
    with BuildSketch() as side_sketch:
        Rectangle(beam_len,side_height)
        with GridLocations(beam_len / tabs, 0,tabs,1):
            with Locations(
                    Location((0,side_height/2,0),(0,0,0)),
                    Location((0,-side_height/2,0),(0,0,180))
                    ):
                dt.Tab(tab_len,sheet_thickness,radius=bit_radius,rotation=0,optimal=True)
        # Before combining holes with the profile, put the two sketches on separate layers in the DXF
        exporter.add_shape(side_sketch.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Profiles")
        exporter.add_shape(side_inners.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Interior")
        dxf_y += beam_width + 20
        exporter.add_shape(side_sketch.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Profiles")
        exporter.add_shape(side_inners.sketch.located(Location((dxf_x,dxf_y,0),(0,0,0))), layer="Interior")
        # Now combine the two sketches before extruding into a part.
        add(side_inners,mode=Mode.SUBTRACT)
    extrude(amount=sheet_thickness)
    side_builder.part.located(Location((0,-beam_width/2 + sheet_thickness + side_inset,side_height/2 + sheet_thickness),(90,0,0))).parent = comp
    side_builder.part.located(Location((0,beam_width/2 - side_inset,side_height/2 + sheet_thickness),(90,0,0))).parent = comp

with BuildPart() as web_builder:
    with BuildSketch() as web_sketch:
        Rectangle(web_width,side_height)
        with PolarLocations(web_width/2,2):
            dt.Tab(tab_len,sheet_thickness,radius=bit_radius,rotation=-90,optimal=True)
        with PolarLocations(side_height/2,2,start_angle=90):
            dt.Tab(tab_len,sheet_thickness,radius=bit_radius,rotation=-90,optimal=True)
    extrude(amount=sheet_thickness)
    for loc in web_locs.locations:
        loc.position = (loc.position.X - sheet_thickness/2, loc.position.Y, beam_height/2)
        loc.orientation = (0,90,90)
        web_builder.part.located(loc).parent = comp

    dxf_y = beam_height / 2
    dxf_x = beam_len + beam_width / 2 + 50
    for i in range(webs): 
        exporter.add_shape(web_sketch.sketch.located(Location((dxf_x, dxf_y,0),(0,0,0))), layer="Profiles")
        dxf_y += beam_height + 20
        
try:
    show_object(comp)
except:
    print("CQ Editor not found")
    pass

try:
    exporter.write("example.dxf")
    comp.export_step("example.step")
except:
    print("Exporter error")
