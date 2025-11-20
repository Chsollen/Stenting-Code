"""
Venous Stenting Visualization Tool
===================================
A neurosurgical tool for visualizing and annotating venous pressure measurements
on medical imaging. This application allows clinicians to:
- Upload medical images
- Annotate venous pressure measurements at specific anatomical locations
- Mark stenosis locations
- Generate annotated images and summary reports
- Export data to Excel for further analysis

Author: NeuroVERT Team
Version: 1.0
"""

import streamlit as st
from streamlit_plotly_events import plotly_events
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
import io
import matplotlib.pyplot as plt

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Venous Stenting Visualization Tool",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Venous Stenting Visualization Tool")

st.write("""
### Instructions
1. **Upload** a medical image (PNG, JPG, or JPEG)
2. **Click** on the image to mark annotation points
3. **Select** the anatomical location and enter pressure values
4. **Generate** annotated images and export data

This tool helps visualize venous pressure measurements for neurosurgical stenting procedures.
""")

# ============================================================================
# ANATOMICAL LOCATION DEFINITIONS
# ============================================================================

# Complete list of venous anatomical locations available for annotation
LOCATIONS = [
    "Select...",
    "Torcula",
    "Posterior superior sagittal sinus",
    "Mid superior sagittal sinus",
    "Medial transverse sinus",
    "Lateral transverse sinus",
    "Transverse-sigmoid junction",
    "Sigmoid sinus",
    "Jugular bulb",
    "Internal jugular vein",
    "Internal jugular vein origin",
    "Subclavian",
    "Superior Vena Cava",
    "Inferior Vena Cava",
    "Stenosis",
    "Pre-Stenosis",
    "Post-Stenosis"
]

# Locations that require left/right side specification
SIDE_REQUIRED = [
    "Medial transverse sinus",
    "Lateral transverse sinus",
    "Transverse-sigmoid junction",
    "Sigmoid sinus",
    "Jugular bulb",
    "Internal jugular vein",
    "Internal jugular vein origin",
    "Subclavian"
]

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Initialize session state variables for maintaining app state across reruns
if "annotations" not in st.session_state:
    # Stores all annotations: {id, x, y, location, value, (side)}
    st.session_state.annotations = []

if "next_id" not in st.session_state:
    # Counter for assigning unique IDs to annotations
    st.session_state.next_id = 1

if "clicked_points" not in st.session_state:
    # Stores clicked coordinates: {x, y}
    st.session_state.clicked_points = []

if "rotation_angle" not in st.session_state:
    # Current rotation angle of the image (0, 90, 180, or 270)
    st.session_state.rotation_angle = 0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_clicked_point(new_point):
    """
    Add a new clicked point to the session state if not already present.
    
    Uses a tolerance of 5 pixels to prevent duplicate points from being added
    when the user clicks near an existing point.
    
    Args:
        new_point (dict): Dictionary with 'x' and 'y' coordinates
    """
    tolerance = 5
    for p in st.session_state.clicked_points:
        if abs(p["x"] - new_point["x"]) < tolerance and abs(p["y"] - new_point["y"]) < tolerance:
            return
    st.session_state.clicked_points.append(new_point)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Step 1: Image Upload
