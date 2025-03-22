import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
import jsondiff

class TestAttribute:

    # Arrange
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession(URL, USER, PASSWORD)

        session.startup(TESTSET)

        return session

    # BTS-142
    def test_get_levels(self, s1):

        levels = xplain.Attribute("Patients", "Gender", "Gender", s1).get_levels()

        print(levels)

        levels2 = s1.get_xobject("Patients").get_dimension("Gender").get_attribute("Gender").get_levels()

        print(levels2)

        assert levels == levels2

    # BTS-144
    def test_get_root_state(self, s1):

        attributeStateHiearchy = xplain.Attribute("Patients", "City", "city", s1).get_root_state()

        print(attributeStateHiearchy)

        assert attributeStateHiearchy == "city"

    # BTS-145
    def test_get_state_hierarchy(self, s1):

        attributeStateHiearchy2 = xplain.Attribute("Patients", "City", "city", s1).get_state_hierarchy("Aalen", 1)

        print(attributeStateHiearchy2)

        assert len(attributeStateHiearchy2) == 126

    # BTS-143
    def test_get_name(self, s1):

        name = xplain.Attribute("Patients", "Gender", "Gender", s1).get_name()

        print(name)

        name2 = s1.get_xobject("Patients").get_dimension("Gender").get_attribute("Gender").get_name()

        print(name2)

        assert len(jsondiff.diff(str(name), name2)) == 0

        s1.terminate()