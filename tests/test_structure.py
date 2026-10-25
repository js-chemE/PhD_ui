import json
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from phd_ui import structure as st
from phd_ui.colors import ATOMS

CO2_MOL = """carbon dioxide, test
  test

  3  2  0  0  0  0  0  0  0  0999 V2000
   -1.1600    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.1600    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  2  3  2  0
M  END
"""
PLANE = ("C1", "O2", "H6")
UPRIGHT = dict(rotate=90, turn=-30, tip=-20)


def _xyz(p):
    return np.column_stack([np.array([a[1:] for a in p.atoms]), p.depth])


# ---------------------------------------------------------------- molecules

def test_bundled_geometries_match_their_sources():
    meoh = st.load("methanol")       # CCCBDB, Venkateswarlu & Gordy 1955
    assert meoh.distance("C1", "O2") == pytest.approx(142.7, abs=0.1)
    assert meoh.distance("O2", "H6") == pytest.approx(95.6, abs=0.1)
    assert meoh.angle("C1", "O2", "H6") == pytest.approx(108.87, abs=0.05)
    assert abs(meoh.dihedral("H3", "C1", "O2", "H6")) == pytest.approx(180, abs=0.01)
    assert st.load("water").angle("H2", "O1", "H3") == pytest.approx(104.48, abs=0.01)
    assert st.load("methane").angle("H2", "C1", "H3") == pytest.approx(109.47, abs=0.01)
    h2co = st.load("formaldehyde")
    assert h2co.angle("H3", "C2", "H4") == pytest.approx(116.13, abs=0.02)
    assert (0, 1, "double") in h2co.bonds
    co = st.load("carbon_monoxide")
    assert co.bonds == [(0, 1, "triple")] and co.distance(0, 1) == pytest.approx(112.83, abs=0.01)
    for name in st.available():
        assert st.load(name).title, name                     # every geometry names its source


def test_readers_and_writer_round_trip(tmp_path):
    co2 = st.read_mol(CO2_MOL)
    assert co2.bonds == [(0, 1, "double"), (1, 2, "double")]
    back = st.read(st.write_mol(co2, tmp_path / "co2.mol"))
    assert back.symbols == co2.symbols and back.bonds == co2.bonds
    assert back.xyz == pytest.approx(co2.xyz)
    water = st.read_xyz("3\nwater\nO 0 0 0\nH 0.9572 0 0\nH -0.2399 0.9266 0\n")
    assert sorted(water.bonds) == [(0, 1, "single"), (0, 2, "single")]


# ---------------------------------------------------------------- views

def test_plane_is_exact_and_views_are_rigid():
    mol = st.load("methanol")
    flat = st.project(mol, PLANE)
    pos = {lab: np.array(a[1:]) for lab, a in zip(flat.labels, flat.atoms)}
    assert pos["C1"] == pytest.approx([0, 0], abs=1e-9) and pos["O2"][1] == pytest.approx(0, abs=1e-9)
    u, v = pos["C1"] - pos["O2"], pos["H6"] - pos["O2"]
    assert np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v))) == pytest.approx(108.87, abs=0.01)
    assert pos["H4"] == pytest.approx(pos["H5"])              # mirror pair coincides
    p = st.project(mol, PLANE, rotations=[("z", 13), ([1, 1, 0], 40)], **UPRIGHT)
    xyz = _xyz(p)
    for a in range(6):
        for b in range(a + 1, 6):
            assert np.linalg.norm(xyz[a] - xyz[b]) == pytest.approx(mol.distance(a, b))
    assert p.reach == pytest.approx(flat.reach)


def test_tip_brings_the_top_towards_the_viewer_and_linear_molecules_project():
    p = st.project(st.load("methanol"), PLANE, rotate=90, tip=20)
    assert p.depth[1] > 0                                     # O2 on top, tipped forward
    co = st.project(st.load("carbon_monoxide"), ("C1", "O2"), rotate=90)
    assert co.atoms[1][1] == pytest.approx(0, abs=1e-9) and co.atoms[1][2] > 0
    with pytest.raises(ValueError):
        st.project(st.read_mol(CO2_MOL), (0, 1, 2))


