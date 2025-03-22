import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
from executedQueries import apiQueries
import jsondiff
from pathlib import Path
from references.BTS1 import apiQueryOutput


class TestExecuteQueries:

    # BTS-108
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession(URL, USER, PASSWORD)

        session.startup(TESTSET)

        return session

    def test_BTS1WebapiAddAggregation(self, s1):
        s1 = xplain.Xsession(URL, USER, PASSWORD)

        s1.startup(TESTSET)

        for i in range(len(apiQueries)):
            df1 = s1.execute_query(apiQueries[i]).T.reset_index(drop=True).to_json(orient="split")
            print(i, df1)
            #print(i, df1, i, apiQueryOutput[i], jsondiff.diff(apiQueryOutput[i], df1))
            #assert len(jsondiff.diff((apiQueryOutput[i]), df1)) == 0


        assert False

        s1.terminate()
