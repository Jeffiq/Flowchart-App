import streamlit as st
import graphviz
import pandas as pd

# Set up the Web App Page
st.set_page_config(page_title="Methodology Flowchart Builder", layout="wide")
st.title("🧬 Dynamic Methodology Flowchart Builder")
st.markdown("Build, color, and connect your methodology phases visually. Your graph will automatically scale to fit your screen.")

# --- INSTRUCTIONAL GUIDE ---
with st.expander("📖 How to Use This Tool (Click to Expand)", expanded=False):
    st.markdown("""
    **Welcome to the Dynamic Methodology Flowchart Builder!** Here is how to create your perfect diagram:
    
    1. **Template Controls:** Use the sidebar to clear all demo data and start fresh, or restore the default Plant Design template.
    2. **Global Settings (Left Sidebar):** Choose your main flow direction (Top-to-Bottom or Left-to-Right) and select the total number of Main Phases you need.
    3. **Phase Configuration:** For each phase, you can assign a custom color and title. 
    4. **Sub-Phases & Nodes:** Check the box to add Sub-Phases. A Node is a single step (a white box). A Sub-Phase groups multiple Nodes together. You can toggle how these nodes stack (Normal vs Perpendicular).
    5. **Relationships (Cross-Linking):** Scroll down to the table. This is where you connect the boxes. Click "Add Row", then use the dropdown menus to select the "Source" (where the arrow starts) and the "Target" (where the arrow points).
    6. **Generate & Download:** Click the blue **🚀 Generate Flowchart** button at the bottom. Once generated, use the download buttons to save it as a high-resolution PNG or PDF.
    """)

# --- SESSION STATE MANAGEMENT (For Clearing Data) ---
if 'use_blank_slate' not in st.session_state:
    st.session_state.use_blank_slate = False

# --- SIDEBAR: Global Settings ---
st.sidebar.header("1. Global Settings")
graph_direction = st.sidebar.selectbox("Main Flow Direction", ["TB (Top to Bottom)", "LR (Left to Right)"])
direction_code = "TB" if "TB" in graph_direction else "LR"

# CONDITIONAL DEFAULTS (Blank vs Plant Template)
if st.session_state.use_blank_slate:
    # BLANK SLATE
    num_phases = st.sidebar.number_input("How many Main Phases do you need?", min_value=1, max_value=15, value=1, key="np_blank")
    default_phases = {}
    default_subs = {}
    default_relationships = []
else:
    # PLANT DESIGN TEMPLATE
    num_phases = st.sidebar.number_input("How many Main Phases do you need?", min_value=1, max_value=15, value=6, key="np_plant")
    default_phases = {
        0: {"title": "Phase 1: Receiving Bay", "color": "#CFD8DC", "n_subs": 2},
        1: {"title": "Phase 2: Grading", "color": "#FFE082", "n_subs": 2},
        2: {"title": "Phase 3: Microbial Culturing", "color": "#C8E6C9", "n_subs": 2},
        3: {"title": "Phase 4: Primary Processing", "color": "#FFCCBC", "n_subs": 2},
        4: {"title": "Phase 5: Fermentation", "color": "#E1BEE7", "n_subs": 2},
        5: {"title": "Phase 6: Industrial Grade Ethanol", "color": "#BBDEFB", "n_subs": 2}
    }
    default_subs = {
        "0_0": {"title": "Unloading", "color": "#ECEFF1", "nodes": ["Truck Entry", "Bulk Unloading"]},
        "0_1": {"title": "Logistics", "color": "#E0E0E0", "nodes": ["Weighbridge", "Initial Storage"]},
        "1_0": {"title": "Sorting", "color": "#FFF8E1", "nodes": ["Size Separation", "Debris Removal"]},
        "1_1": {"title": "Quality Control", "color": "#FFECB3", "nodes": ["Sampling", "Moisture Check"]},
        "2_0": {"title": "Strain Prep", "color": "#E8F5E9", "nodes": ["Master Bank", "Working Bank"]},
        "2_1": {"title": "Inoculum", "color": "#C8E6C9", "nodes": ["Flask Culture", "Seed Bioreactor"]},
        "3_0": {"title": "Cleaning", "color": "#FBE9E7", "nodes": ["Washing", "Rinsing"]},
        "3_1": {"title": "Milling", "color": "#FFCCBC", "nodes": ["Crushing", "Slurry Prep"]},
        "4_0": {"title": "Pre-Fermentation", "color": "#F3E5F5", "nodes": ["Liquefaction", "Saccharification"]},
        "4_1": {"title": "Main Fermentation", "color": "#E1BEE7", "nodes": ["Yeast Addition", "Ethanol Production"]},
        "5_0": {"title": "Distillation", "color": "#E3F2FD", "nodes": ["Stripping Column", "Rectifying Column"]},
        "5_1": {"title": "Dehydration", "color": "#BBDEFB", "nodes": ["Molecular Sieves", "Final Storage"]},
    }
    default_relationships = [
        {"Source": "P1S1_1", "Target": "P1S1_2"}, {"Source": "P1S1_2", "Target": "P1S2_1"},
        {"Source": "P1S2_1", "Target": "P1S2_2"}, {"Source": "P1S2_2", "Target": "P2S1_1"},
        {"Source": "P2S1_1", "Target": "P2S1_2"}, {"Source": "P2S1_2", "Target": "P2S2_1"},
        {"Source": "P2S2_1", "Target": "P2S2_2"}, {"Source": "P2S2_2", "Target": "P4S1_1"},
        {"Source": "P4S1_1", "Target": "P4S1_2"}, {"Source": "P4S1_2", "Target": "P4S2_1"},
        {"Source": "P4S2_1", "Target": "P4S2_2"}, {"Source": "P4S2_2", "Target": "P5S1_1"},
        {"Source": "P5S1_1", "Target": "P5S1_2"}, {"Source": "P5S1_2", "Target": "P5S2_1"},
        {"Source": "P3S1_1", "Target": "P3S1_2"}, {"Source": "P3S1_2", "Target": "P3S2_1"},
        {"Source": "P3S2_1", "Target": "P3S2_2"}, {"Source": "P3S2_2", "Target": "P5S2_1"},
        {"Source": "P5S2_1", "Target": "P5S2_2"}, {"Source": "P5S2_2", "Target": "P6S1_1"},
        {"Source": "P6S1_1", "Target": "P6S1_2"}, {"Source": "P6S1_2", "Target": "P6S2_1"},
        {"Source": "P6S2_1", "Target": "P6S2_2"},
    ]

