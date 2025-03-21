import pytest
from faker import Faker

from wbcore.contrib.pandas.fields import YearField as PandasYearField

fake = Faker()


class TestPandasYearField:
    @pytest.mark.parametrize(
        (
            "key",
            "label",
        ),
        [
            (fake.word(), fake.word()),
        ],
    )
    def test_pandas_year_field_values(self, key, label):
        field = PandasYearField(key=key, label=label, precision=2, decimal_mark="*", delimiter=",")
        representation = field.to_dict()
        assert representation["precision"] == 0
        assert representation["decimal_mark"] == "."
        assert representation["delimiter"] == ""