def test_skeletal_fans_the_methyl_pair_and_keeps_the_plane():
    flat = st.project(st.load("methanol"), PLANE)
    sk_ = st.skeletal(flat)
    assert sorted(sk_.stereo.values()) == ["hash", "wedge"]
    assert [sk_.atoms[k] for k in (0, 1, 2, 5)] == [flat.atoms[k] for k in (0, 1, 2, 5)]
    c, h4, h5 = (np.array(sk_.atoms[k][1:]) for k in (0, 3, 4))
    cos = (h4 - c) @ (h5 - c) / np.linalg.norm(h4 - c) / np.linalg.norm(h5 - c)
    assert np.degrees(np.arccos(cos)) == pytest.approx(50.0)


def test_spin_keeps_the_axis_atoms_still_and_the_conformation():
    mol = st.load("methanol")
    frames = st.spin(mol, PLANE, n=12, rotate=90, tip=-20)
    assert len({round(f.depth[1], 9) for f in frames}) == 1   # O2 on the turning axis
    for f in frames:
        viewed = st.Molecule(mol.symbols, _xyz(f))
        assert viewed.dihedral("H4", "C1", "O2", "H6") == pytest.approx(mol.dihedral("H4", "C1", "O2", "H6"))


def test_painter_order_bond_between_far_and_near_atom():
    p = st.project(st.load("methanol"), PLANE, **UPRIGHT)
    pos = {(k, it if k == "atom" else tuple(it[:2])): n for n, (k, it) in enumerate(p.items())}
    for i, j, _ in p.bonds:
        far, near = sorted((i, j), key=lambda a: p.order.index(a))
        assert pos[("atom", far)] < pos[("bond", (i, j))] < pos[("atom", near)]


# ---------------------------------------------------------------- look and render

def test_look_overrides_resolve_most_specific_last():
    look = st.Look(elements={"H": st.AtomLook(opacity=0.5, fill="#ffffff")},
                   atoms={"H6": st.AtomLook(fill="#000000")},
                   kinds={"single": st.BondLook(width_pt=2.0)},
                   bonds={"O2-C1": st.BondLook(color="#ff0000")})
    assert look.atom("H", "H3").fill == "#ffffff" and look.atom("H", "H3").opacity == 0.5
    assert look.atom("H", "H6").fill == "#000000" and look.atom("H", "H6").opacity == 0.5
    assert look.atom("C", "C1").fill == ATOMS["C"].fill
    assert look.bond("single", "C1", "O2").color == "#ff0000" and look.bond("single", "C1", "O2").width_pt == 2.0
    assert look.bond("double", "C1", "O2").lines == 2
    ionic = st.Look(ions=("O2-",), ball_scale=1.0, size_exponent=1.0)
    assert ionic.radius("O", "O1") == pytest.approx(140)


def test_render_sizes_by_depth_and_ends_sticks_at_the_right_places():
    p = st.project(st.load("methanol"), PLANE)
    d = st.render(p, st.Look(depth_cue=0.0))
    assert d.radii["H4"] == pytest.approx(d.radii["H5"])
    cued = st.render(p, st.Look(depth_cue=0.2))
    near, far = sorted(("H4", "H5"), key=lambda k: -p.depth[p.labels.index(k)])
    assert cued.radii[near] > d.radii[near] > cued.radii[far]
    assert cued.radii["O2"] == pytest.approx(d.radii["O2"])   # in the plane: unchanged
    co = next(it for it in d.items if it.id == "C1-O2")       # in-plane: far ball's surface to near centre
    ends = sorted([(co.x0, co.y0), (co.x1, co.y1)])
    far, near = ("C1", "O2") if p.order.index(0) < p.order.index(1) else ("O2", "C1")
    surface = d.radii["C1"] if far == "C1" else 142.7 - d.radii["O2"]
    centre = 142.7 if near == "O2" else 0.0
    assert np.allclose(ends, sorted([(surface, 0.0), (centre, 0.0)]), atol=0.05)


