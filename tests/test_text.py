import pytest

from phd_ui.text import cite


def test_three_or_more_authors_with_group_lead():
    assert cite("Vico van Berkel", "J. Catal.", 2024, lead="Urakawa") == "Vico van Berkel et al. (Urakawa), J. Catal. 2024"


def test_lead_is_dropped_when_first_author_is_the_lead():
    assert cite("Urakawa", "J. Phys. Chem. C", 2019, lead="urakawa") == "Urakawa et al., J. Phys. Chem. C 2019"
    assert cite("Urakawa", "J. Phys. Chem. C", "2019") == "Urakawa et al., J. Phys. Chem. C 2019"


def test_two_authors_use_an_ampersand():
    assert cite("Maeder", "Chemom. Intell. Lab. Syst.", 1988, second_author="Zilian", et_al=False) == \
        "Maeder & Zilian, Chemom. Intell. Lab. Syst. 1988"


def test_single_author():
    assert cite("Noda", "Appl. Spectrosc.", 1993, et_al=False) == "Noda, Appl. Spectrosc. 1993"


def test_second_author_needs_et_al_off():
    with pytest.raises(ValueError):
        cite("Maeder", "Chemom. Intell. Lab. Syst.", 1988, second_author="Zilian")
