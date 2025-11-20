# 🏥 Venous Stenting Visualization Tool

A neurosurgical web application for visualizing and annotating venous pressure measurements on medical imaging. This tool streamlines the process of documenting venous stenting procedures by allowing clinicians to mark anatomical locations, record pressure measurements, and generate comprehensive reports.

## 📋 Features

- **Interactive Image Annotation**: Click directly on medical images to mark measurement points
- **Anatomical Location Selection**: Comprehensive list of venous anatomical locations
- **Bilateral Structure Support**: Automatic left/right side selection for paired structures
- **Image Rotation**: 90-degree rotation control for proper image orientation
- **Stenosis Marking**: Special markers for stenosis locations
- **Visual Output**: Generate annotated images with pressure values overlaid
- **Data Export**: Download results as:
  - Annotated PNG images
  - Summary tables (PNG format)
  - Excel spreadsheets for further analysis

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Stenting-Code
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   - The app will automatically open at `http://localhost:8501`

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

## 📖 User Guide

### Step 1: Upload Image
- Click "Choose a medical image" to upload a PNG, JPG, or JPEG file
- Use the "Rotate Image 90°" button if needed to orient the image correctly

### Step 2: Mark Annotation Points
- Click directly on the image where you want to add measurements
- Red markers will appear at each clicked location

### Step 3: Add Annotation Details
- For each clicked point, fill out the form that appears below the image
- Select the anatomical location from the dropdown menu
- For bilateral structures (e.g., transverse sinus), select Left or Right
- Enter the pressure value in mmHg (or select "Stenosis" for stenotic regions)
- Click "Save Annotation"

### Step 4: Review Annotations
- View all saved annotations in the sidebar
- Delete any annotation by clicking the delete button next to it
- Annotations show: ID, location, side (if applicable), and pressure value

### Step 5: Generate Output
- Click "Generate and Save Annotated Image"
- View the comparison:
  - **Left image**: Original with colored markers (green = annotated, red = unannotated)
  - **Right image**: Annotated with pressure values overlaid
- Download your files:
  - Annotated image (PNG)
  - Summary table (PNG)
  - Data spreadsheet (Excel)

## 🗂️ Project Structure

```
Stenting-Code/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── .streamlit/            # Streamlit configuration
│   └── secrets.toml       # API keys (not in version control)
├── deprecated/            # Old/test versions
│   ├── test.py
│   ├── testv2.py
│   ├── venous_stent.py
│   ├── main.py
│   └── api_maker.py
└── docs/                  # Documentation files
```

## 🔧 Technical Details

### Anatomical Locations Supported

**Midline Structures:**
- Torcula
- Posterior superior sagittal sinus
- Mid superior sagittal sinus
- Superior Vena Cava
- Inferior Vena Cava

**Bilateral Structures (require side selection):**
- Medial transverse sinus
- Lateral transverse sinus
- Transverse-sigmoid junction
- Sigmoid sinus
- Jugular bulb
- Internal jugular vein
- Internal jugular vein origin
- Subclavian

**Special Markers:**
- Stenosis (marked with red "X")
- Pre-Stenosis
- Post-Stenosis

### Technology Stack

- **Frontend Framework**: Streamlit
- **Interactive Plotting**: Plotly with streamlit-plotly-events
- **Image Processing**: Pillow (PIL)
- **Data Handling**: Pandas, NumPy
- **Visualization**: Matplotlib
- **Export**: openpyxl for Excel files

### Session State Management

The application uses Streamlit's session state to maintain:
- Annotation data (location, pressure, coordinates)
- Clicked points on the image
- Image rotation angle
- Unique annotation IDs

## 🛡️ Security Notes

- The `.streamlit/secrets.toml` file is excluded from version control
- No sensitive patient data is stored by the application
- All processing happens client-side in the browser
- Downloaded files are generated on-demand and not stored on servers

## 🤝 Contributing

This is a specialized medical tool developed by the NeuroVERT team. For questions or contributions, please contact the development team.

## 📄 License

Copyright © 2025 NeuroVERT Team. All rights reserved.

## 🐛 Troubleshooting

### Font Issues
If you see a warning about fonts, the application will fall back to default fonts. This is normal and won't affect functionality, though text may appear smaller.

### Image Upload Issues
- Ensure your image is in PNG, JPG, or JPEG format
- Large images are automatically resized to 600px width for optimal display

### Annotation Not Saving
- Make sure you've selected a location from the dropdown
- For bilateral structures, ensure you've selected Left or Right
- Check that you've entered a pressure value (unless marking stenosis)

## 📞 Support

For technical support or questions about the application, please contact the NeuroVERT development team.

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Developed by**: NeuroVERT Team
