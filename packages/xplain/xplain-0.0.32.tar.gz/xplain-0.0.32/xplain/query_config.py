import xplain
import uuid

class Query_config:
    """
    Factory class to generate the xplain query configuration for the `execute_query` method of Xsession.

    Attributes:
        request (dict): The query configuration containing aggregations, groupBys, and selections.
    """

    def __init__(self, name: str = None):
        """
        Initialize the QueryConfig instance with a default or provided name.

        Args:
            name (str, optional): The name or identifier for the query. Defaults to a UUID.
        """
        self.request = {
            "requestName": name if name else str(uuid.uuid4()),
            "aggregations": [],
            "groupBys": [{"subGroupings": []}],
            "selections": []
        }

    def set_name(self, request_name: str):
        """
        Assign a specific name or ID to the query.

        Args:
            request_name (str): The name or ID to be assigned.

        Raises:
            ValueError: If the request_name is not a valid string.
        """
        if not isinstance(request_name, str) or not request_name.strip():
            raise ValueError("request_name must be a non-empty string.")
        self.request["requestName"] = request_name

    def add_aggregation(self, object_name: str, dimension_name: str, type: str, aggregation_name: str = None):
        """
        Add an aggregation specification to the query.

        Args:
            object_name (str): The name of the xobject.
            dimension_name (str): The name of the dimension.
            type (str): The aggregation type (e.g., SUM, AVG, COUNT).
            aggregation_name (str, optional): The name of the aggregation.

        Raises:
            ValueError: If required arguments are missing or invalid.
        """
        if not object_name or not dimension_name or not type:
            raise ValueError("object_name, dimension_name, and atype are required.")
        if type not in {"SUM", "AVG", "COUNT", "COUNTDISTINCT", "MAX", "MIN", "COUNTENTITY", "VAR", "STDEV", "QUANTILE"}:
            raise ValueError(f"Invalid aggregation type: {type}.")

        aggregation = {
            "object": object_name,
            "dimension": dimension_name,
            "type": type
        }
        if aggregation_name:
            aggregation["aggregationName"] = aggregation_name

        self.request["aggregations"].append(aggregation)

        return self

    def add_groupby(
        self,
        attribute_name: str,
        object_name: str = None,
        dimension_name: str = None,
        groupby_level: str = None,
        groupby_level_number: int = None,
        groupby_states: list = None
    ):
        """
        Add a group-by specification to the query configuration.

        Args:
            attribute_name (str): The name of the attribute.
            object_name (str, optional): The name of the xobject.
            dimension_name (str, optional): The name of the dimension.
            groupby_level (str, optional): The name of the group-by level.
            groupby_level_number (int, optional): The number of the group-by level.
            groupby_states (list, optional): Specific group-by states to apply.

        Raises:
            ValueError: If attribute_name is not provided.
        """
        if not attribute_name:
            raise ValueError("attribute_name is required.")

        try:
            groupby = self._build_groupby(
                object_name=object_name,
                dimension_name=dimension_name,
                attribute_name=attribute_name,
                groupby_level=groupby_level,
                groupby_level_number=groupby_level_number
            )
            self.request["groupBys"][0]["subGroupings"].append(groupby)
        except Exception as e:
            raise RuntimeError("Failed to add group-by specification.") from e

        return self

    def _build_groupby(
            self,
            object_name=None,
            dimension_name=None,
            attribute_name=None,
            groupby_level=None,
            groupby_level_number=None
    ):
        if not any([object_name, dimension_name, attribute_name]):
            raise ValueError("At least one of 'object_name', 'dimension_name', or 'attribute_name' must be provided.")

        groupby_json = {
            "attribute": {
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name,
            }
        }

        if groupby_level:
            groupby_json["groupByLevel"] = groupby_level

        if groupby_level_number:
            if not isinstance(groupby_level_number, int):
                raise ValueError("'groupby_level_number' must be an integer.")
            groupby_json["groupByLevelNumber"] = groupby_level_number

        return groupby_json

    def add_selection(
        self,
        attribute_name: str,
        object_name: str = None,
        dimension_name: str = None,
        selected_states: list = None
    ):
        """
        Add a selection specification to the query configuration.

        Args:
            attribute_name (str): The name of the attribute.
            object_name (str, optional): The name of the xobject.
            dimension_name (str, optional): The name of the dimension.
            selected_states (list, optional): The set of selected states.

        Raises:
            ValueError: If attribute_name is not provided.
        """
        if not attribute_name:
            raise ValueError("attribute_name is required.")

        try:
            selection = self._build_selection(
                attribute_name=attribute_name,
                object_name=object_name,
                dimension_name=dimension_name,
                selected_states=selected_states
            )
            self.request["selections"].append(selection)
        except Exception as e:
            raise RuntimeError("Failed to add selection specification.") from e

        return self

    def _build_selection(self, attribute_name, object_name=None, dimension_name=None, selected_states=None):
        selection = {
            "attribute": {
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name
            },
            "selectedStates": selected_states
        }
        return selection

    def to_json(self) -> dict:
        """
        Return the configuration of this query as JSON.

        Returns:
            dict: The query configuration.
        """
        return self.request