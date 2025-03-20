import pytest
from procrastination_helper import quotes
from procrastination_helper.data.quotesData import quotes as quotes_collection


class Tests:
    @pytest.fixture
    def example_fixture(self):
        """
        An example of a pytest fixture - a function that can be used for setup and teardown.
        """
        yield

    #
    # Test functions
    #
    def test_get_returns_string(self):
        """
        Verify get() function returns a non-empty string.
        """
        for _ in range(10):
            result = quotes.get()
            assert isinstance(
                result, str
            ), f"Expected get() to return a string. Instead, it returned {type(result)}"
            assert (
                len(result) > 0
            ), f"Expected non-empty string, but got string with {len(result)} characters"

    def test_quotes_content(self):
        """
        Verify that the quotes returned are from our collection.
        """
        all_quotes_text = []
        for q in quotes_collection:
            all_quotes_text.append(f"{q['text']} - {q['author']}")

        for _ in range(10):
            result = quotes.get()
            assert (
                result in all_quotes_text
            ), f"Expected quote to be from our collection, but got: {result}"

    def test_multiple_quotes(self):
        """
        Verify that requesting multiple quotes works correctly.
        """
        for num in [2, 3, 5]:
            result = quotes.get(num_quotes=num)

            quote_count = result.count("\n") + 1

            assert quote_count == num, f"Expected {num} quotes, but found {quote_count}"
