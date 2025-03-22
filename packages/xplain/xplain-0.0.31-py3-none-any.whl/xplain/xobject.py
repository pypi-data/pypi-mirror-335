import xplain


class XObject:
    """
    Represents a Xobject with methods to interact with its child objects, dimensions,
    and to add aggregation dimensions.

    Attributes:
        object_name (str): The name of the Xobject.
        _ref_session: The session object used for API interactions.
    """

    def __init__(self, object_name: str, ref_session):
        """
        Initialize a Xobject instance.

        Args:
            object_name (str): The name of the Xobject.
            ref_session: A session object for making API calls.
        """
        if not isinstance(object_name, str):
            raise TypeError("object_name must be a string.")
        self.object_name = object_name
        self._ref_session = ref_session

    def get_name(self) -> str:
        """Return the name of the Xobject."""
        return self.object_name

    def get_child_objects(self) -> list:
        """
        Retrieve the child Xobjects of the current Xobject.

        Returns:
            list: A list of child Xobject names (strings).

        Raises:
            RuntimeError: If fetching child objects fails.
        """
        try:
            child_names = []
            json_details = self._ref_session.get_tree_details(object_name=self.object_name)

            if json_details.get("childObjects"):
                child_names = [
                    child_obj["objectName"]
                    for child_obj in json_details["childObjects"]
                ]

            return child_names
        except KeyError as e:
            raise KeyError(f"Missing expected key in response: {e}")
        except Exception as e:
            raise RuntimeError("Failed to fetch child objects.") from e

    def get_dimensions(self) -> list:
        """
        Retrieve the list of dimensions attached to the current Xobject.

        Returns:
            list: A list of dimension names (strings).

        Raises:
            RuntimeError: If fetching dimensions fails.
        """
        try:
            dimension_names = []
            json_details = self._ref_session.get_tree_details(object_name=self.object_name)

            if json_details.get("dimensions"):
                dimension_names = [
                    dim_obj["dimensionName"]
                    for dim_obj in json_details["dimensions"]
                ]

            return dimension_names
        except KeyError as e:
            raise KeyError(f"Missing expected key in response: {e}")
        except Exception as e:
            raise RuntimeError("Failed to fetch dimensions.") from e

    def get_dimension(self, dimension_name: str) -> str:
        """
        Retrieve a specific dimension by its name.

        Args:
            dimension_name (str): The name of the dimension to retrieve.

        Returns:
            str: The name of the dimension if found, otherwise None.

        Raises:
            ValueError: If the dimension name is invalid.
            RuntimeError: If fetching dimensions fails.
        """
        if not dimension_name or not isinstance(dimension_name, str):
            raise ValueError("dimension_name must be a non-empty string.")

        try:
            json_details = self._ref_session.get_tree_details(object_name=self.object_name)

            if json_details.get("dimensions"):
                for dim_obj in json_details["dimensions"]:
                    if dim_obj["dimensionName"] == dimension_name:
                        return dim_obj["dimensionName"]

            return None
        except KeyError as e:
            raise KeyError(f"Missing expected key in response: {e}")
        except Exception as e:
            raise RuntimeError("Failed to fetch the dimension.") from e

    def add_aggregation_dimension(
            self,
            dimension_name: str,
            aggregation: dict,
            selections: list = None,
            floating_semantics: bool = False
    ) -> dict:
        """
        adds an aggregation dimension to the given target dimension. The
        aggregation dimension aggregates data from a child object (or any
        deeper descendant objects) according to the given aggregation
        definition.

        :param dimension_name: the name of new dimension
        :type dimension_name: string
        :param aggregation: aggregation of the new dimension
        :type aggregation: json or aggregation object
        :param selections: the selections shall be considered
        :type selections: array of json or selection object
        :param floating_semantics: If set to true the resulting dimension will
        have a floating semantics.
        :type floating_semantics: boolean

        Returns:
            dict: Response from the session's `run` method.

        Raises:
            ValueError: If required arguments are missing or invalid.
            RuntimeError: If the API call fails.

        Example:
            >>> xobject = session.get_object("Krankengeld")
            >>> xobject.add_aggregation_dimension(
                                             dimension_name="newDim",
                                             aggregation={
                                                     "object": "Krankengeld",
                                                     "dimension":"Anzahl_Tage",
                                                     "type": "AVG"
                                                    }
                                            )

        """
        if not dimension_name or not isinstance(dimension_name, str):
            raise ValueError("dimension_name must be a non-empty string.")
        if not isinstance(aggregation, dict):
            raise ValueError("aggregation must be a dictionary.")
        if selections and not isinstance(selections, list):
            raise ValueError("selections must be a list or None.")

        try:
            method_call = {
                "method": "addAggregationDimension",
                "targetObject": self.object_name,
                "dimensionName": dimension_name,
                "aggregation": aggregation,
                "selections": selections or [],
                "floatingSemantics": floating_semantics
            }
            return self._ref_session.run(method_call)
        except Exception as e:
            raise RuntimeError("Failed to add aggregation dimension.") from e
