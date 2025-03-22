import xplain


class Dimension:
    """
    Represents a dimension object with methods to retrieve its attributes.

    Attributes:
        object_name (str): Name of the associated object.
        dimension_name (str): Name of the dimension.
        _ref_session (Session): Reference to the session object for API interaction.
    """

    def __init__(self, object_name: str, dimension_name: str, ref_session):
        """
        Initialize the Dimension instance.

        Args:
            object_name (str): Name of the object.
            dimension_name (str): Name of the dimension.
            ref_session: Session object for API calls.
        """
        if not all(isinstance(arg, str) for arg in [object_name, dimension_name]):
            raise TypeError("Both 'object_name' and 'dimension_name' must be strings.")
        self.object_name = object_name
        self.dimension_name = dimension_name
        self._ref_session = ref_session

    def get_name(self) -> str:
        """Returns the dimension name."""
        return self.dimension_name

    def get_attributes(self) -> list:
        """
        Retrieves the list of attributes attached to this dimension.

        Returns:
            list: A list of xplain.Attribute instances.

        Raises:
            RuntimeError: If the API call to fetch details fails.
        """
        try:
            attributes = []
            json_details = self._ref_session.get_tree_details(
                object_name=self.object_name,
                dimension_name=self.dimension_name
            )
            if json_details.get("attributes"):
                for attr_obj in json_details["attributes"]:
                    attributes.append(
                        xplain.Attribute(
                            object_name=self.object_name,
                            dimension_name=self.dimension_name,
                            attribute_name=attr_obj["attributeName"],
                            ref_session=self._ref_session
                        )
                    )
            return attributes
        except KeyError as e:
            raise KeyError(f"Missing expected key in JSON response: {e}")
        except Exception as e:
            raise RuntimeError("Failed to fetch attributes.") from e

    def get_attribute(self, attribute_name: str):
        """
        Retrieves the attribute instance with the specified name.

        Args:
            attribute_name (str): The name of the attribute to retrieve.

        Returns:
            xplain.Attribute: An instance of the attribute, or None if not found.

        Raises:
            ValueError: If 'attribute_name' is not provided or invalid.
            RuntimeError: If the API call to fetch details fails.
        """
        if not attribute_name or not isinstance(attribute_name, str):
            raise ValueError("'attribute_name' must be a non-empty string.")

        try:
            json_details = self._ref_session.get_tree_details(
                object_name=self.object_name,
                dimension_name=self.dimension_name
            )

            if json_details.get("attributes"):
                for attr_obj in json_details["attributes"]:
                    if attr_obj["attributeName"] == attribute_name:
                        return xplain.Attribute(
                            object_name=self.object_name,
                            dimension_name=self.dimension_name,
                            attribute_name=attr_obj["attributeName"],
                            ref_session=self._ref_session
                        )
            return None
        except KeyError as e:
            raise KeyError(f"Missing expected key in JSON response: {e}")
        except Exception as e:
            raise RuntimeError("Failed to fetch the attribute.") from e