def test_wedge_and_hash_run_centre_to_centre_under_both_balls():
    p = st.view("methanol", "organic")
    d = st.render(p, pm_per_pt=4.0)
    ids = [it.id for it in d.items]
    wedge = next(it for it in d.items if it.type == "polygon")
    assert ids.index(wedge.id) < ids.index("C1")              # under the C ball
    tip = np.mean(wedge.points[:1] + wedge.points[-1:], axis=0)
    assert tip == pytest.approx(d.positions["C1"])
    assert any(it.type == "line" and it.kind == "hash" for it in d.items)


def test_library_views_and_json_for_the_web(tmp_path):
    assert {"organic", "upright"} <= set(st.views("methanol"))
    up = st.view("methanol", "upright")
    assert up.depth == pytest.approx(st.project(st.load("methanol"), PLANE, **UPRIGHT).depth)
    with pytest.raises(KeyError):
        st.view("methanol", "nope")
    path = st.frames_to_json(st.spin(st.load("methanol"), PLANE, n=4, rotate=90, tip=-20), tmp_path / "s.json")
    data = json.loads(path.read_text())
    assert data["unit"] == "pm" and len(data["frames"]) == 4
    assert {i["type"] for i in data["frames"][0]["items"]} == {"circle", "line"}
    assert [i["id"] for i in data["frames"][0]["items"] if i["type"] == "circle"].count("O2") == 1


def test_export_writes_every_format(tmp_path):
    import phd_ui as ui
    ui.initialize()
    files = st.export(st.view("methanol", "organic"), tmp_path, "m")
    assert sorted(f.suffix for f in files) == [".pdf", ".png", ".svg"]
    root = ET.parse(tmp_path / "m.svg").getroot()
    ns = "{http://www.w3.org/2000/svg}"
    assert len([c for c in root.iter(ns + "circle")]) == 6
    spin = st.export_spin(st.spin(st.load("water"), ("O1", "H2", "H3"), n=4), tmp_path, "w")
    assert sorted(f.suffix for f in spin) == [".gif", ".svg"]


def test_glb_is_valid_gltf_with_one_node_per_atom_and_bond_line(tmp_path):
    import struct
    path = st.export_glb(st.view("formaldehyde", "upright"), tmp_path / "f.glb",
                         st.Look(atoms={"O1": st.AtomLook(opacity=0.5)}))
    data = path.read_bytes()
    magic, version, length = struct.unpack("<III", data[:12])
    assert (magic, version, length) == (0x46546C67, 2, len(data))
    n_json, kind = struct.unpack("<II", data[12:20])
    gltf = json.loads(data[20:20 + n_json])
    names = [n.get("name") for n in gltf["nodes"][1:]]
    assert {"O1", "C2", "H3", "H4", "C2-H3", "C2-H4", "O1-C2.0", "O1-C2.1"} == set(names)   # C=O as two sticks
    assert all("min" in gltf["accessors"][m["primitives"][0]["attributes"]["POSITION"]] for m in gltf["meshes"])
    assert any(m.get("alphaMode") == "BLEND" for m in gltf["materials"])
    with pytest.raises(ValueError):
        st.export_glb(st.view("methanol", "organic"), tmp_path / "x.glb")


def test_formate_on_cu_with_hidden_surface_atoms():
    m = st.load("formate_cu111")         # Chutia et al. 2016 bond lengths, O-C-O assumed (title says so)
    assert "ASSUMED" in m.title
    assert m.distance("C1", "O2") == pytest.approx(127.0, abs=0.05)
    assert m.distance("O2", "Cu5") == pytest.approx(201.7, abs=0.05)
    assert m.distance("Cu5", "Cu6") == pytest.approx(254.6, abs=0.05)
    assert sorted(k for *_, k in m.bonds) == ["partial", "partial", "single", "surface", "surface"]
    look = st.Look(elements={"Cu": st.AtomLook(opacity=0.0)})
    d = st.render(st.view("formate_cu111", "flat"), look)
    line = next(it for it in d.items if it.id == "O2-Cu5")
    assert (round(line.x0, 6), round(line.y0, 6)) == (0.0, 0.0) or (round(line.x1, 6), round(line.y1, 6)) == (0.0, 0.0)
