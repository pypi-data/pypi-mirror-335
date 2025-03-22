# xplain python package

This is a python package which you can use to perform object data analysis 
on xplain. 

# Testing

Test your code by runing the pytest, for example for the single file:
`python3 -m pytest test/test_xsession.py
`

To run all the pytest, just run
`python3 -m pytest
`
# changelog
### 2025-02-27
+ download_selections method 
* bugfix show_tree

* run_statsmodels
* create_contingency_table
* build_formular
* collapsible_tree
* http_get
* http_post
* run_py




### 2024-07-02
enable JWT auth.

### 2024-03-12
* replace print message with logging
* bugfix: POST payload issue with missing json.dumps
* bugfix: session hijacking issue in pyodide environment
* add http_post and http_get methods

### 2023-12-20
* ssl verify false by login

### 2023-09-06
* bugfix: get_instance_as_dataframe doesn't download the exported csv

### 2023-07-31
* add aggregation_name parameter to query_config.add_aggregation function

### 2023-06-06
* bugfix: build_predictive_model returns error by reading result

### 2023-05-11
add validate_db

### 2023-05-05
* add Xsession.list_files() Xsession.read_file()
* Xsession.startup(file_name), file extension optional 




