import xplain
import json

class Attribute:
    def __init__(self, object_name, dimension_name, attribute_name, ref_session):
        self.object_name = object_name
        self.dimension_name = dimension_name
        self.attribute_name = attribute_name
        self._ref_session = ref_session

    def get_name(self):
        """
        Retrieves the name of the attribute.
        :return: Attribute name as a string.
        """
        return self.attribute_name

    def get_levels(self):
        """
        Retrieves the hierarchy level names of this attribute.

        :return: List of hierarchy level names as strings.
        :raises ValueError: If attribute information is not found or data is invalid.
        """
        try:
            json_details = self._ref_session.get_attribute_info(
                object_name=self.object_name,
                dimension_name=self.dimension_name,
                attribute_name=self.attribute_name
            )

            # Use `.get()` and explicitly check for missing value
            levels = json_details.get("hierarchyLevelNames")
            if levels is None:
                raise ValueError(f"'hierarchyLevelNames' is missing for attribute '{self.attribute_name}'.")

            return levels

        except AttributeError as e:
            raise ValueError(f"Attribute information retrieval failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while fetching levels: {str(e)}")

    def get_state_hierarchy(self, state=None, levels=None):
        """
        state hierarchy of this attribute
        :return: hierarcy as JSON
        """
        return self._ref_session.get_state_hierarchy(self.object_name, self.dimension_name, self.attribute_name, state, levels)

    def get_root_state(self):
        """
        returns the root state of this attribute
        :return: string
        """
        return json.loads(self.get_state_hierarchy()).get("stateName")
