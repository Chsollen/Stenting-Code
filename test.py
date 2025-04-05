import streamlit as st
from streamlit_plotly_events import plotly_events  # Install via: pip install streamlit-plotly-events
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
import io
import matplotlib.pyplot as plt

st.title("Venous Pressure Annotation App (Without st_canvas)")

st.write("""
Upload an image, then click on the image to add annotation points.  
Each click is recorded, and you can select a venous location and enter a pressure value.
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

# 1. Upload Image
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Resize image to a fixed width (e.g., 600px) to reduce scrolling
    display_width = 600
    display_ratio = display_width / image.width
    display_height = int(image.height * display_ratio)
    resized_image = image.resize((display_width, display_height))
    st.image(resized_image, caption="Uploaded Image", width=display_width)

    # Convert the PIL image to a numpy array for Plotly
    img_array = np.array(resized_image)

    # 2. Create a Plotly figure to display the image and capture click events
    fig = px.imshow(img_array)
    fig.update_layout(clickmode='event+select')
    st.write("Click on the image to mark annotations:")

    # Capture click events on the Plotly image
    clicked_points = plotly_events(
        fig,
        click_event=True,
        override_height=display_height,
        override_width=display_width
    )

    # Initialize session state for annotations if not already set
    if "annotations" not in st.session_state:
        st.session_state.annotations = []

    # 3. Process each click event to create an annotation input form
    if clicked_points:
        for point in clicked_points:
            x = point.get('x')
            y = point.get('y')
            st.write(f"Annotation at (x={x:.0f}, y={y:.0f}):")
            location = st.selectbox("Select location:", LOCATIONS, key=f"loc_{x}_{y}")
            if location != "Select...":
                if location == "Occlusion":
                    annotation_value = "OCL"
                else:
                    annotation_value = st.text_input("Enter pressure value (mmHg):", key=f"val_{x}_{y}")
                if st.button("Add Annotation", key=f"add_{x}_{y}"):
                    annotation = {"x": x, "y": y, "location": location, "value": annotation_value}
                    st.session_state.annotations.append(annotation)
                    st.success(f"Annotation added at (x={x:.0f}, y={y:.0f})")

    # 4. Display current annotations
    st.write("Current Annotations:")
    if st.session_state.annotations:
        st.write(pd.DataFrame(st.session_state.annotations))
    else:
        st.write("No annotations yet.")

    # 5. Generate annotated image and summary table as PNG for download
    if st.button("Generate and Save Annotated Image"):
        # Create a copy of the resized image to draw annotations on
        annotated_image = resized_image.copy()
        draw = ImageDraw.Draw(annotated_image)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font = ImageFont.load_default()
        
        # Draw each annotation on the image using the pressure value (or OCL)
        for ann in st.session_state.annotations:
            text = ann["value"]
            offset = (5, -5)
            draw.text(
                (ann["x"] + offset[0], ann["y"] + offset[1]),
                text,
                fill="#FFFFFF",
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )
        
        # Save annotated image to a bytes buffer
        buf_img = io.BytesIO()
        annotated_image.save(buf_img, format="PNG")
        annotated_image_bytes = buf_img.getvalue()
        
        # Create a summary table (exclude rows with "Occlusion")
        df_full = pd.DataFrame(st.session_state.annotations)
        if not df_full.empty:
            df_summary = df_full[df_full["location"] != "Occlusion"][["location", "value"]]
        else:
            df_summary = pd.DataFrame(columns=["location", "value"])
        
        # Generate a PNG image of the summary table using matplotlib
        fig_table, ax = plt.subplots(figsize=(6, len(df_summary)*0.5 + 1))
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

        # Provide download buttons for the annotated image and summary table
        st.download_button("Download Annotated Image", data=annotated_image_bytes, file_name="annotated_image.png", mime="image/png")
        st.download_button("Download Summary Table (PNG)", data=table_png, file_name="summary_table.png", mime="image/png")
