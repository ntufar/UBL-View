# UBL X-Ray

**UBL X-Ray** (or "The Glass Invoice") is a visual tool designed to "explode" complex UBL 2.1 / PEPPOL BIS electronic invoices into an interactive Sunburst chart. It helps developers, business analysts, and QA testers understand the structure and data of e-invoices without reading raw XML code.

## 🚀 Live Demo

Check out the deployed application here: **[https://ubl-view.streamlit.app/](https://ubl-view.streamlit.app/)**

## ✨ Features

-   **Interactive Visualization**: Explore the invoice hierarchy using a zoomable Sunburst chart.
-   **Inspector Panel**: Click on any section to see the exact tag name, path, and value.
-   **Color-Coded Sections**:
    -   🔵 **Blue**: Party/Entity Information (Who)
    -   🟢 **Green**: Monetary Totals (How much)
    -   🟠 **Orange**: Line Items (What)
    -   ⚪ **Grey**: Metadata (ID, Date, Profile)
-   **Sample Data**: Includes pre-loaded examples (Simple Invoice, Credit Note, Correction).
-   **Privacy Focused**: Files are processed in memory and not saved to disk.

## 🛠️ Tech Stack

-   **Python**
-   **Streamlit** (Frontend & App Logic)
-   **Plotly** (Visualization)
-   **Pandas** (Data Handling)
-   **LXML/ElementTree** (XML Parsing)

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ntufar/UBL-View.git
    cd UBL-View
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## 👤 Author

**Nicolai Tufar**

---
*Built with ❤️ for the e-invoicing community.*
