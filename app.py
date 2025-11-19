import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from src.parser import parse_ubl_xml
from src.utils import get_color

st.set_page_config(layout="wide", page_title="UBL X-Ray")

# --- Sidebar ---
st.sidebar.title("UBL X-Ray")
st.sidebar.markdown("Upload a UBL XML invoice to visualize its structure.")

uploaded_file = st.sidebar.file_uploader("Upload XML", type=["xml"])

# Sample Data Buttons
st.sidebar.subheader("Or load a sample:")
sample_dir = "docs/examples"
sample_files = {
    "Simple Invoice": "base-example.xml",
    "Credit Note": "base-creditnote-correction.xml",
    "Correction": "base-negative-inv-correction.xml"
}

selected_sample = None
for label, filename in sample_files.items():
    if st.sidebar.button(label):
        selected_sample = os.path.join(sample_dir, filename)

# --- Main Logic ---
xml_content = None
if uploaded_file:
    xml_content = uploaded_file.read()
elif selected_sample:
    try:
        with open(selected_sample, "rb") as f:
            xml_content = f.read()
    except FileNotFoundError:
        st.error(f"Sample file not found: {selected_sample}")

if xml_content:
    df, error = parse_ubl_xml(xml_content)
    
    if error:
        st.error(error)
    else:
        # --- Visualization ---
        st.title("Invoice Structure")
        
        # Apply colors
        df["color"] = df["tag_name"].apply(get_color)
        
        fig = go.Figure(go.Sunburst(
            ids=df['id'],
            labels=df['label'],
            parents=df['parent'],
            values=df['value'],
            # branchvalues="total", # Removed to let Plotly calculate from leaves
            marker=dict(colors=df['color']),
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Path: %{customdata[1]}<extra></extra>',
            customdata=df[['tag_name', 'path', 'text_value']].values
        ))
        
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            height=700
        )
        
        # Layout: Chart on Left, Inspector on Right
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Use on_select to capture clicks (requires Streamlit 1.35+)
            # For now, we'll rely on hover and maybe a selection event if available
            # Or just show the chart and a data table below
            selection = st.plotly_chart(fig, width="stretch", on_select="rerun")
            
        with col2:
            st.subheader("Inspector")
            
            selected_points = selection.get("selection", {}).get("points", [])
            
            if selected_points:
                point = selected_points[0]
                # Plotly selection data structure can be complex
                # We need to map it back to our dataframe or extract info
                # point_number might correspond to index in df if sorted? 
                # Actually, point object usually contains customdata if passed.
                
                # Let's try to find the node in DF based on label/id if possible
                # Or use customdata from the point
                
                if "customdata" in point:
                    tag_name = point["customdata"][0]
                    path = point["customdata"][1]
                    value = point["customdata"][2]
                    
                    st.markdown(f"**Tag:** `{tag_name}`")
                    st.markdown(f"**Path:** `{path}`")
                    if value:
                        st.markdown(f"**Value:** {value}")
                    else:
                        st.info("This is a container node.")
                else:
                    st.info("Select a node to see details.")
            else:
                st.info("Click on a section of the chart to inspect it.")

        # --- Raw Data Inspector ---
        st.subheader("Raw Data")
        st.dataframe(df[["tag_name", "text_value", "path"]], width="stretch")

else:
    st.info("Please upload a file or select a sample.")
