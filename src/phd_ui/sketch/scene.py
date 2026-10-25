"""
SVG scenes for schematic drawings: surfaces, particles, sites.

A sketch is written as SVG directly rather than through matplotlib, because
it is meant to be opened, read and finished by hand. The file is kept
readable for a person and for an AI: every panel is a named layer, every
part of a panel (support, particles, defects, sites, labels) a named group,
atoms are references to one shared definition per element and state, and
all colours sit in one style block at the top, generated from
:data:`phd_ui.colors.ATOMS`. Change a colour there and every sketch follows
on the next run.

Coordinates
-----------
User units are **picometres**, so a coordinate in the file is a distance on
the drawn surface and atom radii are the covalent radii of
:data:`~phd_ui.colors.ATOMS`. ``pm_per_mm`` fixes the print scale: the
``<svg>`` carries its final width and height in mm, and the ``viewBox`` the
same box in pm. **y grows downwards**, as in every SVG: a surface is a y
value and the bulk lies below it.

Text and line widths are given in pt at final size and converted, so 8 pt
in a sketch is 8 pt on the page, the same as in a ``phd_ui`` figure of the
same preset. Slide presets double everything, as ``SLIDE_SCALE`` does for
figures.

Finishing by hand
-----------------
A generated SVG is regenerated, not edited. Place it in an Illustrator or
Inkscape document and add arrows, callouts and annotations on a layer of
your own there. Illustrator rewrites SVG on save (``cls-1``, ``cls-2``, ...)
and drops the group structure this module writes, so a sketch saved back
from Illustrator can no longer be regenerated.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from collections.abc import Iterable

from phd_ui.colors.atoms import SIZE_EXPONENT, drawn_radius_pm, get_atom, get_ion
from phd_ui.colors.scheme import BLUE, GREY, INK

__all__ = [
    "PANEL_PARTS",
    "Group",
    "Panel",
    "Scene",
]

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)

#: mm per typographic point.
MM_PER_PT: float = 25.4 / 72

#: Font family of every text element, as in the figures.
FONT_FAMILY: str = "'Source Sans 3', 'Source Sans Pro', sans-serif"

#: The groups of a panel, bottom to top. A group is created when first used
#: and always lands at its place in this order, so z-order never depends on
#: the order of the calls that drew into it.
PANEL_PARTS: tuple[str, ...] = ("support", "particles", "adsorbates", "defects", "sites", "labels")

#: Parts of a panel that are clipped to its frame. Labels may sit outside.
_CLIPPED_PARTS: frozenset[str] = frozenset({"support", "particles", "adsorbates", "defects", "sites"})

#: Atom states. ``plain`` is the element as drawn in ATOMS, ``ox`` the oxidised rim or
#: interface tint of :data:`~phd_ui.colors.ATOMS` (lighter fill, dashed edge).
STATES: tuple[str, ...] = ("plain", "ox")


def _ns(tag: str) -> str:
    return f"{{{SVG_NS}}}{tag}"


def _num(value: float) -> str:
    """A coordinate with one decimal and no trailing zeros: pm, so 0.1 pm is plenty."""
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _safe_id(name: str) -> str:
    """Make `name` a valid XML id: letters first, no spaces."""
    text = re.sub(r"[^A-Za-z0-9_.-]", "-", name)
    return text if re.match(r"[A-Za-z_]", text) else f"p{text}"


class Group:
    """
    A named ``<g>`` in a scene.

    Parameters
    ----------
    scene : Scene
        The scene this group belongs to.
    element : xml.etree.ElementTree.Element
        The ``<g>`` element itself.
    """

    def __init__(self, scene: Scene, element: ET.Element) -> None:
        self.scene = scene
        self.element = element

    @property
    def id(self) -> str:
        """The group's id in the file."""
        return self.element.get("id", "")

    def add(self, tag: str, attrs: dict[str, str] | None = None, text: str | None = None) -> ET.Element:
        """
        Append a raw SVG element.

        Parameters
        ----------
        tag : str
            SVG tag without namespace, e.g. ``'circle'``.
        attrs : dict of str to str, optional
            Attributes, already formatted.
        text : str, optional
            Text content.

        Returns
        -------
        xml.etree.ElementTree.Element
            The new element.
        """
        el = ET.SubElement(self.element, _ns(tag), attrs or {})
        if text is not None:
            el.text = text
        return el

    def group(self, name: str) -> Group:
        """
        Append a child group with the id ``<this id>.<name>``.

        Parameters
        ----------
        name : str
            Short name of the child, e.g. ``'island-left'``.

        Returns
        -------
        Group
            The child group.
        """
        el = ET.SubElement(self.element, _ns("g"), {"id": self.scene._unique_id(f"{self.id}.{name}")})
        return Group(self.scene, el)

    def atom(self, symbol: str, x: float, y: float, state: str = "plain") -> None:
        """
        Place one atom, a reference to the shared definition of its element.

        Parameters
        ----------
        symbol : str
            Element symbol, a key of :data:`~phd_ui.colors.ATOMS`.
        x, y : float
            Centre, in pm.
        state : {'plain', 'ox'}, optional
            ``'ox'`` draws the oxidised tint with a dashed edge.
        """
        ref, r = self.scene._atom_def(symbol, state)
        ET.SubElement(self.element, _ns("use"), {
            f"{{{XLINK_NS}}}href": f"#{ref}",
            "x": _num(x - r), "y": _num(y - r), "width": _num(2 * r), "height": _num(2 * r),
        })


