from phd_ui.renaming import Renaming


def test_loading_renaming():
    from phd_ui.renaming import Renaming

    assert True, "This test is a placeholder to ensure that the Renaming class can be imported without errors. It does not perform any assertions on the functionality of the Renaming class."

def test_get_renaming():
    renaming = Renaming.from_json(json_path = r"src\phd_ui\_assets\renaming.json")

    assert renaming.get_renaming("H2") == "H2"