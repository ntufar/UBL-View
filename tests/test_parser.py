import unittest
import os
import pandas as pd
from src.parser import parse_ubl_xml

class TestParser(unittest.TestCase):
    def test_parse_base_example(self):
        file_path = "docs/examples/base-example.xml"
        with open(file_path, "rb") as f:
            content = f.read()
            
        df, error = parse_ubl_xml(content)
        
        self.assertIsNone(error)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        
        # Check required columns
        required_columns = ['id', 'label', 'parent', 'value', 'tag_name', 'path', 'text_value']
        for col in required_columns:
            self.assertIn(col, df.columns)
            
        # Check root node
        root = df[df['id'] == 'Invoice']
        self.assertFalse(root.empty)
        self.assertEqual(root.iloc[0]['parent'], "")
        
    def test_parse_credit_note(self):
        file_path = "docs/examples/base-creditnote-correction.xml"
        with open(file_path, "rb") as f:
            content = f.read()
            
        df, error = parse_ubl_xml(content)
        self.assertIsNone(error)
        self.assertFalse(df.empty)

if __name__ == '__main__':
    unittest.main()
