# Product Requirements Document (PRD)
**Project Name:** UBL X-Ray (or "The Glass Invoice")
**Version:** 1.0
**Status:** Draft

---

## 1. Problem Statement
**The Pain:** Electronic invoices (based on UBL 2.1 or PEPPOL BIS) are complex XML files containing hundreds of nested tags (`cac:Party`, `cbc:TaxAmount`, etc.). For developers and business analysts, reading raw XML is painful, and understanding the relationship between fields is difficult.
**The Opportunity:** A visual tool that "explodes" an invoice into its component parts, allowing users to understand the structure without reading code.
**The Solution:** An interactive "Sunburst" or "Tree" visualization that maps the hierarchy of a standard e-invoice, allowing users to zoom into specific data blocks (like "Buyer Details" or "Tax Breakdown").

---

## 2. Target Audience
1.  **Integration Developers:** Need to map their ERP data to the XML standard.
2.  **Business Analysts:** Need to check if an invoice file contains the correct business data (e.g., "Is the PO Number in the right tag?").
3.  **QA/Testers:** Need to visually verify generated invoices.

---

## 3. User Stories
| ID | As a... | I want to... | So that... |
| :--- | :--- | :--- | :--- |
| **3.1** | User | Upload a raw `.xml` invoice file | I can visualize my own specific data. |
| **3.2** | User | See a high-level "Sunburst" chart | I can instantly see the weight/complexity of different sections (Header vs. Lines vs. Tax). |
| **3.3** | User | Click on a section (e.g., "AccountingSupplierParty") | The view zooms in to show me the child fields (Name, Address, VAT ID). |
| **3.4** | User | Hover over a specific field | I see the actual value from the file (e.g., "100.00 EUR") and the technical tag name (`cbc:TaxAmount`). |
| **3.5** | User | Toggle between "Visual" and "Raw Code" | I can correlate the visual shape with the actual code line. |

---

## 4. Functional Requirements

### 4.1 The Input Mechanism
* **File Upload:** Accept `.xml` files.
* **Sample Data:** Provide 3 pre-loaded buttons: "Simple Invoice," "Complex Invoice (Credit Note)," "Corrective Invoice."

### 4.2 The Visualization (The Core)
* **Chart Type:** **Interactive Sunburst Chart**.
    * **Center:** The Root (`Invoice`).
    * **Ring 1 (Major Categories):** `Supplier`, `Customer`, `PaymentMeans`, `TaxTotal`, `InvoiceLines`.
    * **Ring 2 (Sub-Categories):** `PostalAddress`, `Contact`, `Item`.
    * **Ring 3 (Leaves):** The actual data fields (`StreetName`, `CityName`).
* **Color Coding:**
    * **Blue:** Party/Entity Information (Who).
    * **Green:** Monetary Totals (How much).
    * **Orange:** Line Items (What).
    * **Grey:** Metadata (ID, Date, Profile).

### 4.3 The "Inspector" Panel
* When a node is clicked, a sidebar displays:
    * **Tag Name:** `cac:PostalAddress`
    * **Path:** `/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress`
    * **Value:** "123 Main St"
    * **Description:** (Bonus) A brief description of what this field is for (pulled from a static dictionary).

---

## 5. Technical Approach & Stack

This project is unique because the "Data" isn't a CSV; it's a hierarchical tree parsed from a file.

### 5.1 The Stack
* **Language:** Python.
* **Backend/Parsing:** `lxml` or `xml.etree.ElementTree` (to parse the XML).
* **Frontend:** **Streamlit** (easiest) or **React + D3.js** (if you want to be fancy).
* **Visualization:** **Plotly** (`plotly.graph_objects.Sunburst`). Plotly handles hierarchical data (Parent/Label/Value) natively.

### 5.2 Data Processing Logic (The "Hard" Part)
You cannot just feed XML to a chart. You must write a recursive function to flatten the tree.

**The Algorithm:**
1.  Read XML root.
2.  Create a list of nodes: `[Parent, Label, ID, Value]`.
3.  Recursively walk through every tag.
    * If tag has children -> It's a "Branch" (Inner Ring).
    * If tag has text -> It's a "Leaf" (Outer Ring).
4.  Handle Namespaces! UBL uses `cac:` (Common Aggregate Components) and `cbc:` (Common Basic Components). You need to strip these or handle them gracefully so the chart looks clean.

---

## 6. Proposed UI Wireframe



* **Left Sidebar:** File Uploader & "Load Sample" buttons.
* **Main Center:** Huge, colorful Sunburst chart.
* **Bottom Section:** "Raw Data Inspector." A Dataframe view of the flattened nodes (Tag, Value, Parent) for searchability.

---

## 7. Project Name Ideas
* **UBL X-Ray**
* **Invoice Anatomizer**
* **OpenInvoice Lens**
* **XML Explorer: UBL Edition**

---

## 8. Getting Started
To make this work, you need a valid UBL XML file.

**Would you like me to:**
1.  Generate a **valid, dummy UBL 2.1 XML invoice** so you have a file to test with?
2.  Write the **Python function to recursively parse XML** into the format Plotly needs (this is the trickiest code part)?