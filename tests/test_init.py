

def test_initialize():
    from phd_ui import initialize

    assert initialize is not None

    initialize()
    assert True 