class Panel:
    """
    One panel of a scene: a frame, a title, and its parts as named groups.

    Content is drawn in panel coordinates, (0, 0) at the top-left corner of
    the frame, so a panel can be moved or copied into another scene without
    touching its contents. Get a part with :meth:`part`.

    Parameters
    ----------
    scene : Scene
        The parent scene.
    name : str
        Panel identifier, also its layer name, e.g. ``'10CuGa'``.
    element : xml.etree.ElementTree.Element
        The panel's layer ``<g>``.
    width, height : float
        Frame size, in pm.
    """

    def __init__(self, scene: Scene, name: str, element: ET.Element, width: float, height: float) -> None:
        self.scene = scene
        self.name = name
        self.element = element
        self.width = width
        self.height = height
        self._parts: dict[str, Group] = {}
        self._art: ET.Element | None = None

    @property
    def id(self) -> str:
        """The panel's id in the file."""
        return self.element.get("id", "")

    def part(self, name: str) -> Group:
        """
        The group for one part of the panel, created on first use.

        Parameters
        ----------
        name : str
            One of :data:`PANEL_PARTS`.

        Returns
        -------
        Group
            The part, placed at its fixed position in the drawing order.

        Raises
        ------
        KeyError
            If `name` is not a known part.
        """
        if name not in PANEL_PARTS:
            raise KeyError(f"Unknown panel part '{name}'. Known: {', '.join(PANEL_PARTS)}.")
        if name in self._parts:
            return self._parts[name]
        parent = self._art_group() if name in _CLIPPED_PARTS else self.element
        el = ET.Element(_ns("g"), {"id": _safe_id(f"{self.id}.{name}")})
        el.set(f"{{{INKSCAPE_NS}}}label", name)
        # insert before the first sibling part that comes later in PANEL_PARTS
        rank = PANEL_PARTS.index(name)
        index = len(parent)
        for i, child in enumerate(parent):
            label = child.get(f"{{{INKSCAPE_NS}}}label")
            if label in PANEL_PARTS and PANEL_PARTS.index(label) > rank:
                index = i
                break
        parent.insert(index, el)
        group = Group(self.scene, el)
        self._parts[name] = group
        return group

    def _art_group(self) -> ET.Element:
        if self._art is None:
            self._art = ET.Element(_ns("g"), {"id": _safe_id(f"{self.id}.art"),
                                              "clip-path": f"url(#{_safe_id(self.id + '.clip')})"})
            # the clipped art goes first: under the frame, the title and the labels
            self.element.insert(0, self._art)
        return self._art


