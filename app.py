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
# --- Main Logic ---

# Initialize session state for data if not present
if "xml_content" not in st.session_state:
    st.session_state.xml_content = None
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = None

# Handle File Upload
if uploaded_file:
    # Update state if a new file is uploaded
    # We use the file name to detect if it's a new file to avoid re-reading unnecessarily, 
    # but for simplicity, we can just read it.
    content = uploaded_file.read()
    st.session_state.xml_content = content
    st.session_state.current_file_name = uploaded_file.name

# Handle Sample Selection
elif selected_sample:
    try:
        with open(selected_sample, "rb") as f:
            st.session_state.xml_content = f.read()
        st.session_state.current_file_name = os.path.basename(selected_sample)
    except FileNotFoundError:
        st.error(f"Sample file not found: {selected_sample}")

# Process Data from Session State
if st.session_state.xml_content:
    df, error = parse_ubl_xml(st.session_state.xml_content)
    
    if error:
        st.error(error)
    else:
        # --- Filtering Logic ---
        
        # 1. Identify matching nodes based on search and min_value
        matches = df.copy()
        
        if search_query:
            matches = matches[
                matches['tag_name'].str.contains(search_query, case=False, na=False) |
                matches['text_value'].str.contains(search_query, case=False, na=False)
            ]
            
        if min_value > 0:
             matches = matches[matches['value'] >= min_value]

        # 2. Hierarchy-Aware Filtering: Keep ancestors of matches
        if search_query or min_value > 0:
            ids_to_keep = set(matches['id'])
            parent_map = df.set_index('id')['parent'].to_dict()
            
            for node_id in matches['id']:
                current = node_id
                while current and current in parent_map:
                    parent = parent_map[current]
                    if parent:
                        ids_to_keep.add(parent)
                    current = parent
            
            filtered_df = df[df['id'].isin(ids_to_keep)].copy()
        else:
            filtered_df = df.copy()

        # Store in session state
        st.session_state.filtered_df = filtered_df

        # --- Visualization ---
        st.title(f"Invoice Structure: {st.session_state.current_file_name or 'Unknown'}")
        
        # View Mode Toggle
        view_mode = st.radio("View Mode", ["Sunburst Chart", "Tree View"], horizontal=True)

        # Apply colors
        filtered_df["color"] = filtered_df["tag_name"].apply(get_color)
        
        if view_mode == "Sunburst Chart":
            fig = go.Figure(go.Sunburst(
                ids=filtered_df['id'],
                labels=filtered_df['label'],
                parents=filtered_df['parent'],
                values=filtered_df['value'],
                marker=dict(colors=filtered_df['color']),
                hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Path: %{customdata[1]}<extra></extra>',
                customdata=filtered_df[['id', 'path', 'text_value']].values 
            ))
            
            fig.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),
                height=700
            )
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selection = st.plotly_chart(fig, width="stretch", on_select="rerun")
                
            with col2:
                st.subheader("Inspector")
                
                selected_points = selection.get("selection", {}).get("points", [])

                if selected_points:
                    point = selected_points[0]
                    if "customdata" in point:
                        node_id = point["customdata"][0]
                        
                        # Look up the full row in the dataframe to get attributes
                        row = filtered_df[filtered_df['id'] == node_id].iloc[0]
                        
                        tag_name = row['tag_name']
                        path = row['path']
                        value = row['text_value']
                        attributes = row['attributes']
                        original_element = row.get('original_element')
                        
                        st.markdown(f"**Tag:** `{tag_name}`")
                        st.markdown(f"**Path:** `{path}`")
                        
                        # Attributes
                        if attributes:
                            st.markdown("**Attributes:**")
                            st.json(attributes)
                        
                        # Description
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
                                st.session_state.filtered_df.loc[st.session_state.filtered_df['id'] == node_id, "text_value"] = new_val
                                st.rerun()
                        else:
                            # Show XML snippet for container nodes
                            if original_element is not None:
                                import xml.etree.ElementTree as ET
                                # Indent for pretty printing (simple approach)
                                xml_str = ET.tostring(original_element, encoding='unicode')
                                st.markdown("**XML Snippet:**")
                                st.code(xml_str, language='xml')
                            else:
                                st.info("This is a container node.")
                    else:
                        st.info("Select a node to see details.")
                else:
                    st.info("Click on a section of the chart to inspect it.")

        elif view_mode == "Tree View":
            st.markdown("### Hierarchical View")
            
            # Helper to build tree
            def build_tree_structure(dataframe):
                nodes = {}
                for _, row in dataframe.iterrows():
                    nodes[row['id']] = {**row.to_dict(), 'children': []}
                
                roots = []
                for _, row in dataframe.iterrows():
                    if not row['parent'] or row['parent'] not in nodes:
                        roots.append(nodes[row['id']])
                    else:
                        nodes[row['parent']]['children'].append(nodes[row['id']])
                return roots

            # Helper to generate HTML tree
            def generate_tree_html(node, level=0):
                # Styling
                margin_left = 20
                color = get_color(node['tag_name'])
                
                label_text = f"<span style='color:{color}; font-weight:bold;'>{node['tag_name']}</span>"
                if node['text_value']:
                    label_text += f": {node['text_value']}"
                
                if node['attributes']:
                    attrs = ", ".join([f"{k}={v}" for k, v in node['attributes'].items()])
                    label_text += f" <span style='color:grey; font-size:0.9em;'>({attrs})</span>"

                html = ""
                if node['children']:
                    html += f"""
                    <details style='margin-left: {margin_left if level > 0 else 0}px; margin-bottom: 5px;'>
                        <summary style='cursor: pointer; list-style: none;'>{label_text}</summary>
                        <div style='border-left: 1px solid #ddd; padding-left: 10px;'>
                    """
                    for child in node['children']:
                        html += generate_tree_html(child, level + 1)
                    html += "</div></details>"
                else:
                    html += f"<div style='margin-left: {margin_left if level > 0 else 0}px; padding: 2px 0;'>{label_text}</div>"
                
                return html

            roots = build_tree_structure(filtered_df)
            
            full_html = "<div style='font-family: monospace;'>"
            for root in roots:
                full_html += generate_tree_html(root)
            full_html += "</div>"
            
            st.markdown(full_html, unsafe_allow_html=True)

        # --- Raw Data Inspector ---
        st.subheader("Raw Data")
        st.dataframe(filtered_df[["tag_name", "text_value", "path", "attributes"]], width="stretch")

else:
    st.info("Please upload a file or select a sample.")
