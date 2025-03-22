import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
import jsondiff

class TestXobject:

    # Arrange
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession(URL, USER, PASSWORD)

        session.startup(TESTSET)

        return session

    #
    def test_get_name(self, s1):

        object_name = xplain.Xobject("Patients", s1).get_name()

        assert object_name == "Patients"

    #
    def test_get_attribute(self, s1):

        child_object = xplain.Xobject("Patients", s1).get_child_objects()

        print(child_object)

        assert str(child_object) == "['Prescriptions', 'Hospitalizations']"

    #
    def test_get_dimensions(self, s1):

        dimentions = xplain.Xobject("Patients", s1).get_dimensions()

        print(dimentions)

        assert str(dimentions) == "['Patient', 'Gender', 'DoB', 'Age', 'City', 'Nation', 'Died', 'marginalReturn', 'Is Null']"

    def test_get_dimension(self, s1):

        dimention = xplain.Xobject("Patients", s1).get_dimension("Gender")

        print(dimention)

        assert str(dimention) == 'Gender'

    def test_add_aggregation_dimensions(self, s1):
        #dimention = xplain.Xobject("Patients", s1).get_dimension("Gender")

        xobject = s1.get_xobject("Patients")
        xobject.add_aggregation_dimension(
            dimension_name="newDim",
            aggregation={
                "object": "Patients",
                "dimension": "Age",
                "type": "AVG"
            }
        )

        print(xobject)

        assert False