class Scene:
    """
    An SVG drawing at its final size, in picometre user units.

    Parameters
    ----------
    width_mm, height_mm : float
        Final size of the drawing, in mm.
    pm_per_mm : float, optional
        Drawing scale: how many pm of surface one mm on the page shows.
        At 65, a Cu atom (132 pm) is 4.1 mm across.
    scale : float, optional
        Multiplier on every point size (text, line widths, dashes): 1 for
        print, ``SLIDE_SCALE`` (2) for slides. :meth:`from_figsize` sets it
        from the preset key.
    title : str, optional
        Written to ``<title>``; for a reader of the file, not drawn.
    source : str, optional
        What made the file, e.g. the notebook path; written to ``<desc>``.
    ions : iterable of str, optional
        Ions whose elements are drawn at their ionic radius from
        :data:`~phd_ui.colors.IONS`, e.g. ``('Ga3+', 'O2-')`` for an oxide
        lattice. Elements not listed keep the covalent radius, so a metal
        beside the oxide stays as it is.
    radii : dict of str to float, optional
        Drawn radius per element in pm, taken as is (not compressed),
        overriding both of the above.
    size_exponent : float, optional
        Size compression of the atom convention (``SIZE_EXPONENT``, 0.5):
        size differences are indicated, not to scale. 1.0 draws true radii.
    """

    def __init__(
        self,
        width_mm: float,
        height_mm: float,
        pm_per_mm: float = 65.0,
        scale: float = 1.0,
        title: str = "",
        source: str = "",
        ions: Iterable[str] = (),
        radii: dict[str, float] | None = None,
        size_exponent: float = SIZE_EXPONENT,
    ) -> None:
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.pm_per_mm = pm_per_mm
        self.scale = scale
        self.ions = tuple(ions)
        self.size_exponent = size_exponent
        self._true = {get_ion(k).symbol: get_ion(k).radius_pm for k in self.ions}
        if len(self._true) != len(self.ions):
            raise ValueError(f"Two ions of one element in {self.ions}: one radius per element per scene.")
        self.radii = dict(radii or {})
        self.width = width_mm * pm_per_mm
        self.height = height_mm * pm_per_mm
        self.root = ET.Element(_ns("svg"), {
            "version": "1.1",
            "width": f"{_num(width_mm)}mm",
            "height": f"{_num(height_mm)}mm",
            "viewBox": f"0 0 {_num(self.width)} {_num(self.height)}",
        })
        if title:
            ET.SubElement(self.root, _ns("title")).text = title
        desc = "phd_ui.sketch; user units are pm"
        if self.ions:
            desc += "; ionic radii (Shannon 1976) for " + ", ".join(self.ions)
        if source:
            desc += f"; made by {source}"
        ET.SubElement(self.root, _ns("desc")).text = desc
        self._style = ET.SubElement(self.root, _ns("style"))
        self._defs = ET.SubElement(self.root, _ns("defs"))
        self._atom_defs: dict[tuple[str, str], tuple[str, float]] = {}
        self._panels: dict[str, Panel] = {}
        self._vacancy_symbols: set[str] = set()
        self._ids: set[str] = set()

    def _unique_id(self, name: str) -> str:
        """A valid id from `name`, suffixed ``-2``, ``-3``, ... if already taken."""
        base = _safe_id(name)
        candidate, n = base, 1
        while candidate in self._ids:
            n += 1
            candidate = f"{base}-{n}"
        self._ids.add(candidate)
        return candidate

    @classmethod
    def from_figsize(cls, key: str, height_mm: float | None = None, **kwargs: object) -> Scene:
        """
        A scene as wide as a ``phd_ui`` figure preset.

        Parameters
        ----------
        key : str
            Figure-size key, e.g. ``'double'`` or ``'slide_half'``.
        height_mm : float, optional
            Height in mm. By default the preset's height; the width always
            comes from the preset, so a sketch shares a column with figures.
        **kwargs
            Passed on to :class:`Scene`.

        Returns
        -------
        Scene
            The scene, with ``scale`` set from the key (2 for slides).
        """
        from phd_ui.plotting.figsize import get_figsize
        from phd_ui.plotting.params import scale_for_key

        w_cm, h_cm = get_figsize(key, in_metric=True)
        kwargs.setdefault("scale", scale_for_key(key))
        return cls(w_cm * 10, height_mm if height_mm is not None else h_cm * 10, **kwargs)  # type: ignore[arg-type]

    # -- units --------------------------------------------------------------

    def pt(self, value: float) -> float:
        """
        Convert a size in pt at final size to user units (pm).

        Parameters
        ----------
        value : float
            Size in pt, at print scale; :attr:`scale` is applied here.

        Returns
        -------
        float
            The same size in pm.
        """
        return value * self.scale * MM_PER_PT * self.pm_per_mm

    def mm(self, value: float) -> float:
        """
        Convert a length in mm on the page to user units (pm).

        Parameters
        ----------
        value : float
            Length in mm.

        Returns
        -------
        float
            The same length in pm.
        """
        return value * self.pm_per_mm

    def radius(self, symbol: str) -> float:
        """
        Drawn radius of an element, in pm.

        Parameters
        ----------
        symbol : str
            Element symbol.

        Returns
        -------
        float
            The override from `radii` as given; else the ionic radius if the
            element is in `ions`, else the covalent radius, both compressed
            by `size_exponent`.
        """
        if symbol in self.radii:
            return self.radii[symbol]
        true = self._true.get(symbol, get_atom(symbol).radius_pm)
        return drawn_radius_pm(true, self.size_exponent)

    # -- structure ----------------------------------------------------------

    def layer(self, name: str) -> Group:
        """
        A top-level layer outside any panel (arrows between panels, a key).

        Parameters
        ----------
        name : str
            Layer name and id.

        Returns
        -------
        Group
            The layer.
        """
        el = ET.SubElement(self.root, _ns("g"), {"id": _safe_id(name)})
        el.set(f"{{{INKSCAPE_NS}}}groupmode", "layer")
        el.set(f"{{{INKSCAPE_NS}}}label", name)
        return Group(self, el)

    def panel(self, name: str, x: float, y: float, width: float, height: float,
              title: str | None = None, frame: bool = True) -> Panel:
        """
        Add a panel as its own layer.

        Parameters
        ----------
        name : str
            Panel identifier: layer name, id stem (``panel-<name>``).
        x, y : float
            Top-left corner of the frame in the scene, in pm.
        width, height : float
            Frame size, in pm.
        title : str, optional
            Panel identifier drawn centred above the frame. Markup as in
            :meth:`text`. A panel identifier is not a figure title, which
            this module never draws.
        frame : bool, optional
            Draw the frame outline.

        Returns
        -------
        Panel
            The panel; draw into it with ``panel.part('support')`` etc.
        """
        pid = _safe_id(f"panel-{name}")
        el = ET.SubElement(self.root, _ns("g"), {"id": pid, "transform": f"translate({_num(x)} {_num(y)})"})
        el.set(f"{{{INKSCAPE_NS}}}groupmode", "layer")
        el.set(f"{{{INKSCAPE_NS}}}label", name)
        clip = ET.SubElement(self._defs, _ns("clipPath"), {"id": _safe_id(f"{pid}.clip")})
        ET.SubElement(clip, _ns("rect"), {"width": _num(width), "height": _num(height)})
        frame_el = ET.Element(_ns("rect"), {"id": f"{pid}.frame", "class": "frame",
                                            "width": _num(width), "height": _num(height)})
        if frame:
            el.append(frame_el)
        panel = Panel(self, name, el, width, height)
        if title:
            self._text(el, width / 2, -self.pt(6), title, "title", "middle", id_=f"{pid}.title")
        self._panels[name] = panel
        return panel

    # -- text ---------------------------------------------------------------

    def text(self, group: Group, x: float, y: float, text: str, kind: str = "label",
             anchor: str = "start") -> ET.Element:
        """
        Write text, with ``_`` and ``^`` for sub- and superscripts.

        Parameters
        ----------
        group : Group
            Where the text goes, usually ``panel.part('labels')``.
        x, y : float
            Anchor point (baseline), in pm.
        text : str
            Plain text with light markup: ``GaO_x``, ``Cu^{δ+}``, ``V_O``.
            One character after ``_``/``^``, or a ``{...}`` group. Write the
            Unicode character for anything else (``δ``, ``–``).
        kind : {'label', 'title', 'note'}, optional
            Style class: ``label`` 8 pt, ``title`` 9 pt semibold, ``note``
            7 pt grey.
        anchor : {'start', 'middle', 'end'}, optional
            Horizontal anchor.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ``<text>`` element.
        """
        return self._text(group.element, x, y, text, kind, anchor)

    def _text(self, parent: ET.Element, x: float, y: float, text: str, kind: str, anchor: str,
              id_: str | None = None) -> ET.Element:
        size = self.pt(_TEXT_PT[kind])
        attrs = {"class": kind, "x": _num(x), "y": _num(y)}
        if anchor != "start":
            attrs["text-anchor"] = anchor
        if id_:
            attrs["id"] = id_
        el = ET.SubElement(parent, _ns("text"), attrs)
        parts = _parse_markup(text)
        if len(parts) == 1 and parts[0][1] == 0:
            el.text = parts[0][0]
            return el
        shift = 0.0
        for chunk, level in parts:
            target = -0.36 * size if level > 0 else (0.18 * size if level < 0 else 0.0)
            span = ET.SubElement(el, _ns("tspan"))
            if target != shift:
                span.set("dy", _num(target - shift))
                shift = target
            if level != 0:
                span.set("font-size", _num(0.7 * size))
            span.text = chunk
        return el

    # -- atoms --------------------------------------------------------------

    def _atom_def(self, symbol: str, state: str) -> tuple[str, float]:
        if state not in STATES:
            raise KeyError(f"Unknown atom state '{state}'. Known: {', '.join(STATES)}.")
        key = (symbol, state)
        if key not in self._atom_defs:
            get_atom(symbol)  # raises with the list of known symbols
            r = self.radius(symbol)
            ref = f"atom-{symbol}" if state == "plain" else f"atom-{symbol}-{state}"
            sym = ET.SubElement(self._defs, _ns("symbol"), {
                "id": ref, "viewBox": f"{_num(-r)} {_num(-r)} {_num(2 * r)} {_num(2 * r)}",
                "overflow": "visible"})
            ET.SubElement(sym, _ns("circle"), {"class": ref, "r": _num(r - self.pt(0.3))})
            self._atom_defs[key] = (ref, r)
        return self._atom_defs[key]

    # -- output -------------------------------------------------------------

    def _css(self) -> str:
        p = self.pt
        rules = [
            f"text{{font-family:{FONT_FAMILY};fill:{INK.base}}}",
            f".label{{font-size:{_num(p(_TEXT_PT['label']))}px}}",
            f".title{{font-size:{_num(p(_TEXT_PT['title']))}px;font-weight:600}}",
            f".note{{font-size:{_num(p(_TEXT_PT['note']))}px;fill:{GREY.dark}}}",
            f".frame{{fill:none;stroke:{GREY.light};stroke-width:{_num(p(0.6))}}}",
            f".leader{{fill:none;stroke:{INK.light};stroke-width:{_num(p(0.5))}}}",
            f".site{{fill:none;stroke:{BLUE.line};stroke-width:{_num(p(1.0))}}}",
            f".arrow{{fill:none;stroke:{INK.light};stroke-width:{_num(p(0.8))}}}",
            f".arrowhead{{fill:{INK.light}}}",
            f".angle{{fill:none;stroke:{INK.light};stroke-width:{_num(p(0.6))}}}",
        ]
        dash = f"{_num(p(1.6))} {_num(p(1.0))}"
        for (symbol, state), (ref, _) in sorted(self._atom_defs.items()):
            atom = get_atom(symbol)
            if state == "plain":
                rules.append(f".{ref}{{fill:{atom.fill};stroke:{atom.edge};stroke-width:{_num(p(0.6))}}}")
            else:
                rules.append(f".{ref}{{fill:{atom.light};stroke:{atom.edge};stroke-width:{_num(p(0.6))};"
                             f"stroke-dasharray:{dash}}}")
        for symbol in sorted(self._vacancy_symbols):
            rules.append(f".vacancy-{symbol}{{fill:none;stroke:{get_atom(symbol).edge};"
                         f"stroke-width:{_num(p(0.6))};stroke-dasharray:{dash}}}")
        return "\n".join(rules)

    def to_string(self) -> str:
        """
        The drawing as SVG text.

        Returns
        -------
        str
            A complete SVG document, indented, one element per line.
        """
        self._style.text = "\n" + self._css() + "\n"
        tree = ET.ElementTree(self.root)
        ET.indent(tree, space=" ")
        # indentation inside <text> would render as spaces before sub- and superscripts
        for el in self.root.iter(_ns("text")):
            if len(el) and el.text is not None and not el.text.strip():
                el.text = None
            for child in el:
                child.tail = None
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(self.root, encoding="unicode") + "\n"

    def save(self, directory: str | Path, name: str) -> Path:
        """
        Write the drawing as ``<directory>/<name>.svg``.

        Parameters
        ----------
        directory : str or pathlib.Path
            Output folder, created if missing.
        name : str
            File stem.

        Returns
        -------
        pathlib.Path
            Path of the written file.
        """
        path = Path(directory) / f"{name}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_string(), encoding="utf-8")
        return path

    def _repr_svg_(self) -> str:
        return self.to_string()


#: Text sizes in pt at print scale, matching the figure presets.
_TEXT_PT: dict[str, float] = {"label": 8.0, "title": 9.0, "note": 7.0}


def _parse_markup(text: str) -> list[tuple[str, int]]:
    """Split ``GaO_x`` into ``[('GaO', 0), ('x', -1)]``; ``^`` gives +1."""
    out: list[tuple[str, int]] = []
    buf = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "_^" and i + 1 < len(text):
            if buf:
                out.append((buf, 0))
                buf = ""
            level = -1 if ch == "_" else 1
            if text[i + 1] == "{":
                end = text.index("}", i + 2)
                out.append((text[i + 2:end], level))
                i = end + 1
            else:
                out.append((text[i + 1], level))
                i += 2
            continue
        buf += ch
        i += 1
    if buf:
        out.append((buf, 0))
    return out
