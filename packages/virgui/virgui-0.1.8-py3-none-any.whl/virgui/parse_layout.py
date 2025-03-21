import importlib.resources
from dataclasses import dataclass
from pathlib import Path

import finesse

# import xml.etree.ElementTree as ET
import lxml.etree

import virgui

LAYOUTS = Path(str(importlib.resources.files(virgui))) / "layouts"
PREFIX = "finesse_hitbox_"


@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float


hitbox_mapping: dict[str, Rect] = {}


def parse_layout(layout_dir: Path) -> tuple[finesse.Model, dict[str, Rect], bytes]:
    assert layout_dir.exists()
    kat_file = layout_dir / "layout.kat"
    assert kat_file.exists()
    svg_file = layout_dir / "layout.svg"
    assert svg_file.exists()

    model: finesse.Model = finesse.script.parse_file(kat_file)
    tree = lxml.etree.parse(svg_file, lxml.etree.XMLParser())
    root = tree.getroot()

    # I don't know if this viewbox thing is always added by inkscape or something more general
    svg_width = float(root.attrib["width"])
    svg_height = float(root.attrib["height"])
    viewbox = [float(val) for val in root.attrib["viewBox"].split()]
    viewbox_width = viewbox[2] - viewbox[0]
    viewbox_height = viewbox[3] - viewbox[1]
    x_scaling = svg_width / viewbox_width
    y_scaling = svg_height / viewbox_height

    # we just look for anything with the 'finesse_hitbox_<component_name> value
    # and look for x,y,width,height?
    for el in root.iter():
        hitbox = None
        for key, val in el.attrib.items():
            if val.startswith(PREFIX):
                hitbox = val
        if not hitbox:
            continue

        for attr in ("x", "y", "width", "height"):
            assert attr in el.attrib

        hitbox_mapping[hitbox.split(PREFIX)[-1]] = Rect(
            x=float(el.attrib["x"]) * x_scaling,
            y=float(el.attrib["y"]) * y_scaling,
            width=float(el.attrib["width"]) * x_scaling,
            height=float(el.attrib["height"]) * y_scaling,
        )
        parent = el.getparent()
        parent.remove(el)

    # all models have an fsig element, but should not be present in the svg
    diff = set(el for el in model.elements if el != "fsig").symmetric_difference(
        set(hitbox_mapping.keys())
    )
    if len(diff):
        raise ValueError(f"Hitbox mapping and model elements dont match: {diff}")

    # render whole svg / component layer to png? or render svg directly in QT?
    # TODO maybe check size?
    # click get coordinates and find correct element
    return model, hitbox_mapping, lxml.etree.tostring(tree)
