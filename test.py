import streamlit as st
from streamlit_plotly_events import plotly_events  # pip install streamlit-plotly-events
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
import io
import matplotlib.pyplot as plt

st.title("Venous Pressure Annotation App (Without st_canvas)")

st.write("""
Upload an image, then click on the image to add annotation points.  
Each click is recorded and you can add annotation details (location and pressure) via the forms below.
""")

# Venous locations list, including "Occlusion"
LOCATIONS = [
    "Select...",
    "Torcula",
    "Posterior superior sagittal sinus",
    "Mid superior sagittal sinus",
    "Right medial transverse sinus",
    "Right lateral transverse sinus",
    "Right transverse-sigmoid junction",
    "Right sigmoid sinus",
    "Right jugular bulb",
    "Right internal jugular vein",
    "Occlusion"
]

# Initialize session state for annotations, clicked points, and next annotation ID
if "annotations" not in st.session_state:
    st.session_state.annotations = []  # Each is a dict: {id, x, y, location, value}
if "next_id" not in st.session_state:
    st.session_state.next_id = 1
if "clicked_points" not in st.session_state:
    st.session_state.clicked_points = []  # Each is a dict: {x, y}

def add_clicked_point(new_point):
    """Add a new clicked point if not already present (within a 5-pixel tolerance)."""
    tolerance = 5
    for p in st.session_state.clicked_points:
        if abs(p["x"] - new_point["x"]) < tolerance and abs(p["y"] - new_point["y"]) < tolerance:
            return
    st.session_state.clicked_points.append(new_point)

