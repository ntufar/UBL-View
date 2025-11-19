import xml.etree.ElementTree as ET
import pandas as pd

def clean_tag(tag):
    """Removes the namespace from the tag name."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def parse_ubl_xml(xml_content):
    """
    Parses UBL XML content and returns a DataFrame suitable for Plotly Sunburst.
    
    Args:
        xml_content (bytes or str): The XML content to parse.
        
    Returns:
        pd.DataFrame: DataFrame with columns ['id', 'label', 'parent', 'value', 'tag_name', 'path']
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return None, f"Error parsing XML: {e}"

    nodes = []
    
    # Add root node
    root_id = "Invoice"
    root_label = "Invoice"
    nodes.append({
        "id": root_id,
        "label": root_label,
        "parent": "",
        "value": 0, # Let Plotly calculate based on children
        "tag_name": clean_tag(root.tag),
        "path": f"/{clean_tag(root.tag)}",
        "text_value": ""
    })

    def traverse(element, parent_id, path):
        # Group children by tag to handle lists (e.g. multiple InvoiceLine)
        children_counts = {}
        
        for child in element:
            tag = clean_tag(child.tag)
            children_counts[tag] = children_counts.get(tag, 0) + 1
            
            # Create a unique ID for this node
            # If there are multiple siblings with same tag, append index
            if children_counts[tag] > 1:
                node_id = f"{parent_id}/{tag}[{children_counts[tag]}]"
                label = f"{tag} ({children_counts[tag]})"
            else:
                node_id = f"{parent_id}/{tag}"
                label = tag
            
            current_path = f"{path}/{tag}"
            
            # Determine if leaf or branch
            # In UBL, leaves usually have text and no children (cbc elements)
            # Branches have children (cac elements)
            
            has_children = len(child) > 0
            text_value = child.text.strip() if child.text else ""
            
            # Calculate "value" for the chart
            # Leaves get a value of 1 (or based on content length?)
            # Branches sum up their children (Plotly does this automatically if we don't set value for branches)
            # But to be safe, let's set 1 for leaves.
            
            node_data = {
                "id": node_id,
                "label": label,
                "parent": parent_id,
                "tag_name": tag, # Keep original tag name (without namespace) for display
                "path": current_path,
                "text_value": text_value
            }
            
            if not has_children:
                node_data["value"] = 1
            else:
                node_data["value"] = 0 # Let Plotly calculate based on children
                
            nodes.append(node_data)
            
            if has_children:
                traverse(child, node_id, current_path)

    traverse(root, root_id, f"/{clean_tag(root.tag)}")
    
    return pd.DataFrame(nodes), None
