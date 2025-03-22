import xplain
from setting import (URL, USER, PASSWORD, TESTSET, SESSIONID)
import secrets
from queries import queries
import jsondiff

# Getting systemRandom class instance out of secrets module
secretsGenerator = secrets.SystemRandom()

# In Process: unit test each xplain py function to work as expected
# In Process: load each api and compare the results
# In Process: load each python analysis and compare the results

# secure random integer numbers
random_number = secretsGenerator.randint(0, 1)
print(random_number)
# Output 
query = queries[random_number]

query.get("content")


# BTS-106
def test_query_config():
    s1 = xplain.Xsession(URL, USER, PASSWORD)

    s1.startup(TESTSET)

    s1.execute_query(query)

    # option 1, query config object
    query_config = xplain.QueryConfig()
    query_config_input_aggregations = query.get("aggregations")[0]
    print(query_config_input_aggregations)
    query_config_input_group_bys = query.get("groupBys")[0].get("attribute")
    print(query_config_input_group_bys)
    query_config_input_selections = query.get("selections")[0]
    print(query_config_input_selections)
    query_config.aggregation(
        object_name=query_config_input_aggregations.get("object"),
        dimension_name=query_config_input_aggregations.get("dimension"),
        type=query_config_input_aggregations.get("type"))\
        .groupby(object_name=query_config_input_group_bys.get("object"),
                             dimension_name=query_config_input_group_bys.get("dimension"),
                             attribute_name=query_config_input_group_bys.get("attribute"))\
        .selection(object_name=query_config_input_selections.get("attribute").get("object"),
                               dimension_name=query_config_input_selections.get("attribute").get("dimension"),
                               attribute_name=query_config_input_selections.get("attribute").get("attribute"),
                               selected_states=query_config_input_selections.get("selectedStates"))
    print("query_config:", query_config)
    df1 = s1.execute_query(query_config).T.reset_index(drop=True).to_json(orient="split")
    print("df1:", df1)

    # query = queries[random_number]

    df2 = s1.execute_query(query).T.reset_index(drop=True).to_json(orient="split")
    print("df2:", df2)

    assert len(jsondiff.diff(df1, df2)) == 0

    s1.terminate()
