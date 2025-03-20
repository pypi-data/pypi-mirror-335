import pytest
from simple_currency_converter.currency_codes import all_codes, common_codes, crypto_codes


def test_common_codes_exist():
    """Test that common currency codes exist and are in the expected format."""
    assert isinstance(common_codes, dict)
    assert len(common_codes) > 0
    
    # Check some common currencies
    assert "usd" in common_codes
    assert "eur" in common_codes
    assert "gbp" in common_codes
    assert "aud" in common_codes
    
    # Check the format of entries
    for code, name in common_codes.items():
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert code.islower()


def test_crypto_codes_exist():
    """Test that crypto currency codes exist and are in the expected format."""
    assert isinstance(crypto_codes, dict)
    assert len(crypto_codes) > 0
    
    # Check some crypto currencies
    assert "btc" in crypto_codes
    assert "eth" in crypto_codes
    
    # Check the format of entries
    for code, name in crypto_codes.items():
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert code.islower()


def test_all_codes_include_common_and_crypto():
    """Test that all_codes includes all common and crypto codes."""
    assert isinstance(all_codes, dict)
    assert len(all_codes) > len(common_codes) + len(crypto_codes)
    
    # All common codes should be in all_codes
    for code in common_codes:
        assert code in all_codes
    
    # All crypto codes should be in all_codes
    for code in crypto_codes:
        assert code in all_codes 