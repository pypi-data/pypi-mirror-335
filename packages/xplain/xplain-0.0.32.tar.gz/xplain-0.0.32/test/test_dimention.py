import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
import jsondiff


class TestDimension:

    # Arrange
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession(URL, USER, PASSWORD)

        session.startup(TESTSET)

        return session

    # BTS-148
    def test_get_name(self, s1):

        dimension_name = xplain.Dimension("Patients", "Costs",
                                          s1.__xplain_session__['focusObject']).get_name()

        assert len(jsondiff.diff(str(dimension_name), "Costs")) == 0

    # BTS-146 143
    def test_get_attribute(self, s1):

        attribute = s1.get_xobject("Patients").get_dimension("Gender").get_attribute("Gender").get_name()

        assert str(attribute).startswith("Gender")

    # BTS-147 143
    def test_get_attributes(self, s1):

        attributes_name = s1.get_xobject("Patients").get_dimension("Gender").get_attributes()[0].get_name()

        assert str(attributes_name).startswith("Gender")

        s1.terminate()