uploaded_file = st.file_uploader("📁 Choose a medical image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load the uploaded image
    image = Image.open(uploaded_file)
    
    # Step 2: Image Rotation Control
    # Allow users to rotate the image in 90-degree increments for proper orientation
    if st.button("🔄 Rotate Image 90°"):
        st.session_state.rotation_angle = (st.session_state.rotation_angle + 90) % 360
    
    # Apply rotation transformation
    rotated_image = image.rotate(st.session_state.rotation_angle, expand=True)
    
    # Step 3: Image Resizing for Display
    # Resize to fixed width (600px) to ensure consistent display and reduce scrolling
    display_width = 600
    display_ratio = display_width / rotated_image.width
    display_height = int(rotated_image.height * display_ratio)
    resized_image = rotated_image.resize((display_width, display_height))
    
    # Convert PIL image to numpy array for Plotly visualization
    img_array = np.array(resized_image)
    
    # Step 4: Create Interactive Plotly Figure
    # Display image with click event capture for annotation placement
    fig = px.imshow(img_array)
    fig.update_yaxes(autorange='reversed')  # Match PIL coordinate system
    fig.update_layout(clickmode='event+select')
    
    # Display existing clicked points as red markers on the image
    if st.session_state.clicked_points:
        fig.add_scatter(
            x=[pt["x"] for pt in st.session_state.clicked_points],
            y=[pt["y"] for pt in st.session_state.clicked_points],
            mode="markers",
            marker=dict(size=12, color="red"),
            name="Clicked Points"
        )
    
    # Capture new click events from user interaction
    new_clicked = plotly_events(fig, click_event=True, override_height=display_height, override_width=display_width)
    if new_clicked:
        for pt in new_clicked:
            add_clicked_point({"x": pt.get("x"), "y": pt.get("y")})
    
    # Refresh the figure to show all clicked points (including newly added ones)
    fig.data = []  # Clear previous traces
    fig = px.imshow(img_array)
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(clickmode='event+select')
    if st.session_state.clicked_points:
        fig.add_scatter(
            x=[pt["x"] for pt in st.session_state.clicked_points],
            y=[pt["y"] for pt in st.session_state.clicked_points],
            mode="markers",
            marker=dict(size=12, color="red"),
            name="Clicked Points"
        )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    st.write("### 📝 Annotation Details")
    st.write("Fill out the forms below for each point you clicked on the image.")
    
    # Step 5: Annotation Form Generation
    # For each clicked point that hasn't been annotated, display a form
    tolerance = 5
    for pt in st.session_state.clicked_points:
        already_annotated = any(
            abs(ann["x"] - pt["x"]) < tolerance and abs(ann["y"] - pt["y"]) < tolerance 
            for ann in st.session_state.annotations
        )
        if not already_annotated:
            with st.expander(f"Add Annotation at (x={pt['x']:.0f}, y={pt['y']:.0f})"):
                # Select anatomical location from dropdown
                location = st.selectbox("Select location:", LOCATIONS, key=f"loc_{pt['x']}_{pt['y']}")
                
                # For bilateral structures, require left/right side selection
                side = "Select..."
                if location in SIDE_REQUIRED:
                    side = st.selectbox("Select side:", ["Select...", "Left", "Right"], key=f"side_{pt['x']}_{pt['y']}")
                
                # Handle different annotation types
                if location != "Select...":
                    if location == "Stenosis":
                        # Stenosis is marked with an "X" instead of a pressure value
                        annotation_value = "X"
                    else:
                        # For all other locations, collect pressure measurement in mmHg
                        annotation_value = st.text_input("Enter pressure value (mmHg):", key=f"val_{pt['x']}_{pt['y']}")
                else:
                    annotation_value = ""
                
                # Save button with validation
                if location != "Select..." and st.button("💾 Save Annotation", key=f"save_{pt['x']}_{pt['y']}"):
                    # Validate that bilateral structures have a side selected
                    if location in SIDE_REQUIRED and side == "Select...":
                        st.error("⚠️ Please select a side (Left or Right) for this location.")
                    else:
                        # Create annotation object
                        annotation = {
                            "id": st.session_state.next_id,
                            "x": pt["x"],
                            "y": pt["y"],
                            "location": location,
                            "value": annotation_value
                        }
                        # Add side information if applicable
                        if location in SIDE_REQUIRED:
                            annotation["side"] = side
                        
                        # Save to session state
                        st.session_state.annotations.append(annotation)
                        st.session_state.next_id += 1
                        st.success(f"✅ Annotation {annotation['id']} added successfully!")
    
    # ========================================================================
    # SIDEBAR: Annotation Management
    # ========================================================================
    st.sidebar.title("📋 Current Annotations")
    st.sidebar.write(f"Total: {len(st.session_state.annotations)}")
    
    if st.session_state.annotations:
        st.sidebar.write("---")
        for ann in st.session_state.annotations.copy():
            # Display annotation with side information if applicable
            extra = f" - {ann['side']}" if "side" in ann else ""
            st.sidebar.write(f"**ID {ann['id']}:** {ann['location']}{extra}")
            st.sidebar.write(f"Value: {ann['value']} mmHg" if ann['value'] != "X" else "Stenosis marked")
            
            # Delete button for each annotation
            if st.sidebar.button("🗑️ Delete", key=f"delete_{ann['id']}"):
                st.session_state.annotations = [a for a in st.session_state.annotations if a["id"] != ann["id"]]
                st.sidebar.success(f"Annotation {ann['id']} deleted!")
            st.sidebar.write("---")
    else:
        st.sidebar.info("No annotations yet. Click on the image to start.")
    
    # ========================================================================
    # Step 6: Generate Annotated Images and Export Data
    # ========================================================================
    st.write("---")
    st.write("### 📊 Generate Output")
    
    if st.button("🎨 Generate and Save Annotated Image", type="primary"):
        # ====================================================================
        # LEFT IMAGE: Original with Colored Markers
        # ====================================================================
        # Create a copy of the original image and draw markers
        # Green = annotated points, Red = unannotated points
        left_image = resized_image.copy()
        draw_left = ImageDraw.Draw(left_image)
        r = 6  # Marker radius in pixels
        tolerance = 5  # Pixel tolerance for matching points
        
        for pt in st.session_state.clicked_points:
            # Check if this point has been annotated
            annotated = any(
                abs(ann["x"] - pt["x"]) < tolerance and abs(ann["y"] - pt["y"]) < tolerance
                for ann in st.session_state.annotations
            )
            color = "green" if annotated else "red"
            # Draw circular marker
            draw_left.ellipse(
                [(pt["x"] - r, pt["y"] - r), (pt["x"] + r, pt["y"] + r)],
                fill=color,
                outline=color
            )
        
        # ====================================================================
        # RIGHT IMAGE: Annotated with Pressure Values
        # ====================================================================
        # Create a copy for the annotated version with text overlays
        right_image = resized_image.copy()
        draw_right = ImageDraw.Draw(right_image)
        
        # Load font with fallback options for cross-platform compatibility
        try:
            base_font = ImageFont.truetype("arialbd.ttf", 40)  # Windows
        except Exception:
            try:
                base_font = ImageFont.truetype("arial.ttf", 40)  # Windows fallback
            except Exception:
                try:
                    base_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)  # Linux
                except Exception:
                    st.warning("⚠️ Custom font not available. Using default font (text may be smaller).")
                    base_font = ImageFont.load_default()

        # Draw each annotation on the image
        for ann in st.session_state.annotations:
            if ann["location"] == "Stenosis":
                # Stenosis: Display red "X" marker
                text = "X"
                try:
                    font = ImageFont.truetype("arialbd.ttf", 40)
                except Exception:
                    try:
                        font = ImageFont.truetype("arial.ttf", 40)
                    except Exception:
                        try:
                            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
                        except Exception:
                            font = ImageFont.load_default()
                fill_color = "red"
            else:
                # Pressure measurements: Display white text with black outline
                text = ann["value"]
                font = base_font
                fill_color = "#FFFFFF"
            
            # Calculate text position to center it on the annotation point
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = ann["x"] - text_width / 2
            y = ann["y"] - text_height / 2
            
            # Draw text with stroke for better visibility
            draw_right.text(
                (x, y),
                text,
                fill=fill_color,
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )

        # ====================================================================
        # Display Generated Images Side-by-Side
        # ====================================================================
        col1, col2 = st.columns(2)
        with col1:
            st.image(left_image, caption="Original Image (with markers)", use_container_width=True)
        with col2:
            st.image(right_image, caption="Annotated Image (with pressure values)", use_container_width=True)
        
        # ====================================================================
        # Prepare Annotated Image for Download
        # ====================================================================
        buf_img = io.BytesIO()
        right_image.save(buf_img, format="PNG")
        annotated_image_bytes = buf_img.getvalue()
        
        # ====================================================================
        # Generate Summary Table (Pressure Measurements Only)
        # ====================================================================
        df_full = pd.DataFrame(st.session_state.annotations)
        if not df_full.empty:
            # Exclude stenosis markers from the pressure summary table
            df_summary = df_full[~df_full["location"].isin(["Stenosis"])].copy()
            
            # Handle side information
            if "side" in df_summary.columns:
                df_summary["side"] = df_summary["side"].fillna("")
            
            # Combine side and location for bilateral structures
            df_summary["location"] = df_summary.apply(
                lambda row: f"{row['side']} {row['location']}".strip() 
                    if row.get("side", "") and row["side"] != "Select..." 
                    else row["location"],
                axis=1
            )
            df_summary = df_summary[["location", "value"]]
        else:
            df_summary = pd.DataFrame(columns=["location", "value"])
        
        # ====================================================================
        # Create PNG Table Image
        # ====================================================================
        fig_table, ax = plt.subplots(figsize=(6, len(df_summary) * 0.5 + 1))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(
            cellText=df_summary.values,
            colLabels=["Location", "Pressure (mmHg)"],
            loc='center'
        )
        # Format table cells
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                # Header row: bold and centered
                cell.set_text_props(weight='bold', ha='center')
            else:
                if j == 0:
                    # Location column: left-aligned
                    cell.set_text_props(ha='left')
                elif j == 1:
                    # Pressure column: right-aligned
                    cell.set_text_props(ha='right')
        plt.tight_layout()
        buf_table = io.BytesIO()
        plt.savefig(buf_table, format="PNG")
        buf_table.seek(0)
        table_png = buf_table.getvalue()
        
        # ====================================================================
        # Create Excel File for Data Export
        # ====================================================================
        excel_buffer = io.BytesIO()
        df_summary.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # ====================================================================
        # Download Buttons
        # ====================================================================
        st.write("---")
        st.write("### 📥 Download Files")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📷 Download Annotated Image", 
                data=annotated_image_bytes,
                file_name="annotated_venous_image.png", 
                mime="image/png",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📊 Download Summary Table (PNG)", 
                data=table_png,
                file_name="pressure_summary_table.png", 
                mime="image/png",
                use_container_width=True
            )
        with col3:
            st.download_button(
                "📑 Download Excel File", 
                data=excel_buffer,
                file_name="venous_pressure_data.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
