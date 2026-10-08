import pytest

def reverse(input_list):
    if len(input_list) == 1:
        return [input_list[0]]

    return reverse(input_list[len(input_list) // 2 :]) + reverse(
        input_list[: len(input_list) // 2]
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [([1, 2], [2, 1]), 
     ([1, 2, 3], [3, 2, 1]), 
     ([1, 2, 3, 4], [4, 3, 2, 1]),
     (['hi', 'there'], ['there', 'hi'])],
)
def test_reverse(test_input, expected):
    assert reverse(test_input) == expected