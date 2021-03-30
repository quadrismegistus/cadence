
# Hacky quick-fix allowing importing of cadence module. 
# Should be removed when this is expanded into a "real" testing suite
import sys
sys.path.append("..")

# Sample Test passing with nose and pytest

def test_pass():
    assert True, "dummy sample test"

def test_import():
    import cadence as cd
    assert True, "Ensure that Cadence can be imported"

def test_scan():
    import cadence as cd

    milton = "OF Mans First Disobedience, and the Fruit"\
    "Of that Forbidden Tree, whose mortal tast"\
    "Brought Death into the World, and all our woe"

    txtdf = cd.scan(milton)
    assert txtdf is not None, "Ensure that Cadence can scan without Exceptions"
