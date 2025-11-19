import pytest
from src.utils import get_description

def test_get_description():
    # Test known tag
    desc = get_description("cbc:ID")
    assert desc == "Invoice identifier"
    
    # Test unknown tag
    desc_unknown = get_description("UnknownTag")
    assert desc_unknown == "No description available."
