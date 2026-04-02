import streamlit as st
import graphviz

# Set up the Web App Page
st.set_page_config(page_title="PhD Flowchart Builder", layout="wide")
st.title("🧬 Dynamic Methodology Flowchart Builder")
st.markdown("Build, color, and connect your methodology phases visually. Your graph will generate at the bottom.")

# --- SIDEBAR: Global Settings ---
st.sidebar.header("1. Global Settings")
graph_direction = st.sidebar.selectbox("Flow Direction", ["TB (Top to Bottom)", "LR (Left to Right)"])
direction_code = "TB" if "TB" in graph_direction else "LR"

num_phases = st.sidebar.number_input("How many Phases do you need?", min_value=1, max_value=10, value=5)

# --- MAIN AREA: Dynamic Phase & Node Creation ---
st.header("2. Phase & Node Configuration")

phase_data = [] 

for i in range(num_phases):
    with st.expander(f"Phase {i+1} Configuration", expanded=True):
        col1, col2 = st.columns([3, 1])
        
        phase_title = col1.text_input(f"Title for Phase {i+1}", value=f"Phase {i+1} Title", key=f"title_{i}")
        phase_color = col2.color_picker(f"Color for Phase {i+1}", value="#E1F5FE", key=f"color_{i}")
        
        num_nodes = st.number_input(f"How many nodes in Phase {i+1}?", min_value=1, max_value=20, value=3, key=f"nnodes_{i}")
        
        nodes_in_this_phase = []
        
        st.markdown("**Node Details:**")
        for j in range(num_nodes):
            n_col1, n_col2 = st.columns([1, 4])
            node_id = n_col1.text_input("Node ID (e.g., A)", value=f"P{i+1}_{j+1}", key=f"id_{i}_{j}")
            node_label = n_col2.text_input("Node Text", value=f"Description for node {node_id}", key=f"lbl_{i}_{j}")
            nodes_in_this_phase.append({"id": node_id, "label": node_label})
            
        phase_data.append({
            "title": phase_title,
            "color": phase_color,
            "nodes": nodes_in_this_phase
        })

# --- RELATIONSHIPS (EDGES) ---
st.header("3. Define Relationships")
st.markdown("Type the connections between your nodes here. Use the format **Source_ID -> Target_ID**. Put one connection per line.")

default_edges = "P1_1 -> P1_2\nP1_2 -> P2_1\nP2_1 -> P3_1"
edges_input = st.text_area("Connections:", value=default_edges, height=150)

# --- GRAPH GENERATION ---
st.header("4. Your Flowchart")

if st.button("🚀 Generate Flowchart", type="primary"):
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir=direction_code, dpi='300', fontname='Helvetica', splines='ortho')
    dot.attr('node', shape='box', style='filled,rounded', fontname='Helvetica', fontsize='11', margin='0.2,0.1')
    
    for idx, phase in enumerate(phase_data):
        with dot.subgraph(name=f'cluster_phase_{idx}') as c:
            c.attr(style='filled', fillcolor=phase['color'], penwidth='2')
            c.attr(label=phase['title'], fontname='Helvetica-Bold', fontsize='12')
            
            for node in phase['nodes']:
                c.node(node['id'], node['label'], fillcolor='#FFFFFF')
                
    for line in edges_input.split('\n'):
        if '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                src = parts[0].strip()
                dst = parts[1].strip()
                dot.edge(src, dst)
                
    st.graphviz_chart(dot)
