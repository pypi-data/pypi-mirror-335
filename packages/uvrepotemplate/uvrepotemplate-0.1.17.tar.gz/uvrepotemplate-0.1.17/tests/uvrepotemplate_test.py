import uvrepotemplate


def test_Add1():
    assert uvrepotemplate.Add(1, 12) == 13


def test_Add2():
    assert uvrepotemplate.Add(1, 12) == 13


def test_Subtract():
    assert uvrepotemplate.Subtract(1, 10) == -9