# 1. Upload Image
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Resize image to a fixed width (e.g., 600px)
    display_width = 600
    display_ratio = display_width / image.width
    display_height = int(image.height * display_ratio)
    resized_image = image.resize((display_width, display_height))
    
    # Convert the PIL image to a numpy array for Plotly
    img_array = np.array(resized_image)
    
    # 2. Create a Plotly figure to display the image and capture click events.
    # Reverse the y-axis so that coordinates match the PIL image.
    fig = px.imshow(img_array)
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(clickmode='event+select')
    
    # If there are already clicked points, add them as red markers.
    if st.session_state.clicked_points:
        fig.add_scatter(
            x=[pt["x"] for pt in st.session_state.clicked_points],
            y=[pt["y"] for pt in st.session_state.clicked_points],
            mode="markers",
            marker=dict(size=12, color="red"),
            name="Clicked Points"
        )
    
    # Capture new click events on the Plotly image.
    new_clicked = plotly_events(
        fig,
        click_event=True,
        override_height=display_height,
        override_width=display_width
    )
    if new_clicked:
        for pt in new_clicked:
            add_clicked_point({"x": pt.get("x"), "y": pt.get("y")})
    
    # Refresh the Plotly figure with all clicked points.
    fig.data = []  # clear previous traces
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
    
    st.write("Below are forms for adding details to each new annotation (for each point you clicked).")
    
    # 3. For each clicked point that is not yet annotated, display a form to add annotation details.
    tolerance = 5
    for pt in st.session_state.clicked_points:
        already_annotated = any(
            abs(ann["x"] - pt["x"]) < tolerance and abs(ann["y"] - pt["y"]) < tolerance 
            for ann in st.session_state.annotations
        )
        if not already_annotated:
            with st.expander(f"Add Annotation at (x={pt['x']:.0f}, y={pt['y']:.0f})"):
                location = st.selectbox("Select location:", LOCATIONS, key=f"loc_{pt['x']}_{pt['y']}")
                annotation_value = ""
                if location != "Select...":
                    if location == "Occlusion":
                        annotation_value = "OCL"
                    else:
                        annotation_value = st.text_input("Enter pressure value (mmHg):", key=f"val_{pt['x']}_{pt['y']}")
                if location != "Select..." and st.button("Save Annotation", key=f"save_{pt['x']}_{pt['y']}"):
                    annotation = {
                        "id": st.session_state.next_id,
                        "x": pt["x"],
                        "y": pt["y"],
                        "location": location,
                        "value": annotation_value
                    }
                    st.session_state.annotations.append(annotation)
                    st.session_state.next_id += 1
                    st.success(f"Annotation {annotation['id']} added!")
    
    # 4. Display current annotations in the sidebar with delete options.
    st.sidebar.title("Annotations")
    if st.session_state.annotations:
        for ann in st.session_state.annotations.copy():
            st.sidebar.write(f"ID {ann['id']}: {ann['location']} - {ann['value']}")
            if st.sidebar.button("Delete", key=f"delete_{ann['id']}"):
                st.session_state.annotations = [a for a in st.session_state.annotations if a["id"] != ann["id"]]
                st.sidebar.success(f"Annotation {ann['id']} deleted!")
    else:
        st.sidebar.write("No annotations yet.")
    
    # 5. Generate and display side by side:
    #    - Left: The original image (the one you clicked on) with drawn markers.
    #    - Right: The annotated image with large text drawn.
    if st.button("Generate and Save Annotated Image"):
        # Left image: Draw markers (red if unannotated, green if annotated) on a copy of the original resized image.
        left_image = resized_image.copy()
        draw_left = ImageDraw.Draw(left_image)
        r = 6  # marker radius
        tolerance = 5
        for pt in st.session_state.clicked_points:
            annotated = any(
                abs(ann["x"] - pt["x"]) < tolerance and abs(ann["y"] - pt["y"]) < tolerance 
                for ann in st.session_state.annotations
            )
            color = "green" if annotated else "red"
            draw_left.ellipse(
                [(pt["x"] - r, pt["y"] - r), (pt["x"] + r, pt["y"] + r)],
                fill=color,
                outline=color
            )
        
        # Right image: Draw the annotation text onto a copy of the original image.
        right_image = resized_image.copy()
        draw_right = ImageDraw.Draw(right_image)
        # Try to use a bold font; if unavailable, fall back to a regular one. Set font size to 200.
        try:
            font = ImageFont.truetype("arialbd.ttf", 100)
        except Exception as e1:
            try:
                font = ImageFont.truetype("arial.ttf", 100)
            except Exception as e2:
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 100)
                except Exception as e3:
                    st.error("No custom font available; falling back to default font (text may be small).")
                    font = ImageFont.load_default()

        for ann in st.session_state.annotations:
            text = ann["value"]
            offset = (5, -5)
            draw_right.text(
                (ann["x"] + offset[0], ann["y"] + offset[1]),
                text,
                fill="#FFFFFF",
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )
        
        # Display the two images side by side using columns.
        col1, col2 = st.columns(2)
        with col1:
            st.image(left_image, caption="Original Image (with markers)", use_container_width=True)
        with col2:
            st.image(right_image, caption="Annotated Image (with large text)", use_container_width=True)
        
        # Save the annotated image to bytes for download.
        buf_img = io.BytesIO()
        right_image.save(buf_img, format="PNG")
        annotated_image_bytes = buf_img.getvalue()
        
        # Generate a summary table as before.
        df_full = pd.DataFrame(st.session_state.annotations)
        if not df_full.empty:
            df_summary = df_full[df_full["location"] != "Occlusion"][["location", "value"]]
        else:
            df_summary = pd.DataFrame(columns=["location", "value"])
        
        fig_table, ax = plt.subplots(figsize=(6, len(df_summary) * 0.5 + 1))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(
            cellText=df_summary.values,
            colLabels=["Location", "Pressure (mmHg)"],
            loc='center'
        )
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_text_props(weight='bold', ha='center')
            else:
                if j == 0:
                    cell.set_text_props(ha='left')
                elif j == 1:
                    cell.set_text_props(ha='right')
        plt.tight_layout()
        buf_table = io.BytesIO()
        plt.savefig(buf_table, format="PNG")
        buf_table.seek(0)
        table_png = buf_table.getvalue()
        
        st.download_button("Download Annotated Image", data=annotated_image_bytes,
                           file_name="annotated_image.png", mime="image/png")
        st.download_button("Download Summary Table (PNG)", data=table_png,
                           file_name="summary_table.png", mime="image/png")