# --- SIDEBAR: Template Controls & Citation ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Template Controls")
st.sidebar.markdown("Start fresh or use the default plant design.")

# The Clear and Restore Buttons
colA, colB = st.sidebar.columns(2)
if colA.button("🗑️ Clear All"):
    st.session_state.use_blank_slate = True
    if 'df' in st.session_state:
        del st.session_state.df # Force Dataframe reset
    st.rerun()
    
if colB.button("🔄 Restore"):
    st.session_state.use_blank_slate = False
    if 'df' in st.session_state:
        del st.session_state.df # Force Dataframe reset
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📝 How to Cite")
st.sidebar.markdown("""
If you use this tool to generate flowcharts, please reference it as:
> **Metha, Jefferson.** *Dynamic Methodology Flowchart Builder.* Available at: [https://flowchart-by-jeff.streamlit.app/](https://flowchart-by-jeff.streamlit.app/)
""")

# --- MAIN AREA: Dynamic Phase & Node Creation ---
st.header("2. Phase & Sub-Phase Configuration")

phase_data = [] 
all_node_ids = []

for i in range(num_phases):
    p_def = default_phases.get(i, {"title": f"Phase {i+1}", "color": "#E1F5FE", "n_subs": 1})
    
    with st.expander(f"Phase {i+1}: {p_def.get('title', 'Configuration')}", expanded=False if (not st.session_state.use_blank_slate and i > 1) else True):
        col1, col2 = st.columns([3, 1])
        phase_title = col1.text_input(f"Title for Phase {i+1}", value=p_def["title"], help="Name this major section of your methodology.", key=f"title_{i}")
        phase_color = col2.color_picker(f"Color for Phase {i+1}", value=p_def["color"], key=f"color_{i}")
        
        has_subphases = st.checkbox(f"🗂️ Enable nested Sub-Phases inside {phase_title}?", value=True, key=f"hassub_{i}")
        
        if has_subphases:
            num_subs = st.number_input(f"How many Sub-Phases inside Phase {i+1}?", min_value=1, max_value=10, value=p_def["n_subs"], key=f"nsub_{i}")
            sub_phases_list = []
            
            for s in range(num_subs):
                s_def = default_subs.get(f"{i}_{s}", {"title": f"Sub-step {s+1}", "color": "#F8F9FA", "nodes": [f"Action 1"]})
                
                st.markdown(f"**↳ Sub-Phase {s+1}**")
                s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
                sub_title = s_col1.text_input(f"Title for Sub-Phase {s+1}", value=s_def["title"], key=f"subtitle_{i}_{s}")
                sub_color = s_col2.color_picker(f"Background Color", value=s_def["color"], key=f"subcolor_{i}_{s}")
                
                sub_layout = s_col3.selectbox("Sub-Phase Layout", ["Rank Same (Perpendicular)", "Normal (Parallel)"], help="Choose how the white boxes stack inside this sub-phase.", key=f"sublay_{i}_{s}")
                
                num_snodes = st.number_input(f"Nodes in Sub-Phase {s+1}?", min_value=1, max_value=10, value=len(s_def["nodes"]), key=f"nsnodes_{i}_{s}")
                snodes_in_this_sub = []
                
                for j in range(num_snodes):
                    n_col1, n_col2 = st.columns([1, 4])
                    node_id = f"P{i+1}S{s+1}_{j+1}"
                    def_text = s_def["nodes"][j] if j < len(s_def["nodes"]) else f"Action {j+1}"
                    
                    n_col1.text_input("Node ID (Auto)", value=node_id, disabled=True, key=f"dsid_{i}_{s}_{j}")
                    node_label = n_col2.text_input("Node Text", value=def_text, help="The actual text that appears in the flowchart box.", key=f"slbl_{i}_{s}_{j}")
                    
                    snodes_in_this_sub.append({"id": node_id, "label": node_label})
                    all_node_ids.append(node_id) 
                    
                sub_phases_list.append({
                    "title": sub_title,
                    "color": sub_color,
                    "layout": sub_layout,
                    "nodes": snodes_in_this_sub
                })
                
            phase_data.append({
                "title": phase_title,
                "color": phase_color,
                "is_sub": True,
                "sub_phases": sub_phases_list
            })
            
