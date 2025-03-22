import xplain
from setting import (URL, USER, PASSWORD, TESTSET)
import pytest
from apis import queries
import jsondiff
from references.apis import (EXPECTED_REPSONSE_IMPORT, EXPECTED_RESPONSE_EXPORT)

class TestPerformApi:

    # BTS-108
    @pytest.fixture
    def s1(self):
        session = xplain.Xsession(URL, USER, PASSWORD)

        session.startup(TESTSET)

        return session

    def test_import_selections(self, s1):

        importSelections = s1.perform(queries[0])

        print("responseImport", importSelections)

        assert len(importSelections) == len(EXPECTED_REPSONSE_IMPORT)

    def test_export_selections(self, s1):

        importSelections = s1.perform(queries[0])

        print("responseImport", importSelections)

        exportSelections = s1.perform(queries[1])

        print("responseExport", exportSelections)

        assert len(exportSelections) == len(EXPECTED_RESPONSE_EXPORT)