import pytest
from simple_currency_converter.core import convert, get_currency_data


def test_get_currency_data(mock_requests_get):
    """Test the get_currency_data function."""
    mock_get, mock_response = mock_requests_get
    mock_response.json.return_value = {"aud": {"usd": 0.6712}}
    
    result = get_currency_data("aud")
    
    mock_get.assert_called_once_with(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/aud.json"
    )
    assert result == {"aud": {"usd": 0.6712}}


def test_convert(mock_get_currency_data):
    """Test the convert function."""
    mock_get_currency_data.return_value = {
        "aud": {
            "usd": 0.6712,
        }
    }
    
    result = convert("aud", "usd", 100)
    
    mock_get_currency_data.assert_called_once_with("aud")
    assert result == pytest.approx(67.12)


def test_convert_with_different_currencies(mock_get_currency_data):
    """Test conversion between different currency pairs."""
    mock_get_currency_data.return_value = {
        "eur": {
            "gbp": 0.8532,
        }
    }
    
    result = convert("eur", "gbp", 50)
    
    mock_get_currency_data.assert_called_once_with("eur")
    assert result == pytest.approx(42.66) 