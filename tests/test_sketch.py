import xml.etree.ElementTree as ET

import pytest

import phd_ui.sketch as sk
from phd_ui.colors import ATOMS
from phd_ui.sketch.scene import INKSCAPE_NS, SVG_NS, XLINK_NS, _parse_markup

NS = {"svg": SVG_NS}


def _parse(scene: sk.Scene) -> ET.Element:
    return ET.fromstring(scene.to_string().split("\n", 1)[1])


def _small_scene() -> tuple[sk.Scene, sk.Panel]:
    scene = sk.Scene(60, 40, pm_per_mm=65, title="test")
    panel = scene.panel("10CuGa", 0, scene.mm(5), scene.mm(50), scene.mm(30), title="10CuGa")
    return scene, panel


def test_size_and_viewbox_in_pm():
    scene = sk.Scene(180, 42, pm_per_mm=65)
    root = _parse(scene)
    assert root.get("width") == "180mm" and root.get("height") == "42mm"
    assert root.get("viewBox") == "0 0 11700 2730"


def test_pt_conversion_and_slide_scale():
    print_scene = sk.Scene(10, 10, pm_per_mm=100)
    slide_scene = sk.Scene(10, 10, pm_per_mm=100, scale=2.0)
    assert print_scene.pt(72) == pytest.approx(25.4 * 100)
    assert slide_scene.pt(8) == pytest.approx(2 * print_scene.pt(8))


def test_from_figsize_takes_width_from_preset():
    scene = sk.Scene.from_figsize("double", height_mm=40)
    assert scene.width_mm == pytest.approx(180)
    assert scene.scale == 1.0
    assert sk.Scene.from_figsize("slide_half").scale == 2.0


def test_panel_is_a_layer_with_parts_in_fixed_order():
    scene, panel = _small_scene()
    # draw in the "wrong" order: labels and defects before the support
    sk.label(panel.part("labels"), 0, 0, "GaO_x")
    panel.part("defects")
    slab = sk.slab(panel.part("support"), ("Ga", "O"), 0, panel.width, 1000, 800, name="GaOx")
    assert slab.atoms
    root = _parse(scene)
    layer = root.find("svg:g[@id='panel-10CuGa']", NS)
    assert layer.get(f"{{{INKSCAPE_NS}}}groupmode") == "layer"
    art = layer.find("svg:g[@id='panel-10CuGa.art']", NS)
    order = [g.get(f"{{{INKSCAPE_NS}}}label") for g in art.findall("svg:g", NS)]
    assert order == ["support", "defects"]
    assert art.get("clip-path") == "url(#panel-10CuGa.clip)"
    # labels sit outside the clip, after the frame
    children = [c.get("id") for c in layer]
    assert children.index("panel-10CuGa.labels") > children.index("panel-10CuGa.frame")


def test_atoms_are_references_to_one_symbol_per_element_and_state():
    scene, panel = _small_scene()
    sk.slab(panel.part("support"), "Cu", 0, panel.width, 1000, 600)
    sk.stack(panel.part("particles"), "Cu", 500, 600, rows=[3, 2], ox="base")
    root = _parse(scene)
    symbols = {s.get("id") for s in root.iter(f"{{{SVG_NS}}}symbol")}
    assert symbols == {"atom-Cu", "atom-Cu-ox"}
    uses = list(root.iter(f"{{{SVG_NS}}}use"))
    assert len(uses) > 20
    assert all(u.get(f"{{{XLINK_NS}}}href", "").startswith("#atom-") for u in uses)
    css = root.find("svg:style", NS).text
    assert ATOMS["Cu"].fill in css and ATOMS["Cu"].light in css


def test_stack_ox_base_and_omit():
    scene, panel = _small_scene()
    placed = sk.stack(panel.part("particles"), "Cu", 0, 0, rows=[3, 2], ox="base", omit=[(1, 1)])
    assert len(placed.atoms) == 4 and len(placed.omitted) == 1
    r = scene.radius("Cu")
    assert placed.at(1, 1) == pytest.approx((r * 2 * 1.5, -2 * r * 3 ** 0.5 / 2))


def test_oxide_slab_is_a_checkerboard():
    scene, panel = _small_scene()
    placed = sk.slab(panel.part("support"), ("Ga", "O"), 0, 2000, 1000, 500)
    grid = {(r, c): s for s, _, _, r, c in placed.atoms}
    for (r, c), s in grid.items():
        if (r, c + 1) in grid:
            assert grid[(r, c + 1)] != s
        if (r + 1, c) in grid:
            assert grid[(r + 1, c)] != s


def test_oxide_island_alternates_vertically():
    scene, panel = _small_scene()
    island = sk.stack(panel.part("particles"), ("O", "Ga"), 0, 0, rows=[5, 3])
    by_xy = {(round(x), round(y)): s for s, x, y, _, _ in island.atoms}
    for s, x, y, r, _ in island.atoms:
        if r == 1:
            below = by_xy[(round(x), round(y + scene.radius("O") + scene.radius("Ga")))]
            assert below != s


