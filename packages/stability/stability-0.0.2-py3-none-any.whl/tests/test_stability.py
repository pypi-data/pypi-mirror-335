import pandas as pd

from stability.decorators import expected


@expected
def test_expected_decorator_basics():
    df = pd.DataFrame({
        'str_col': ['a', 'b'],
        'int_col': [1, 2],
        'float_col': [3.14159, -1],
    })
    return df