# --- RELATIONSHIPS (EDGES) ---
st.header("3. Define Relationships (Cross-Linking)")
st.markdown("Use the table below to link your nodes. **Click 'Add Row' at the bottom of the table** to create new connections. You can select the Source and Target directly from dropdown menus!")

# Initialize the Dataframe properly based on whether we are clearing or not
if 'df' not in st.session_state:
    if st.session_state.use_blank_slate:
        # Create an empty dataframe with the correct columns if Blank Slate
        st.session_state.df = pd.DataFrame(columns=["Source", "Target"])
    else:
        st.session_state.df = pd.DataFrame(default_relationships)

# THE FIX IS HERE: We render the editor and IMMEDIATELY save it back into session_state!
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    key="relationship_editor", # Adding a key helps Streamlit track it natively
    column_config={
        "Source": st.column_config.SelectboxColumn("From (Source Node)", help="Select starting node", width="medium", options=all_node_ids, required=True),
        "Target": st.column_config.SelectboxColumn("To (Target Node)", help="Select ending node", width="medium", options=all_node_ids, required=True),
    }
)

# 🚨 THE MAGIC LINE: Constantly save changes back to memory so they survive page updates 🚨
st.session_state.df = edited_df

# --- GRAPH GENERATION ---
st.header("4. Your Flowchart")

if st.button("🚀 Generate Flowchart", type="primary"):
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir=direction_code, dpi='300', fontname='Helvetica', splines='ortho', compound='true')
    dot.attr('node', shape='box', style='filled,rounded', fontname='Helvetica', fontsize='11', margin='0.2,0.1')
    
    for idx, phase in enumerate(phase_data):
        with dot.subgraph(name=f'cluster_phase_{idx}') as c:
            c.attr(style='filled,rounded', fillcolor=phase['color'], penwidth='2')
            c.attr(label=phase['title'], fontname='Helvetica-Bold', fontsize='14')
            
            if phase['is_sub']:
                for s_idx, sub in enumerate(phase['sub_phases']):
                    with c.subgraph(name=f'cluster_sub_{idx}_{s_idx}') as sub_c:
                        sub_c.attr(style='filled,rounded', fillcolor=sub['color'], penwidth='1', color='#6c757d')
                        sub_c.attr(label=sub['title'], fontname='Helvetica-Oblique', fontsize='11')
                        
                        node_ids = []
                        for node in sub['nodes']:
                            sub_c.node(node['id'], node['label'], fillcolor='#FFFFFF')
                            node_ids.append(node['id'])
                            
                        if "Rank Same" in sub['layout'] and len(node_ids) > 1:
                            rank_string = "{ rank=same; " + "; ".join(node_ids) + "; }"
                            sub_c.body.append(rank_string)
                            
    # Build Edges from the UI Table
    for index, row in edited_df.iterrows():
        src = str(row['Source'])
        dst = str(row['Target'])
        if src in all_node_ids and dst in all_node_ids and pd.notna(row['Source']) and pd.notna(row['Target']):
            dot.edge(src, dst)
            
    # Convert graph to high-res PNG bytes
    png_bytes = dot.pipe(format='png')
    pdf_bytes = dot.pipe(format='pdf')
    
    # Success Notification
    st.toast('Flowchart generated successfully!', icon='🎉')
    
    st.image(png_bytes, use_container_width=True)
    
    # --- DOWNLOAD BUTTONS ---
    st.markdown("### 📥 Download Your High-Resolution Flowchart")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(label="Download as PNG (Image)", data=png_bytes, file_name="methodology_flowchart.png", mime="image/png")
    with d_col2:
        st.download_button(label="Download as PDF (Best for Documents)", data=pdf_bytes, file_name="methodology_flowchart.pdf", mime="application/pdf")
