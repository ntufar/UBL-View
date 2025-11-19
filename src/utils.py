import pandas as pd

# Color mapping based on PRD
# Blue: Party/Entity Information (Who)
# Green: Monetary Totals (How much)
# Orange: Line Items (What)
# Grey: Metadata (ID, Date, Profile)

COLOR_MAP = {
    "Supplier": "#636EFA", # Blue-ish
    "Customer": "#636EFA",
    "Party": "#636EFA",
    "AccountingSupplierParty": "#636EFA",
    "AccountingCustomerParty": "#636EFA",
    
    "MonetaryTotal": "#00CC96", # Green-ish
    "TaxTotal": "#00CC96",
    "LegalMonetaryTotal": "#00CC96",
    "TaxAmount": "#00CC96",
    "PayableAmount": "#00CC96",
    
    "InvoiceLine": "#EF553B", # Orange-ish
    "Item": "#EF553B",
    "Price": "#EF553B",
    
    "Metadata": "#B6E880", # Light Green/Grey
    "ID": "#B6E880",
    "IssueDate": "#B6E880",
    "InvoiceTypeCode": "#B6E880"
}

DEFAULT_COLOR = "#D3D3D3" # Grey

def get_color(tag_name):
    """Returns the color for a given tag name."""
    # Check for exact match
    if tag_name in COLOR_MAP:
        return COLOR_MAP[tag_name]
    
    # Check for partial match (e.g. "Party" in "AccountingSupplierParty")
    for key, color in COLOR_MAP.items():
        if key in tag_name:
            return color
            
    return DEFAULT_COLOR
