import io
import json
import logging
import os
import pprint
import uuid
import numpy as np
import pandas as pd
import patsy
import requests
import statsmodels.api as sm
import urllib3
from requests.exceptions import HTTPError, RequestException, ConnectionError, Timeout
from treelib import Tree
from xplain import Xobject
from pyecharts import options as opts
from pyecharts.charts import Tree as CollabTree, Timeline, Bar
from collections import defaultdict

class Xsession:
    """
       class for managing xplain session and calling Xplain Web API.
       Each Xsession instance could manage an individual xplain session.

       Example:
           >>> from xplain import Xsession
           >>> s1 = Xsession(url="myhost:8080", user="me",
           password="secret1")
           >>> s1.terminate()

    """
    __url__ = ""

    __cookies__ = ""

    __xplain_session__ = {}

    __headers__ = ""

    __last_error__ = {}

    __id__ = ""

    __pp__ = pprint.PrettyPrinter(indent=4)

    __broadcast__ = True

    __requests_session__ = None

    """
        python client class for calling Xplain Web API
    
        Example:
            >>> from xplain import XplainSession
            >>> s = Xsession(url="myhost:8080", user="me", password="secret")

    """

    def __parse_response(self, response):
        return json.loads(response.text)

    def _build_dataframe(self, children, data_set, data_fields):
        try:
            for child in children:
                # Recursively process child nodes if they contain children
                if 'children' in child and child['children']:
                    self._build_dataframe(child['children'], data_set, data_fields)
                else:
                    # Process data fields for leaf nodes
                    for field in data_fields:
                        for rec in child.get('data', []):
                            value = rec.get(field)
                            if isinstance(value, str):
                                data_set[field].append(value)
                            elif isinstance(value, dict):
                                data_set[field].append(value.get('value'))
                            else:
                                data_set[field].append(None)
        except (KeyError, AttributeError, TypeError) as e:
            logging.error(f"An error occurred while building the dataframe: {e}")
            print(f"An error occurred while building the dataframe: {e}")
        except Exception as e:
            logging.error(f"An error occurred while building the dataframe: {e}")
            print(f"An unexpected error occurred: {e}")

    def convert_to_dataframe(self, data):
        """
            Convert result JSON to DataFrame format.

            :param data: data in JSON format
            :return: data in pandas DataFrame format
        """
        try:
            # Retrieve data fields, setting to an empty list if not provided
            data_fields = data.get("fields", [])

            # Retrieve children nodes, setting to an empty list if not provided
            children = data.get("children", [])

            # Initialize the dataset dictionary
            data_set = {field: [] for field in data_fields}

            # Populate data_set using a helper function
            self._build_dataframe(children, data_set, data_fields)

            # Convert data_set to DataFrame and return
            df = pd.DataFrame(data_set)
            return df

        except KeyError as e:
            logging.error(f"KeyError: Missing expected key in data - {e}")
            print(f"KeyError: Missing expected key in data - {e}")
        except TypeError as e:
            logging.error(f"TypeError: Invalid data type encountered - {e}")
            print(f"TypeError: Invalid data type encountered - {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")

    def __build_tree(self, tree, json_object, parent_id=None):
        try:
            root_id = uuid.uuid4()
            object_name = f"(( {json_object['objectName']} ))"
            tree.create_node(object_name, root_id, parent=parent_id)

            for dimension in json_object.get('dimensions', []):
                dimension_id = uuid.uuid4()
                tree.create_node(dimension['dimensionName'], dimension_id, parent=root_id)

                for attribute in dimension.get('attributes', []):
                    attribute_id = uuid.uuid4()
                    tree.create_node(attribute['attributeName'], attribute_id, parent=dimension_id)

            for child_object in json_object.get('childObjects', []):
                self.__build_tree(tree, child_object, root_id)

            return tree
        except Exception as e:
            raise RuntimeError(f"Error while building tree: {e}")

    def get_session_id(self):
        """
        get the current xplain session id

        :return: session id
        :rtype: string
        """
        return self.__id__

    def perform(self, payload):
        """
         Send POST request against entry point /xplainsession with payload as
         json

        :param method_call: content of xplain web api
        :type method_call: json
        :return: request response
        :rtype: json

        Example
            >>> session.perform({"method": "deleteRequest",
                                  "requestName":"abcd"})
        """
        try:
            response = self.__requests_session__.post(
                f"{self.__url__}/xplainsession",
                data=json.dumps(payload),
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
            return self.__parse_response(response)
        except Exception as e:
            raise RuntimeError(f"Error performing POST request: {e}")

    def _broadcast_update(self):
        """
        Use a WebSocket to broadcast session updates.
        """
        try:
            payload = json.dumps({"sessionId": self.__id__})
            self.__requests_session__.post(
                f"{self.__url__}/broadcast",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
        except Exception as e:
            raise RuntimeError(f"Error broadcasting update: {e}")

    def _store_error_and_show_message(self, response):
        try:
            self.__last_error__ = self.__parse_response(response)
            self.print_error()
        except Exception as e:
            logging.error(f"Error processing response: {e}")

    def print_last_stack_trace(self):
        """
        Print the stack trace of the last error.
        """
        stacktrace = self.__last_error__.get('stacktrace')
        if stacktrace:
            self.__pp__.pprint(stacktrace)

    def print_error(self):
        """
        Print the last error message.
        """
        error_messages = self.__last_error__.get('localized_error_messages')
        if error_messages:
            self.__pp__.pprint(error_messages)

    def download_result(self, filename, save_as):
        """
        download a file from result directory of server and save it to
        current local path

        :param file_name: file name in result directory
        :type file_name: string
        :param save_as: downloaded file save as local file
        :type save_as: string
        """
        try:
            download_url = f"{self.__url__}/downloadfile?filename={filename}"
            response = self.__requests_session__.get(
                download_url,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
            with open(save_as, 'wb') as file:
                file.write(response.content)
        except Exception as e:
            raise RuntimeError(f"Error downloading file '{filename}': {e}")

    def upload_data(self, file_name):
        """
        upload the file from current local directory to data directory on
        server
        :param file_name: file
        :type file_name: string
        """
        try:
            with open(file_name, 'rb') as data:
                files = {file_name: data}
                payload = json.dumps({"filename": file_name, "type": "DATA"})
                self.__requests_session__.post(
                    f"{self.__url__}/upload2data",
                    cookies=self.__cookies__,
                    headers=self.__headers__,
                    verify=False,
                    files=files,
                    data=payload
                )
        except Exception as e:
            raise RuntimeError(f"Error uploading file '{file_name}': {e}")

    def post_and_broadcast(self, payload):
        """
        Send a POST request and notify the backend of session updates.

        :param payload: JSON payload for the API request.
        """
        response = self.post(payload)
        if response.status_code == 200:
            response_json = self.__parse_response(response)
            self.store_xsession(response_json)
            if self.__broadcast__:
                self._broadcast_update()
        else:
            self._store_error_and_show_message(response)
            raise RuntimeError("POST and broadcast failed.")

    def run(self, method):
        """
        perform xplain web api method and broadcast the change to other
        client sharing with same session id

        :param method: xplain web api method in json format
        :type method: json

        """
        payload = json.dumps(method)
        self.post_and_broadcast(payload)

    def get(self, params=None):
        """
        Send a GET request to the /xplainsession endpoint.

        :param params: Optional URL parameters.
        :return: API response.
        """
        try:
            response = self.__requests_session__.get(
                f"{self.__url__}/xplainsession",
                params=params,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Error performing GET request: {e}")

    def store_xsession(self, response_json):
        """
        Store session details from the response.

        :param response_json: Response parsed as JSON.
        """
        try:
            session = response_json.get('session')
            if session:
                self.__xplain_session__ = session[0]["element"]
                self.__id__ = self.__xplain_session__.get('sessionName')
            else:
                self.__xplain_session__ = response_json
                self.__id__ = response_json.get("sessionName")
        except KeyError:
            logging.warning("No session data found in response.")

    def post(self, payload):
        """
        Send POST request against entry point /xplainsession with payload as
        json

        :param payload: xplain web api in json
        :return: request response as JSON
        """
        try:

            # Perform the POST request
            response = self.__requests_session__.post(
                f"{self.__url__}/xplainsession",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )

            # Log the response status and content for debugging
            logging.debug(f"POST {self.__url__}/xplainsession Status: {response.status_code}")
            logging.debug(f"Response Content: {response.text}")
            #print("RESPONSE:", response.json())

            # Handle non-200 status codes
            if response.status_code != 200:
                raise RuntimeError(f"POST request failed with status {response.status_code}: {response.text}")

            return response

        except Exception as e:
            raise RuntimeError(f"Error performing POST request: {e}") from e

    def _load_session(self, startup_option):
        """
        Load session details based on a startup option.

        :param startup_option: Startup configuration.
        """
        try:
            params = {"startupconfig": startup_option}
            response = self.get(params)
            if response.status_code == 200:
                payload = json.dumps({"method": "setResultsFormat", "format": "unified"})
                response = self.post(payload)
                if response.status_code == 200:
                    self.store_xsession(self.__parse_response(response))
                    logging.info(f"Session initialized with startup option: {startup_option}")
                else:
                    raise RuntimeError("Failed to set results format.")
            else:
                raise RuntimeError("Failed to load startup configuration.")
        except Exception as e:
            raise RuntimeError(f"Error during session initialization: {e}")

    def get_result(self, query_name, data_frame=True):
        """
        get the result of the query
        :param query_name: the name /id of the query
        :type query_name: string
        :return: Dataframe result of the query
        :rtype: pd.Dataframe or json
        """

        if self.__xplain_session__.get('requests') is not None:
            for xrequest in self.__xplain_session__["requests"]:
                if xrequest["requestName"] == query_name:
                    if data_frame:
                        return self.convert_to_dataframe(xrequest["results"][0])
                    else:
                        return xrequest["results"][0]

    def open_query(self, query, data_frame=True):
        """
        perform the query and keep it open, the result of this query will be
        impacted by further modification of current session, like selection
        changes

        :param query: either xplain.Query instance or JSON
        :param data_frame: if True, the result will be returned as
        dataFrame
        :return:  result of given query
        :rtype:  JSON or DataFrame, depending on parameter dataFrame
        """

        if query.__class__.__name__ == "Query":
            query = query.to_json()

        if query.get('requestName') != None:
            request_id = query['requestName']
        else:
            request_id = str(uuid.uuid4())
            query['requestName'] = request_id

        methodCall = {
            'method': 'openRequest',
            'request': query
        }

        self.run(methodCall)
        return self.get_result(request_id, data_frame)

    def terminate(self):
        """
        terminate the xplain session

        """
        self.__requests_session__.get(self.__url__ + '/logout', cookies=self.__cookies__,
                     headers=self.__headers__, verify=False)
        logging.info("logged out")

    def __init__(self, url=None, user='user',
                 password='xplainData', httpsession=None,
                 jwt_dispatch_url=None, jwt_cookie_name=None, jwt_token=None):
        """
           class for managing xplain session and calling Xplain Web API.
           Each Xsession instance could manage an individual xplain session.

           Example:
               >>> from xplain import Xsession
               >>> s1 = Xsession(url="myhost:8080", user="me",
               password="secret1")
               >>> s2 = XplainSession(url="my_other_host:8080", user="me",
               password="secret2")
               >>> s1.terminate()
               >>> s2.terminate()

           """
        urllib3.disable_warnings()
        self.__requests_session__ = httpsession or requests.Session()
        self.__headers__ = self.__requests_session__.headers

        # Auto-discover URL if not provided
        self.__url__ = url or self._discover_url()

        try:
            # Step 1: Authenticate using parameters first
            logging.info("Attempting credential-based authentication.")
            response = self._authenticate_with_credentials(user, password)

            if response.status_code == 401:
                logging.info("Authentication required (401 Unauthorized).")
                # Step 2: Choose authentication method based on provided parameters: jwt or default
                if jwt_dispatch_url and jwt_cookie_name and jwt_token:
                    logging.info("Attempting JWT-based authentication.")
                    self._authenticate_with_jwt(jwt_dispatch_url, jwt_cookie_name, jwt_token)
                else:
                    self.__requests_session__.get(f"{self.__url__}/user", verify=False)
            elif response.status_code == 200:
                self._update_csrf_token(response)
                logging.info("Already authenticated.")
            else:
                logging.warning(f"Unexpected status code during authentication: {response.status_code}")

        except HTTPError as e:
            logging.error(f"HTTP error during authentication: {e}")
        except (ConnectionError, Timeout) as e:
            logging.error(f"Network error during authentication: {e}")
        except RequestException as e:
            logging.error(f"General error during authentication: {e}")

    def _discover_url(self):
        """
        Attempts to discover the base URL automatically based on proxies or default endpoints.
        """
        logging.info("Attempting to auto-discover the base URL.")

        # Check proxy settings from the session
        proxies = self.__requests_session__.proxies
        if proxies:
            for proxy_url in proxies.values():
                try:
                    logging.info(f"Trying proxy URL: {proxy_url}")
                    # Test a common endpoint to verify the proxy
                    response = self.__requests_session__.get(f"{proxy_url}/user", verify=False, timeout=5)
                    if response.status_code in (200, 401):
                        logging.info(f"Base URL discovered via proxy: {proxy_url}")
                        return proxy_url
                except requests.RequestException:
                    logging.warning(f"Proxy URL {proxy_url} did not respond.")

        # Fallback: Try localhost as the default
        logging.info("Falling back to default URL: http://localhost:8080")
        return "http://localhost:8080"

    def _authenticate_with_jwt(self, jwt_dispatch_url, jwt_cookie_name, jwt_token):
        """
        Performs JWT-based authentication and updates CSRF token if successful.
        """
        cookies = {jwt_cookie_name: jwt_token}
        try:
            response = self.__requests_session__.get(jwt_dispatch_url, cookies=cookies, verify=False)
            response.raise_for_status()
            # After JWT authentication, update the CSRF token from the /user endpoint
            user_response = self.__requests_session__.get(f"{self.__url__}/user", verify=False)
            self._update_csrf_token(user_response)
            logging.info("JWT authentication successful.")
        except HTTPError as e:
            logging.warning(f"JWT authentication failed: {e}")

    def _authenticate_with_credentials(self, user, password):
        """
        Performs credential-based authentication and updates CSRF token if successful.
        """
        try:
            # Get initial CSRF token
            csrf_response = self.__requests_session__.get(f"{self.__url__}/user", verify=False)
            csrf_token = csrf_response.headers.get("X-CSRF-TOKEN")

            if not csrf_token:
                logging.error("CSRF token missing; cannot proceed with credential-based login.")
                return

            # if already authenticated --> update the csrf return the response
            if csrf_response.status_code == 200:
                self._update_csrf_token(csrf_response)
                logging.info("already authenticated.")
                return csrf_response

            # Prepare headers and payload for login with credentials
            headers = {'User-Agent': 'Mozilla/5.0'}
            payload = {"username": user, "password": password, "_csrf": csrf_token}

            # Attempt login with credentials
            response = self.__requests_session__.post(f"{self.__url__}/login", headers=headers, data=payload,
                                                      verify=False)
            response.raise_for_status()

            # After successful login, update CSRF token from the /user endpoint
            user_response = self.__requests_session__.get(f"{self.__url__}/user", verify=False)
            self._update_csrf_token(user_response)
            logging.info("Credential-based authentication successful.")
            return user_response
        except HTTPError as e:
            if e.response.status_code == 401:
                logging.error("Invalid username or password; authentication failed.")
            else:
                logging.warning(f"Credential-based authentication failed with HTTP error: {e}")

    def _update_csrf_token(self, response):
        """
        Updates the CSRF token in the session headers if found in response.
        """
        csrf_token = response.headers.get("X-CSRF-TOKEN")
        if csrf_token:
            self.__requests_session__.headers.update({"X-CSRF-TOKEN": csrf_token})
            self.__headers__ = self.__requests_session__.headers
            logging.info("CSRF token updated.")
        else:
            logging.warning("CSRF token not found in response headers.")

    def startup(self, startup_file):
        """
        load xplain session by given startup configuration file name without
        file extension

        :param startup_file: the file name of startup configuration,
        :type startup_file: string

        """
        try:
            self.set_default_broadcast(False)
            if not startup_file.endswith(".xstartup"):
                startup_file += ".xstartup"
            self._load_session(startup_file)
        except Exception as e:
            raise RuntimeError(f"Failed to load startup file '{startup_file}': {e}")

    def load_from_session_id(self, session_id):
        """
        load xplain session by given exisiting session id

        :param session_id: the 32 digit  xplain session id
        :type session_id: string
        """
        try:
            self.set_default_broadcast(False)
            if len(session_id) != 32:
                raise ValueError("Session ID must be exactly 32 characters.")
            self._load_session(session_id)
        except Exception as e:
            raise RuntimeError(f"Failed to load session ID '{session_id}': {e}")

    def open_attribute(self, object_name, dimension_name, attribute_name,
                       request_name=None, data_frame=True):
        """
        convinient method to open an attribute

        :param object_name: name of object
        :type object_name: string
        :param dimension_name: name of dimension
        :type dimension_name: string
        :param attribute_name: name of attribute
        :type attribute_name: string
        :param request_name: id or name of request
        :type request_name: string
        :param data_frame: if result shall be returned as pandas
        :type data_frame: boolean
        :return: attribute groupped by on first level and aggregated by count.
        :rtype: attribute: data frame or json

        Example:
            >>> session = xplain.Xsession(url="myhost:8080", user="myUser",
            password="myPwd")
            >>> session.startup("mystartup")
            >>> session.open_attribute("Patient", "Age", "Agegroup")
        """
        try:
            request_id = request_name or str(uuid.uuid4())
            method = {
                "method": "openAttribute",
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name,
                "requestName": request_id
            }
            self.run(method)
            return self.get_result(request_id, data_frame)
        except Exception as e:
            raise RuntimeError(f"Error while opening attribute: {e}")

    def get_state_hierarchy(self, object_name, dimension_name, attribute_name, state=None, levels=None, request_name=None): #, data_frame=True
        """
        Retrieve the hierarchical structure of states for a given attribute.

        :param object_name: Name of the object.
        :param dimension_name: Name of the dimension.
        :param attribute_name: Name of the attribute.
        :param state: The name of a state in the attribute's hierarchy. Optional.
        :param levels: The number of hierarchy levels to return. Optional.
        :param data_frame: Whether to return the result as a pandas DataFrame. Default is True.
        :return: Hierarchical structure of states.
        :rtype: dict or DataFrame
        """
        try:
            request_id = request_name or str(uuid.uuid4())
            method = {
                "method": "getStateHierarchy",
                "object": object_name,
                "dimension": dimension_name,
                "attribute": attribute_name,
                "requestName": request_id
            }
            if state:
                method["state"] = state
            if levels:
                method["levels"] = levels

            # Send the POST request
            # Attempt login with credentials
            response = self.__requests_session__.post(f"{self.__url__}/xplainsession", headers=self.__headers__, data=json.dumps(method), cookies=self.__cookies__, verify=False)
            response.raise_for_status()
            #self.run(method)
            return json.loads(response.text).get("stateHierarchy")
            #return self.__requests_session__.get('requests')
            #return self.get_result(request_id)
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}")
        except Exception as e:
            raise RuntimeError(f"Error while retrieving state hierarchy: {e}")

    def _pprint(self, content):
        """
        Pretty-print the provided content.

        :param content: The content to pretty-print (any).
        """
        try:
            self.__pp__.pprint(content)
        except Exception as e:
            raise RuntimeError(f"Failed to pretty-print content: {e}")

    def execute_query(self, query, data_frame=True):
        """
        execute the xplain request

        :param query: specification of the query
        :type query: Query_config or json
        :param data_frame: if True, the result will be returned as dataFrame
        :type data_frame: boolean
        :return:  result of given query
        :rtype:  JSON or DataFrame, depending on parameter dataFrame

        Example:
            >>> import xplain

            >>> session = xplain.Xsession()
            >>> session.startup('Patients')

            >>> # option 1, query config object
            >>>  query_config = xplain.Query_config()
            >>>  query_config.add_aggregation(
                                    object_name="Hospital Diagnose",
                                    dimension_name="Diagnose", type="COUNT")
            >>>  query_config.add_groupby(object_name="Hospital Diagnose",
                                          dimension_name="Diagnose",
                                          attribute_name="Type")
            >>> query_config.add_selection(object_name="Hospital Diagnose",
                                          dimension_name="Date_from",
                                          attribute_name="Date_from",
                                       selected_states=["2020-12"])
            >>> session.execute_query(query_config)

            >>> # option 2,  query in json
            >>> query = {
                    "aggregations" :[
                        {
                           "object": "AU-Diagnosen",
                           "dimension": "Diagnose",
                           "type": "SUM"
                       }
                    ],
                    "groupBys":[{
                       "attribute": {
                           "object": "Hospital Diagnose",
                           "dimension": "Diagnose",
                           "attribute": "Type"
                       }]
                }
            }
            >>> session.execute_query(query)
        """

        try:
            # Convert Query_config to JSON if necessary
            if hasattr(query, "to_json") and callable(query.to_json):
                query = query.to_json()

            if not isinstance(query, dict):
                raise ValueError("The query must be a dictionary or a Query_config object.")

            request_id = query.get("requestName")
            if request_id is None:
                request_id = f"query_{uuid.uuid4().hex[:8]}"
                query["requestName"] = request_id
                print(f"Assigned unique query name: {request_id}")


            # Prepare the method call payload
            method_call = {
                "method": "executeRequest",
                "request": query
            }

            # Execute the query and fetch results
            self.run(method_call)
            return self.get_result(request_id, data_frame)

        except AttributeError as e:
            raise ValueError("Invalid query object provided. Ensure it has a 'to_json' method if using Query_config.") from e
        except Exception as e:
            raise RuntimeError(f"An error occurred while executing the query: {e}") from e

    def show_tree(self):
        """
        show object tree

        :return: render the object hierarchy as a tree
        :rtype: string
        :raises RuntimeError: if the session is not properly initialized.
        :raises Exception: if an unexpected error occurs.
        """
        new_tree = Tree()
        try:
            session = self.get()
            session = json.loads(session.text)
            #self.store_xsession(session)
            # Attempt to build the tree with the session's 'focusObject'
            tree = self.__build_tree(new_tree, session.get('focusObject'), parent_id=None)
        except KeyError:
            # Missing 'focusObject' key in session dictionary
            raise RuntimeError("Unable to show tree: 'focusObject' is not set. "
                               "Have you run the startup method to initialize the session?")
        except AttributeError:
            # Session or focusObject attribute might not be initialized
            raise RuntimeError("Session appears uninitialized. Ensure that 'startup' has been called to set up the session.")
        except Exception as e:
            # Catch-all for any other unexpected errors
            raise Exception("An unexpected error occurred while attempting to show the tree. "
                            "Please check your inputs and session initialization.") from e
        else:
            print(str(tree))

    def show_tree_details(self):
        """
        Display the details of the object tree.
        """
        try:
            self._pprint(self.__xplain_session__.get('focusObject'))
        except Exception as e:
            logging.error(f"Failed to show tree details: {e}")
            raise Exception(f"Failed to show tree details: {e}")

    def get_session(self):
        return self.__xplain_session__

    def get_selections(self):
        """
        display all global selections in the current xplain session

        :return: selections as json
        :rtype: list of json
        """
        if self.__xplain_session__.get('globalSelections') is not None:
            return self.__xplain_session__['globalSelections']

    def download_selections(self, objects, selection_set=None):
        """
        returns the selection as json for given objects and selection set

        :param objects: list of object names
        :type objects: list of strings
        :param selectionSet: the selection set name
        :type selectionSet: string
        """
        try:
            method = {
                "method": "downloadSelections",
                "objects": objects,
                "selectionSet": selection_set
            }
            result = self.perform(method)
            # check if dic has key "error"


            if "error" in result:
                return {}

            if 'selections' in result:
                return result['selections']

            if 'selection' in result:
                return result['selection']

            return {}

        except Exception as e:
            logging.warning(f"Error downloading selections: {e}")
            return {}


    def get_object_info(self, object_name, root=None):
        """
        find and display the details of a xobject in json

        :param object_name:
        :param root: the object name from where the search starts. if none
        root is provided, the root node of the entire
        object tree
        :return: details of the Xobject in json
        """
        try:
            result = self._get_object_info(object_name, root)
            if result:
                return result
            raise ValueError(f"Object '{object_name}' not found in session.")
        except ValueError as ve:
            logging.error(ve)
            raise
        except Exception as e:
            logging.error(f"Error retrieving object info: {e}")
            raise RuntimeError("Unexpected error occurred while fetching object details.")

    def _get_object_info(self, object_name, root=None):
        """
        Helper method to find an object in the tree recursively.
        """
        if root is None:
            root = self.get_session().get('focusObject')

        if root.get('objectName') == object_name:
            return root

        for child in root.get('childObjects', []):
            result = self._get_object_info(object_name, child)
            if result:
                return result

        return None

    def get_dimension_info(self, object_name, dimension_name):
        """
        find and retrieves the details of a dimension

        :param object_name: the name of the xobject
        :param dimension_name: the name of dimension
        :return: details of this dimension in json format
        """
        try:
            obj = self.get_object_info(object_name)
            for dim in obj.get('dimensions', []):
                if dim.get('dimensionName') == dimension_name:
                    return dim
            raise ValueError(f"Dimension '{dimension_name}' not found in object '{object_name}'.Please check if the session is initialized correctly or if you have a typo in the dimension name.")
        except ValueError as ve:
            logging.error(ve)
            raise
        except Exception as e:
            logging.error(f"Error retrieving dimension info: {e}")
            raise RuntimeError("Unexpected error occurred while fetching dimension details.")

    def get_attribute_info(self, object_name, dimension_name, attribute_name):
        """
        find and retrieves the details of an attribute

        :param object_name: the name of xobject
        :param dimension_name: the name of dimension
        :param attribute_name: the name of attribute
        :return: details of this attribute in json format
        """

        try:
            dimension = self.get_dimension_info(object_name, dimension_name)
            for attr in dimension.get('attributes', []):
                if attr.get('attributeName') == attribute_name:
                    return attr
            raise ValueError(f"Attribute '{attribute_name}' not found in dimension '{dimension_name}' of object '{object_name}'.")
        except ValueError as ve:
            logging.error(ve)
            raise
        except Exception as e:
            logging.error(f"Error retrieving attribute info: {e}")
            raise RuntimeError("Unexpected error occurred while fetching attribute details.")

    def get_tree_details(self, object_name=None, dimension_name=None, attribute_name=None):
        """
        get the metadata details of certain xplain object, dimension or
        attribute as json

        :param object_name:  the name of object optional , if empty, show the
        whole object tree from root,  if only objectName is specified,
        this funtion will return the metadata of
                 this object
        :type    object_name: string, optional
        :param dimension_name:  the name of dimension, optional,
        it object_name and dimension_name are specified, it will return the
        dimesion metadata
        :type    dimension_name: string, optional
        :param attribute_name:  the name of attribute, optional,
        it object_name, dimension_name and attribute_name is specified,
        it will return the attribute metadata
        :type    attribute_name: string, optional
        :return: object tree details
        :rtype: json
        """

        try:
            if not any([object_name, dimension_name, attribute_name]):
                return self.__xplain_session__.get('focusObject')

            if object_name and not dimension_name and not attribute_name:
                return self.get_object_info(object_name)

            if object_name and dimension_name and not attribute_name:
                return self.get_dimension_info(object_name, dimension_name)

            if object_name and dimension_name and attribute_name:
                return self.get_attribute_info(object_name, dimension_name, attribute_name)
        except Exception as e:
            logging.error(f"Error retrieving tree details: {e}")
            raise RuntimeError("Unexpected error occurred while fetching tree details.")

    def get_root_object(self):
        """
        [Beta] Retrieve the root object.

        :return: The root object.
        :rtype: Xobject
        :raises KeyError: If 'focusObject' or 'objectName' is missing from the session.
        """
        try:
            root_object_name = self.__xplain_session__.get('focusObject', {}).get('objectName')
            return Xobject(root_object_name, self)
        except KeyError as e:
            raise KeyError(f"Missing expected key in session data: {e}") from e

    def get_xobject(self, object_name):
        """
        [Beta] Retrieve the object with the given name.

        :param object_name: The name of the object to retrieve.
        :type object_name: str
        :return: The object with the given name, or None if not found.
        :rtype: Xobject or None
        """
        try:
            object_info = self.get_object_info(object_name)
            if object_info:
                return Xobject(object_info["objectName"], self)
            return None
        except Exception as e:
            raise RuntimeError(f"Error retrieving Xobject for '{object_name}': {e}") from e

    def resume_analysis(self, file_name):
        """
        resume the stored session

        :param file_name: name of stored session file
        :type file_name: string
        :return:  False (fail) or True (success)
        :rtype: Boolean
        """
        try:
            if not file_name.endswith(".xanalysis"):
                file_name += ".xanalysis"

            method_call = {
                "method": "resumeAnalysis",
                "fileName": file_name
            }
            self.post(method_call)
            return True
        except Exception as e:
            print(f"Error resuming analysis with file '{file_name}': {str(e)}")
            logging.error(f"Error resuming analysis with file '{file_name}': {e}")
            raise

    def get_queries(self):
        """
        get the list of the existing query ids

        :return: list of query ids
        :rtype: array of string
        """
        result = []
        requests = self.__xplain_session__["requests"]
        for req in requests:
            result.append(req["requestName"])
        return result

    def refresh(self):
        """
        synchronize the session content with the backend

        """
        try:
            response_json = self.__parse_response(self.get())
            self.store_xsession(response_json)
        except Exception as e:
            print(f"Error refreshing session: {str(e)}")
            logging.error(f"Error refreshing session: {e}")
            raise

    def get_model_names(self):
        """
        list all loaded predictive models

        :return: list of model names
        :rtype: array of string
        """
        try:
            models = self.get_session().get("predictiveModels", {})
            return list(models.keys())
        except Exception as e:
            print(f"Error retrieving model names: {str(e)}")
            logging.error(f"Error retrieving model names: {e}")
            raise

    def get_variable_list(self, model_name):
        """
        get the list of independent variables of given predictive model

        :param model_name: name of predictive model
        :type model_name: string
        :return: list of independent variables
        :rtype: array of string
        """
        try:
            models = self.get_session().get("predictiveModels", {})
            model = models.get(model_name)

            if model is None:
                warning_message = f"Model '{model_name}' not found."
                print(warning_message)
                logging.warning(warning_message)
                return []

            return [var["name"] for var in model.get("independentVariables", [])]
        except Exception as e:
            print(f"Error retrieving variables for model '{model_name}': {str(e)}")
            logging.error(f"Error retrieving variables for model '{model_name}': {e}")
            raise

    def build_predictive_model(self, model_name, model_config,
                               model_object_name, significance,
                               target_event_object_name,
                               target_selection_object_name,
                               target_selection_dimension_name,
                               target_selection_attribute,
                               output_prefix=''):
        """
        build predictive model [BETA!!]

        :param model_name: model name
        :type model_name: string
        :param xmodel_config: xmodel configuration file
        :type xmodel_config: string
        :param model_object_name: model object name
        :type model_object_name: string
        :param significance: significance 0.0 - 1.0
        :type significance: float
        :param target_event_object_name: target even object name
        :type target_event_object_name: string
        :param target_selection_object_name: target selection object name
        :type target_selection_object_name: string
        :param target_selection_dimension_name: target selection dimension name
        :type target_selection_dimension_name: string
        :param target_selection_attribute: target selection attribute name
        :type target_selection_attribute: string
        :param output_prefix: prefix of output csv files on file system,
        default is empty
        :type output_prefix: string
        :return: results of predictive model as dictionary of
        padas dataframes which includs independent varialbes,
        observations, learning log,
        predicted probabilities, ROC
        :rtype: dictionary

        Example:
            >>> Xsession.build_predictive_model(model_name='Depression',
                                xmodel_config='DEPRESSION - demo.xmodel',
                                model_object_name='Person',
                                significance=0.9,
                                target_event_object_name='Diagnosen',
                                target_selection_object_name='Diagnosen',
                                target_selection_dimension_name='Type',
                                target_selection_attribute='Type')

        """
        if model_config.find('.xdefaultmodel') == -1 and model_config.find(
                '.xmodel') == -1:
            model_config = model_config + '.xmodel'

        query = {
            "method": "buildPredictiveModel",
            "significance": significance,
            "modelName": model_name,
            "targetSelectionAttributes": [
                {
                    "attribute": target_selection_attribute,
                    "dimension": target_selection_dimension_name,
                    "object": target_selection_object_name
                }
            ],
            "modelObject": model_object_name,
            "xmodelConfigurationName": model_config,
            "targetEventObject": target_event_object_name
        }
        self.run(query)
        result = {}

        df_independent_var = self.load_file_as_df(str(output_prefix or '') +
                                                  model_name + str(
            '-IndependentVariables.csv'))

        df_learning_log = self.load_file_as_df(str(output_prefix or '') +
                                               model_name +
                                               '-Learning-Log.txt')

        df_observation = self.load_file_as_df(
            str(output_prefix or '') + model_name +
            "-Observations.csv")

        df_predicted_probabilities = self.load_file_as_df(
            str(output_prefix or '') +
            model_name +
            '-PredictedProbabilities.csv')
        df_roc = self.load_file_as_df(
            str(output_prefix or '') + model_name + '-ROC.csv')
        result["IndependentVariables"] = df_independent_var
        result["Learning - Log"] = df_learning_log
        result["Observation"] = df_observation
        result["PredictedProbabilities"] = df_predicted_probabilities
        result["ROC"] = df_roc
        return result

    def load_file_as_df(self, filename):
        """
        Load a file from the session as a pandas DataFrame.

        :param filename: Name of the file to load.
        :return: DataFrame containing file content.
        """
        try:
            response = self.__requests_session__.get(
                f"{self.__url__}/readfile?filename={filename}",
                cookies=self.__cookies__,
                verify=False
            )
            if response.status_code == 200:
                return pd.read_csv(io.StringIO(response.text), sep=';')
            raise FileNotFoundError(f"File '{filename}' could not be found.")
        except Exception as e:
            logging.error(f"Error loading file '{filename}': {e}")
            raise

    def post_file_download(self, file_name, file_type, ownership="PUBLIC", team=None, user=None,
                           delete_after_download=True):
        """
        Triggers the flat table download functionality in XOE.

        :param file_name: Name of the file to be downloaded.
        :param file_type: Type of the file.
        :param ownership: Ownership type, defaults to "PUBLIC".
        :param team: Team identifier, optional.
        :param user: User identifier, optional.
        :param delete_after_download: Whether to delete the file after download, defaults to True.
        :return: HTTP response object or raises exception on failure.
        """

        try:
            # Prepare the payload
            payload = json.dumps({
                "file": {
                    "ownership": ownership,
                    "fileType": file_type,
                    "filePath": [file_name],
                    "team": team,
                    "user": user
                }
            })

            # Perform file download
            download_url = f"{self.__url__}/download_file"
            response = self.__requests_session__.post(
                download_url,
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )

            # Check response status, used response.raise_for_status() to handle HTTP errors cleanly.
            response.raise_for_status()

            # Delete the file after download if specified
            if delete_after_download:
                delete_url = f"{self.__url__}/remove_file"
                delete_response = self.__requests_session__.post(
                    delete_url,
                    data=payload,
                    cookies=self.__cookies__,
                    headers=self.__headers__,
                    verify=False
                )
                delete_response.raise_for_status()

            return response

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to process file download: {e}") from e

    def set_default_broadcast(self, broadcast):
        """
        set default broadcast behaviour so that other xplain client sharing
        the same xplain session could get informed about the update of
        current xplain session.

        :param broadcast: after successful session update via python call,
        if a default
        refresh signal should be broadcasted to all xplain clients those are
        sharing the same xplain session, in order to force them to perform the
        refresh to get the most current session.
        :type broadcast: boolean

        """
        self.__broadcast__ = broadcast

    def open_sequence(self, target_object,
                      base_object,
                      ranks, reverse, names, name_postfixes,
                      dimensions_2_replicate, sort_dimension,
                      zero_point_dimension,
                      selections,
                      selection_set_definition_rank,
                      floating_semantics, attribute_2_copy,
                      sequence_name, rank_dimension_name,
                      rank_zero_is_first_instance_equal_or_greater_zero_point,
                      transition_attribute, transition_level,
                      open_marginal_queries,
                      open_transition_queries,
                      selection_set
                      ):
        sequence_request = dict(method="openSequence",
                                targetObject=target_object,
                                ranks=ranks,
                                reverse=reverse,
                                names=[names],
                                namePostfixes=name_postfixes,
                                dimensionsToReplicate=[dimensions_2_replicate],
                                sortDimension=sort_dimension,
                                baseObject=base_object,
                                zeroPointDimension=zero_point_dimension,
                                # selections=selections,
                                selectionSetDefiningRank=selection_set_definition_rank,
                                floatingSemantics=floating_semantics,
                                attributesToCopy=[[attribute_2_copy]],
                                sequenceNames=[sequence_name],
                                rankDimensionName=[rank_dimension_name],
                                rankZeroIsFirstInstanceEqualOrGreaterZeroPoint
                                =rank_zero_is_first_instance_equal_or_greater_zero_point,
                                transitionAttribute=transition_attribute,
                                transitionLevel=transition_level,
                                openMarginalQueries=open_marginal_queries,
                                openTransitionQueries=open_transition_queries,
                                selectionSet=selection_set
                                )

        cleaned_req = {k: v for k, v in sequence_request.items() if v is not None}
        self.run(cleaned_req)

    def get_open_sequences(self, sequence_name):
        """Retrieves details of open sequences by name."""
        return self.__xplain_session__["openSequences"].get(sequence_name, {})

    def get_sequence_transition_matrix(self, sequence_name):
        """
        Retrieves the transition matrix for the specified sequence.

        :param sequence_name: Name of the sequence.
        :return: Transition matrix as a dictionary with labels, sources, targets, and values.
        """
        label, source, target, value = [], [], [], []

        transition_queries = self.get_open_sequences(sequence_name).get('transitionQueryNames', [])
        for query_name in transition_queries:
            df = self.get_result(query_name)
            col = list(df.columns)

            for _, row in df.iterrows():
                source_node = f"{col[0].split('. ')[0]} {row[col[0]]}"
                target_node = f"{col[1].split('. ')[0]} {row[col[1]]}"

                if source_node not in label:
                    label.append(source_node)
                source.append(label.index(source_node))

                if target_node not in label:
                    label.append(target_node)
                target.append(label.index(target_node))

                value.append(row[col[2]])

        return {"label": label, "source": source, "target": target, "value": value}

    '''
    Todo: Implement the following methods
    '''
    def gen_xtable(self, data, xtable_config, file_name):
        pass



    def list_files(self, ownership, file_type, file_extension=None):
        """
        Lists files with the specified ownership and type.

        :param ownership: Ownership type.
        :param file_type: File type.
        :param file_extension: Optional file extension.
        :return: List of files or raises exception on failure.
        """
        payload = {
            "file": {
                "ownership": ownership,
                "fileType": file_type
            }
        }
        if file_extension:
            payload["fileExtension"] = file_extension

        try:
            response = self.__requests_session__.post(
                f"{self.__url__}/list_files",
                data=json.dumps(payload),
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to list files: {e}") from e

    def read_file(self, ownership, file_type, file_path):
        """
        Reads the specified file.

        :param ownership: Ownership type.
        :param file_type: File type.
        :param file_path: Path of the file.
        :return: File content or raises exception on failure.
        """
        payload = json.dumps({
            "file": {
                "ownership": ownership,
                "fileType": file_type,
                "filePath": file_path
            }
        })

        try:
            response = self.__requests_session__.post(
                f"{self.__url__}/read_file",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to read file: {e}") from e

    def validate_db(self, db_connection_config):
        """
        Validates a database connection configuration.

        :param db_connection_config: Dictionary containing DB connection settings.
        :raises RuntimeError: If validation fails or an error occurs.
        """
        payload = json.dumps({"databaseConnectionConfiguration": db_connection_config})

        try:
            response = self.__requests_session__.post(
                f"{self.__url__}/db_tables",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = f"Database validation failed: {str(e)}"
            if response is not None:
                try:
                    error_details = response.json().get("message", response.text)
                    error_message += f" Details: {error_details}"
                except json.JSONDecodeError:
                    error_message += f" Details: {response.text}"
            raise RuntimeError(error_message) from e

    def run_py(self, file_name, options, ownership):
        """
        Executes a Python script file on the server.

        :param file_name: Name of the Python file.
        :param options: Execution options.
        :param ownership: File ownership type.
        :return: Parsed JSON result or raw content.
        :raises RuntimeError: If the request fails.
        """
        payload = json.dumps({
            "file": {
                "ownership": ownership,
                "fileType": "XSCRIPT",
                "filePath": [file_name],
            },
            "options": options,
        })

        try:
            response = self.__requests_session__.post(
                f"{self.__url__}/run_python_file",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Running Python file failed: {str(e)}"
            if response is not None:
                try:
                    error_message += f" Details: {response.text}"
                except json.JSONDecodeError:
                    pass
            raise RuntimeError(error_message) from e

    def http_get(self, entrypoint, params=None):
        """
        Performs an HTTP GET request to the specified endpoint.

        :param entrypoint: API endpoint relative to the base URL.
        :param params: Query parameters for the GET request.
        :return: Parsed JSON response or raw content.
        :raises RuntimeError: If the GET request fails.
        """
        try:
            response = self.__requests_session__.get(
                f"{self.__url__}{entrypoint}",
                params=params,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"GET request failed for {entrypoint}: {str(e)}"
            if response is not None:
                error_message += f" Details: {response.text}"
            logging.warning(error_message)
            raise RuntimeError(error_message) from e

    def http_post(self, entrypoint, payload_json=None):
        """
        Performs an HTTP POST request to the specified endpoint.

        :param entrypoint: API endpoint relative to the base URL.
        :param payload_json: Dictionary payload for the POST request.
        :return: Parsed JSON response or raw content.
        :raises RuntimeError: If the POST request fails.
        """
        payload = json.dumps(payload_json or {})

        try:
            response = self.__requests_session__.post(
                f"{self.__url__}{entrypoint}",
                data=payload,
                cookies=self.__cookies__,
                headers=self.__headers__,
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"POST request failed for {entrypoint}: {str(e)}"
            if response is not None:
                error_message += f" Details: {response.text}"
            logging.warning(error_message)
            raise RuntimeError(error_message) from e

    def build_tree_data(self, json_object):
        """
        Convert complex JSON structure into a format suitable for D3.js tree visualization.
        This recursively parses the JSON, building a nested dictionary format compatible with D3.js.
        """
        try:
            # Root node
            node = {
                "name": json_object["objectName"],
                "type": "object",   # Add type here
                "children": []
            }

            # Add dimensions as children nodes
            for dimension in json_object.get("dimensions", []):
                dim_node = {"name": dimension["dimensionName"], "type": "dimension", "children": []}

                # If dimension has attributes, add them as sub-children
                if "attributes" in dimension:
                    for attribute in dimension["attributes"]:
                        attr_node = {
                            "name": attribute["attributeName"],
                            "type": "attribute"  # Add type here
                        }
                        dim_node["children"].append(attr_node)

                # Append dimension node to the main node
                node["children"].append(dim_node)

            # Recursively process child objects if any
            for child_object in json_object.get("childObjects", []):
                child_node = self.build_tree_data(child_object)
                child_node["type"] = "childObject"  # Mark child nodes as childObject
                node["children"].append(child_node)

            return node
        except Exception as e:
            logging.error(f"Error building tree data: {e}")
            raise RuntimeError("Failed to convert JSON to tree data.")

    def collapsible_tree(self):
        """
        Generate and visualize a collapsible tree using hierarchical data.

        This function builds a tree structure based on the current focus object, processes it into
        a source-target DataFrame suitable for visualization, and then uses pyecharts to render the tree
        directly in Jupyter.

        Example:
            Xsession.collapsible_tree()

        Args:
            None

        Returns:
            None: The function directly renders the visualization in the notebook.
        """

        # Build the hierarchical data (df1)
        df1 = self.build_tree_data(self.__xplain_session__.get('focusObject'))

        # Create the tree using pyecharts
        tree = (
            CollabTree()
            .add("", [df1], collapse_interval=2)
            .set_global_opts(title_opts=opts.TitleOpts(title="Collapsible Tree"))
        )

        tree.render("tree_left_right.html")
        # Render the tree directly to the notebook
        tree.render_notebook()  # This renders directly inside the notebook

    def get_instance_as_dataframe(self, elements):
        """
        get a pandas dataframe representation of the xplain artifacts
        references by elements,
        equivalent to the standard csv download functionality in XOE

        :param elements: array of x-element paths, each one referring a
        Xplain artifact, an object,
        a dimension or an attribute
        :type elements: list
        :return: Dataframe representation of requested instance
        :rtype: pd.Dataframe

        Example:
                elements: [
                 {"object": "Person"},
                 {"object": "Diagnosis", "dimension": "Physician"},
                 {"object": "Prescription", "dimension": "Rx Code",
                 "attribute": "ATC Hierarchy"},
                 {"object": "Prescription", "dimension": "Rx Code",
                 "attribute": "Substance"}
                ],

        """
        filename = "Flat Table Export.csv"
        self.run({
            "method": "saveAsCSV",
            "elements": elements,
        })
        response = self.post_file_download(file_name=filename,
                                                        file_type="EXPORT_CSV"
                                                        )
        if response.ok:
            open(filename, 'wb').write(response.content)
            dataframe = pd.read_csv(filename, sep=';')
            os.remove(filename)
            return dataframe
        else:
            # Log the error for developers or for detailed logs
            logging.error("could not get instance as dataframe " + response.content.decode('utf-8'))

            # Raise a user-facing error in Jupyter
            raise Exception(f"Error: Could not get instance as dataframe '"
                            f"{response.content.decode('utf-8')}'.")

    def get_variable_details(self, model_name, data_frame=True):
        """
        Retrieve the details of the independent variables for a predictive model.

        :param model_name: The name of the predictive model.
        :type model_name: str
        :param data_frame: Whether to return the result as a pandas DataFrame.
        :type data_frame: bool
        :return: The model's independent variables details as a DataFrame or JSON.
        :rtype: pd.DataFrame or dict
        :raises ValueError: If the predictive model or its variables are not found.
        """
        try:
            session_data = self.get_session()
            predictive_models = session_data.get("predictiveModels", {})
            model_data = predictive_models.get(model_name)

            if not model_data:
                raise ValueError(f"Predictive model '{model_name}' not found in session.")

            result = model_data.get("independentVariables")
            if result is None:
                raise ValueError(f"No independent variables found for model '{model_name}'.")

            return pd.json_normalize(result) if data_frame else result

        except Exception as e:
            raise RuntimeError(f"Error retrieving variable details for model '{model_name}': {e}") from e


    def create_contingency_table(self, df, var1, var2):
        """
        Create a contingency table (frequency table) for two variables.

        Args:
            df (pd.DataFrame): The data frame containing the variables.
            var1 (str): Name of the first variable (row).
            var2 (str): Name of the second variable (column).

        Returns:
            pd.DataFrame: A contingency table.
        """
        if var1 not in df.columns or var2 not in df.columns:
            raise ValueError(f"Both {var1} and {var2} must be in the DataFrame.")

        contingency_table = pd.crosstab(df[var1], df[var2])
        logging.info(f"Contingency table created for {var1} and {var2}.")
        return contingency_table

    def run_statsmodels(self, df, formula, model_type="logit"):
        """
        Fit a statistical model to the provided dataframe using the specified formula and model type.

        Args:
            df (pandas.DataFrame): The input dataframe containing the data.
            formula (str): A Patsy-compatible formula specifying the dependent and independent variables.
            model_type (str): The type of model to fit. Supported options are 'logit', 'probit', 'ols',
                              'mnlogit', 'glm', 'poisson', 'negative_binomial'. Default is 'logit'.

        Returns:
            statsmodels.regression.linear_model.OLSResults or
            statsmodels.discrete.discrete_model.LogitResults or
            other statsmodels result object depending on the model_type.

        Raises:
            ValueError: If the model_type is unsupported or if the dependent variable is not appropriate
                        for the chosen model (e.g., non-binary dependent variable for logit/probit).
        """
        df = df.rename(columns=lambda x: x.replace(".", "_"))
        formula = formula.replace(".", "_")

        y, X = patsy.dmatrices(formula, data=df, return_type="dataframe")

        model_map = {
            "logit": self._run_logit,
            "probit": self._run_probit,
            "ols": self._run_ols,
            "mnlogit": self._run_mnlogit,
            "glm": self._run_glm,
            "poisson": self._run_poisson,
            "negative_binomial": self._run_negative_binomial,
        }

        if model_type not in model_map:
            raise ValueError(f"Unsupported model type: {model_type}")

        return model_map[model_type](y, X)

    def _run_logit(self, y, X):
        if not np.all((y >= 0) & (y <= 1)):
            raise ValueError("Dependent variable must be binary (0 or 1) for logistic regression.")
        return sm.Logit(y, X).fit()

    def _run_probit(self, y, X):
        if not np.all((y >= 0) & (y <= 1)):
            raise ValueError("Dependent variable must be binary (0 or 1) for probit regression.")
        return sm.Probit(y, X).fit()

    def _run_ols(self, y, X):
        return sm.OLS(y, X).fit()

    def _run_mnlogit(self, y, X):
        return sm.MNLogit(y, X).fit()

    def _run_glm(self, y, X):
        from statsmodels.genmod.families import Gaussian
        return sm.GLM(y, X, family=Gaussian()).fit()

    def _run_poisson(self, y, X):
        return sm.Poisson(y, X).fit()

    def _run_negative_binomial(self, y, X):
        return sm.NegativeBinomial(y, X).fit()

    def build_formula(self, response, predictors):
        """
        Dynamically build an R-style formula for Patsy.

        Args:
            response (str): The dependent variable.
            predictors (list): A list of predictor variable names.

        Returns:
            str: The constructed formula in R-style syntax.
        """
        cleaned_predictors = [pred.strip() for pred in predictors]

        formula = f"{response} ~ {' + '.join(cleaned_predictors)}"

        logging.info(f"Constructed formula: {formula}")
        return formula
