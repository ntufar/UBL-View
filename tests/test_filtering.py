import pytest
import pandas as pd
from src.parser import parse_ubl_xml

def test_filter_dataframe():
    # Create a dummy dataframe similar to what parser returns
    data = {
        "tag_name": ["Invoice", "ID", "TaxTotal", "TaxAmount"],
        "text_value": ["", "INV-123", "", "100.00"],
        "value": [0, 1, 0, 100.0],
        "path": ["/Invoice", "/Invoice/ID", "/Invoice/TaxTotal", "/Invoice/TaxTotal/TaxAmount"],
        "id": ["Invoice", "Invoice/ID", "Invoice/TaxTotal", "Invoice/TaxTotal/TaxAmount"],
        "label": ["Invoice", "ID", "TaxTotal", "TaxAmount"],
        "parent": ["", "Invoice", "Invoice", "Invoice/TaxTotal"]
    }
    df = pd.DataFrame(data)
    
    # Test Search Filter
    search_query = "Tax"
    filtered_df = df[
        df['tag_name'].str.contains(search_query, case=False, na=False) |
        df['text_value'].str.contains(search_query, case=False, na=False)
    ]
    assert len(filtered_df) == 2 # TaxTotal and TaxAmount
    assert "TaxTotal" in filtered_df['tag_name'].values
    
    # Test Value Filter
    min_value = 50
    filtered_df_val = df[df['value'] >= min_value]
    assert len(filtered_df_val) == 1
    assert "TaxAmount" in filtered_df_val['tag_name'].values