def test_vacancies_drawn_for_omitted_positions():
    scene, panel = _small_scene()
    placed = sk.slab(panel.part("support"), ("Ga", "O"), 0, 2000, 1000, 500, omit=[(0, 1), (0, 3)])
    sk.vacancies(panel.part("defects"), placed)
    root = _parse(scene)
    rings = [c for c in root.iter(f"{{{SVG_NS}}}circle") if c.get("class", "").startswith("vacancy-")]
    assert len(rings) == 2 and {c.get("class") for c in rings} == {"vacancy-O"}


def test_rest_y_sits_above_the_surface_row():
    scene, panel = _small_scene()
    placed = sk.slab(panel.part("support"), "Cu", 0, 2000, 1000, 500)
    y = sk.rest_y(scene, placed, "Cu")
    assert y == pytest.approx(1000 - 2 * scene.radius("Cu") * 3 ** 0.5 / 2)


def test_markup_and_no_whitespace_in_text():
    assert _parse_markup("GaO_x") == [("GaO", 0), ("x", -1)]
    assert _parse_markup("Cu^{δ+}") == [("Cu", 0), ("δ+", 1)]
    scene, panel = _small_scene()
    sk.label(panel.part("labels"), 0, 0, "Cu^{δ+}")
    root = _parse(scene)
    text = [t for t in root.iter(f"{{{SVG_NS}}}text") if t.get("class") == "label"][0]
    assert "".join(text.itertext()) == "Cuδ+"


def test_unique_ids_and_unknown_inputs():
    scene, panel = _small_scene()
    a = panel.part("particles").group("Cu")
    b = panel.part("particles").group("Cu")
    assert a.id != b.id
    with pytest.raises(KeyError):
        panel.part("background")
    with pytest.raises(KeyError):
        panel.part("particles").atom("Xx", 0, 0)
    with pytest.raises(KeyError):
        panel.part("particles").atom("Cu", 0, 0, state="reduced")


def test_radius_override_and_compression():
    from phd_ui.colors import drawn_radius_pm, SIZE_REFERENCE_PM
    scene = sk.Scene(10, 10, radii={"O": 140})
    assert scene.radius("O") == 140                       # overrides are taken as given
    assert scene.radius("Ga") == pytest.approx(ATOMS["Ga"].drawn_pm)
    # compression keeps the order but shrinks every ratio to its square root
    assert ATOMS["O"].drawn_pm / ATOMS["H"].drawn_pm == pytest.approx((66 / 31) ** 0.5)
    assert drawn_radius_pm(SIZE_REFERENCE_PM) == pytest.approx(SIZE_REFERENCE_PM)
    assert sk.Scene(10, 10, size_exponent=1.0).radius("H") == ATOMS["H"].radius_pm


def test_atom_sheet_has_every_element(tmp_path):
    scene = sk.atom_sheet()
    path = scene.save(tmp_path, "atoms")
    root = ET.parse(path).getroot()
    ids = {s.get("id") for s in root.iter(f"{{{SVG_NS}}}symbol")}
    for symbol in ATOMS:
        assert f"atom-{symbol}" in ids and f"atom-{symbol}-ox" in ids


def test_ions_set_ionic_radii_and_keep_metals_covalent():
    from phd_ui.colors import IONS
    scene = sk.Scene(10, 10, ions=("Ga3+", "O2-"), size_exponent=1.0)
    assert scene.radius("O") == IONS["O2-"].radius_pm == 140
    assert scene.radius("Ga") == IONS["Ga3+"].radius_pm == 62
    assert scene.radius("Cu") == ATOMS["Cu"].radius_pm
    assert sk.Scene(10, 10, ions=("O2-",)).radius("O") == pytest.approx(IONS["O2-"].drawn_pm)
    assert sk.Scene(10, 10, ions=("O2-",), radii={"O": 100}).radius("O") == 100
    with pytest.raises(ValueError):
        sk.Scene(10, 10, ions=("Ga3+", "Ga3+(IV)"))
    with pytest.raises(KeyError):
        sk.Scene(10, 10, ions=("Xx9+",))


def test_ions_point_at_known_elements():
    from phd_ui.colors import IONS
    for key, ion in IONS.items():
        assert ion.symbol in ATOMS, key
        assert key.startswith(ion.symbol)
        assert ion.radius_pm > 0


def test_nearest_lands_on_a_drawn_atom():
    scene, panel = _small_scene()
    placed = sk.slab(panel.part("support"), ("Ga", "O"), 0, 2000, 1000, 500, omit=[(0, 3)])
    x, y = placed.nearest(700, symbol="Ga")
    assert ("Ga", x, y) in {(s, a, b) for s, a, b, r, _ in placed.atoms if r == 0}
