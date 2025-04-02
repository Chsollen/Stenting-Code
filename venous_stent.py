import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

st.title("Venous Pressure Annotation App")

st.write("""
Upload an image, then click on the image to add annotation points.  
For each point, choose a venous location from the dropdown.  
If you select **Occlusion**, a big bold **OCL** will be used instead of a pressure value.  
Annotations are numbered for reference in the sidebar (for deletion), but the final annotated image will only display the pressure value.
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
    
    # Convert resized_image to RGB and then to a NumPy array
    bg_image = np.ascontiguousarray(np.array(resized_image.convert("RGB")), dtype=np.uint8)


    
    # 2. Create a drawing canvas overlay on the resized image using the NumPy array
    canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",  # required parameter, but not used here
    stroke_width=3,
    stroke_color="red",
    background_image=bg_image,
    update_streamlit=True,
    height=display_height,
    width=display_width,
    drawing_mode="point",
    key="canvas",
    )


    
    # Initialize session state for annotations and next annotation ID if not already set
    if "annotations" not in st.session_state:
        st.session_state.annotations = []
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1

    # 3. Process canvas clicks: add an annotation for each new point
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        for obj in objects:
            if obj.get("type") == "circle":
                x = obj.get("left")
                y = obj.get("top")
                # Check if this point is already annotated (tolerance: 5 pixels)
                exists = any(abs(ann["x"] - x) < 5 and abs(ann["y"] - y) < 5 for ann in st.session_state.annotations)
                if not exists:
                    st.write(f"New annotation at (x={x:.0f}, y={y:.0f}):")
                    location = st.selectbox(
                        "Select location:",
                        LOCATIONS,
                        key=f"loc_{x}_{y}"
                    )
                    if location != "Select...":
                        if location == "Occlusion":
                            annotation_value = "OCL"  # Big bold occlusion indicator
                        else:
                            annotation_value = st.text_input(
                                "Enter pressure value (mmHg):",
                                key=f"val_{x}_{y}"
                            )
                        if st.button("Add Annotation", key=f"add_{x}_{y}"):
                            annotation = {
                                "id": st.session_state.next_id,
                                "x": x,
                                "y": y,
                                "location": location,
                                "value": annotation_value
                            }
                            st.session_state.annotations.append(annotation)
                            st.session_state.next_id += 1
                            st.success(f"Annotation {annotation['id']} added!")
    
    # 4. Display current annotations in the sidebar with delete options
    st.sidebar.title("Annotations")
    if st.session_state.annotations:
        for ann in st.session_state.annotations.copy():
            st.sidebar.write(f"ID {ann['id']}: {ann['location']} - {ann['value']}")
            if st.sidebar.button("Delete", key=f"delete_{ann['id']}"):
                st.session_state.annotations = [a for a in st.session_state.annotations if a["id"] != ann["id"]]
                st.sidebar.success(f"Annotation {ann['id']} deleted!")
                st.experimental_rerun()
    else:
        st.sidebar.write("No annotations yet.")
    
    # 5. Generate annotated image and summary table as PNG for download
    if st.button("Generate and Save Annotated Image"):
        # Annotate the image (using the resized version)
        annotated_image = resized_image.copy()
        draw = ImageDraw.Draw(annotated_image)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except Exception as e:
            font = ImageFont.load_default()
        
        # Draw each annotation on the image using only the pressure value (or OCL)
        for ann in st.session_state.annotations:
            text = ann["value"]  # Do not include the ID in the final image
            offset = (5, -5)
            draw.text(
                (ann["x"] + offset[0], ann["y"] + offset[1]),
                text,
                fill="#FFFFFF",    # White font color
                font=font,
                stroke_width=2,    # Thicker text outline
                stroke_fill="black"
            )
        
        buf_img = io.BytesIO()
        annotated_image.save(buf_img, format="PNG")
        annotated_image_bytes = buf_img.getvalue()
        
        # Create a summary table with only location and pressure (mmHg)
        # Exclude rows where location is "Occlusion"
        df_full = pd.DataFrame(st.session_state.annotations)
        if not df_full.empty:
            df_summary = df_full[df_full["location"] != "Occlusion"][["location", "value"]]
        else:
            df_summary = pd.DataFrame(columns=["location", "value"])
        
        # Generate a PNG image of the summary table using matplotlib
        fig, ax = plt.subplots(figsize=(6, len(df_summary)*0.5 + 1))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(
            cellText=df_summary.values,
            colLabels=["Location", "Pressure (mmHg)"],
            loc='center'
        )
        # Format table: left-align location, right-align pressure
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
        
        st.download_button("Download Annotated Image", data=annotated_image_bytes, file_name="annotated_image.png", mime="image/png")
        st.download_button("Download Summary Table (PNG)", data=table_png, file_name="summary_table.png", mime="image/png")
