import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
import jsondiff
from pathlib import Path
from unittest.mock import patch, MagicMock
from queries import queries
from references.BTS113xplainXsessionGetAttributeInfo import (attributeInfoRef)
from references.BTS114xplainXsessionGetDimensionInfo import (dimensionInfoRef)
from references.BTS117xplainXsessionGetObjectInfo import (OBJECTINFOREF)
from references.BTS130xplainSessionOpenAttribute import (openedAttribute)


class TestXsession:

    # BTS-108
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession()#URL, USER, PASSWORD

        session.startup(TESTSET)

        return session

    # BTS-110
    def test_build_predictive_model(self, s1):
        s1.run({
            "selectionSet": "globalSelections",
            "selections": [
                {
                    "attribute": {
                        "name": "Prescriptions",
                        "object": "Prescriptions",
                        "dimension": "PZN",
                        "attribute": "pzn"
                    },
                    "selectedStates": [
                        "C KARDIOVASKULAERES SYSTEM"
                    ]
                }
            ],
            "method": "select"
        })

        s1.build_predictive_model(model_name='Kardio',
                                  xmodel_config='Causal Discovery.xdefaultmodel',
                                  model_object_name='Patients',
                                  significance=0.9,
                                  target_event_object_name='Prescriptions',
                                  target_selection_object_name='Prescriptions',
                                  target_selection_dimension_name='PZN',
                                  target_selection_attribute='pzn')

        model_name = s1.get_model_names()

        print(model_name)

        assert False

    # BTS-113
    def test_get_attribute_info(self, s1):

        attribute_info = s1.get_attribute_info("Patients", "Age", "Age")

        assert len(jsondiff.diff(attribute_info, attributeInfoRef)) == 0

    # BTS-114
    def test_get_dimension_info(self, s1):

        dimension_info = s1.get_dimension_info("Patients", "Age")

        assert len(jsondiff.diff(dimension_info, dimensionInfoRef)) == 0

    # BTS-115
    def test_get_instance_as_dataframe(self, s1):

        dataframe = s1.get_instance_as_dataframe([{"object": "Patients"}])

        assert len(dataframe) == 54132

    # BTS-117
    def test_get_object_info(self, s1):
        objectInfo = s1.get_object_info("Patients")

        objectInfoRef = OBJECTINFOREF

        print(objectInfo, objectInfoRef, jsondiff.diff(objectInfo, objectInfoRef))

        assert len(jsondiff.diff(objectInfo, objectInfoRef)) == 0

    # BTS-119
    def test_get_queries(self, s1):
        query = queries[0]

        openedQuery = s1.open_query(query)

        queryIds = s1.get_queries()

        print(queryIds, openedQuery, len(queryIds))

        assert len(queryIds[0]) == 36

    # BTS-121, 153
    def test_get_root_object(self, s1):

        rootObject = s1.get_root_object().get_name()

        object_name = s1.get_xobject("Patients").get_name()

        assert len(jsondiff.diff(str(rootObject), str(object_name))) == 0

    # BTS-124, 129
    def test_get_session_id(self, s1):

        sessionId = s1.get_session_id()

        s1.load_from_session_id(sessionId)

        print(sessionId, s1.load_from_session_id(sessionId))

        assert len(sessionId) > 0

        assert s1.load_from_session_id(sessionId) is None

    # BTS-127
    def test_get_xobject(self, s1):

        object_name = s1.get_xobject("Patients")

        object2 = s1.get_xobject("Patients")

        print(object_name)

        assert str(object_name).find("0x") > 0

    # BTS-130
    def test_open_attribute(self, s1):

        attribute = s1.open_attribute("Patients", "Age", "Age").to_json(orient="split")

        assert len(jsondiff.diff(attribute, openedAttribute)) == 0

    # BTS-139
    @patch('builtins.print')
    def test_show_tree(self, mock_print, s1):

        path = Path(__file__).parent / "references/BTS139xplainXsessionShowTree.txt"

        try:
            with path.open() as file:
                data = file.read()
        except:
            print("error occurred")

        magicMock = MagicMock()
        mock_print.return_value = magicMock

        # new_tree = Tree() tree = s1._ref_session.__buildTree__(new_tree, s1._ref_session.__xplain_session__[
        # 'focusObject'], parent_id=None) print(str(tree))

        s1.show_tree()
        mock_print.assert_called_with(data)

        # print("helloS")
        # mock_print.assert_called_with("helloS")

    # BTS-149
    def test_add_aggregation_dimension(self, s1):
        try:
            dimension1 = s1.get_xobject("Patients").add_aggregation_dimension(
                dimension_name="newDim",
                aggregation={
                    "object": "Patients",
                    "dimension": "marginalReturn",
                    "type": "AVG"
                }
            )
        except:
            print("error")

        print(dimension1)

        dimension2 = s1.get_xobject("Patients").get_dimension("Costs")

        # error = s1.print_error()

        # print("error", error)

        # assert error is None

        assert False  # len(jsondiff.diff(str(dimension1), str(dimension2))) == 0

    # BTS-150
    def test_get_child_objects(self, s1):

        print(type(s1.get_root_object().get_child_objects()), s1.get_root_object().get_child_objects())

        childObject = (s1.get_root_object().get_child_objects())

        object_name = (s1.get_xobject("Patients").get_child_objects())

        assert len(jsondiff.diff(str(childObject), str(object_name))) == 0

    # BTS-151
    def test_get_dimension(self, s1):

        dimension1 = s1.get_root_object().get_dimension("Costs")

        dimension2 = s1.get_xobject("Patients").get_dimension("Costs")

        assert len(jsondiff.diff(str(dimension1), str(dimension2))) == 0

    # BTS-152
    def test_get_dimensions(self, s1):
        print(s1.get_root_object().get_child_objects()[1])
        childDimension = ((s1.get_root_object()).get_dimensions()[0])

        dimension = ((s1.get_xobject("Patients")).get_dimensions()[0])

        assert len(jsondiff.diff(str(childDimension), str(dimension))) == 0

    # BTS-133
    def test_print_error(self, s1):

        error = s1.print_error()

        assert error is None

        s1.terminate()

    # create collapsible tree
    def test_collapsible_tree(self, s1):

        print(s1.get_root_object().get_name(), s1)

        s1.collapsible_tree()

        #assert False

    def test_execute_query(self, s1):
        query = queries[1]

        openedQuery = s1.execute_query(query)

        print("test_execute_query", str(openedQuery))

        assert len(openedQuery) == 18

    def test_execute_query_with_invalid_query(self, s1):

        with pytest.raises(ValueError, match="The query must be a dictionary or a Query_config object."):
            s1.execute_query(123)  # Pass an invalid type

    def test_create_contingency_table(self, s1):

        dataframe = s1.get_instance_as_dataframe([{"object": "Patients"}])

        contingency = s1.create_contingency_table(dataframe, 'Patients.Gender', 'Patients.Age')
        print("Contingency Table:\n", contingency, len(contingency.to_json()))

        assert len(contingency.to_json()) == 1993

    def test_run_statsmodels(self, s1):

        dataframe = s1.get_instance_as_dataframe([{"object": "Patients"}])

        formula = s1.build_formula("Patients.Nation", ["Patients.Gender", "Patients.Age", "Patients.City"])
        model = s1.run_statsmodels(dataframe, formula, model_type="mnlogit")
        print("Model Summary:\n", model.summary(), len(str(model.summary())))

        assert len(str(model.summary())) == 5512
