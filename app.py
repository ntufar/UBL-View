import streamlit as st
import plotly.graph_objects as go
import pandas as pd
# Tag descriptions are loaded in src.utils
import os
from src.parser import parse_ubl_xml
from src.utils import get_color

st.set_page_config(layout="wide", page_title="UBL View")

# --- Sidebar ---
st.sidebar.title("UBL View")
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
# Search and filter UI
search_query = st.sidebar.text_input("Search tags or values", "")
min_value = st.sidebar.slider("Minimum value", min_value=0, max_value=1000, value=0)

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
        # --- Filtering Logic ---
        filtered_df = df.copy()

        # Store in session state for later edits
        st.session_state.filtered_df = filtered_df

        # Apply search query filter
        if search_query:
            filtered_df = filtered_df[
                filtered_df['tag_name'].str.contains(search_query, case=False, na=False) |
                filtered_df['text_value'].str.contains(search_query, case=False, na=False)
            ]

        # Apply minimum value filter
        filtered_df = filtered_df[filtered_df['value'] >= min_value]
        # Update session state after filtering
        st.session_state.filtered_df = filtered_df
        # --- Visualization ---
        st.title("Invoice Structure")
        
        # Apply colors
        filtered_df["color"] = filtered_df["tag_name"].apply(get_color)
        
        fig = go.Figure(go.Sunburst(
            ids=filtered_df['id'],
            labels=filtered_df['label'],
            parents=filtered_df['parent'],
            values=filtered_df['value'],
            # branchvalues="total", # Removed to let Plotly calculate from leaves
            marker=dict(colors=filtered_df['color']),
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Path: %{customdata[1]}<extra></extra>',
            customdata=filtered_df[['tag_name', 'path', 'text_value']].values
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
                if "customdata" in point:
                    tag_name = point["customdata"][0]
                    path = point["customdata"][1]
                    value = point["customdata"][2]
                    st.markdown(f"**Tag:** `{tag_name}`")
                    st.markdown(f"**Path:** `{path}`")
                    # Show description from tag_descriptions
                    from src.utils import get_description
                    description = get_description(tag_name)
                    st.markdown(f"**Description:** {description}")
                    if value:
                        st.markdown(f"**Value:** {value}")
                        # Edit value UI
                        new_val = st.text_input("Edit value", value=str(value), key="edit_val")
                        if st.button("Update"):
                            # Ensure dataframe is stored in session state
                            if "filtered_df" not in st.session_state:
                                st.session_state.filtered_df = filtered_df
                            st.session_state.filtered_df.loc[st.session_state.filtered_df['id'] == point["customdata"][0], "text_value"] = new_val
                            st.experimental_rerun()
                    else:
                        st.info("This is a container node.")
                else:
                    st.info("Select a node to see details.")
            else:
                st.info("Click on a section of the chart to inspect it.")

        # --- Raw Data Inspector ---
        st.subheader("Raw Data")
        st.dataframe(filtered_df[["tag_name", "text_value", "path"]], width="stretch")

else:
    st.info("Please upload a file or select a sample.")
