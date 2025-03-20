import pytest
import sys
import io
from unittest.mock import patch, MagicMock
from simple_currency_converter.__main__ import main


def test_cli_convert():
    """Test the CLI currency conversion functionality."""
    # Patch both stdout and the convert function
    stdout = io.StringIO()
    with patch("sys.stdout", stdout):
        with patch("simple_currency_converter.__main__.convert") as mock_convert:
            mock_convert.return_value = 67.12
            
            with patch.object(sys, "argv", ["simple-currency-converter", "aud", "usd", "100"]):
                main()
        
            mock_convert.assert_called_once_with("aud", "usd", 100.0)
    
    # Check stdout after the context manager is exited
    output = stdout.getvalue().strip()
    assert output == "67.12000000"


@patch("simple_currency_converter.__main__.list_currencies")
def test_cli_list_all_currencies(mock_list_currencies):
    """Test the CLI list all currencies functionality."""
    with patch.object(sys, "argv", ["simple-currency-converter", "--list-all-currencies"]):
        main()
    
    mock_list_currencies.assert_called_once()


@patch("simple_currency_converter.__main__.list_currencies")
def test_cli_list_common_currencies(mock_list_currencies):
    """Test the CLI list common currencies functionality."""
    with patch.object(sys, "argv", ["simple-currency-converter", "--list-common-currencies"]):
        main()
    
    mock_list_currencies.assert_called_once()


@patch("simple_currency_converter.__main__.list_currencies")
def test_cli_list_crypto_currencies(mock_list_currencies):
    """Test the CLI list crypto currencies functionality."""
    with patch.object(sys, "argv", ["simple-currency-converter", "--list-crypto-currencies"]):
        main()
    
    mock_list_currencies.assert_called_once()


def test_cli_invalid_currency_code():
    """Test CLI behavior with invalid currency code."""
    stdout = io.StringIO()
    with patch("sys.stdout", stdout):
        with patch.object(sys, "argv", ["simple-currency-converter", "invalid", "usd", "100"]):
            # We also need to patch parser.print_help to prevent actual output
            with patch("argparse.ArgumentParser.print_help"):
                main()
    
    output = stdout.getvalue()
    assert "Invalid currency code: invalid" in output 