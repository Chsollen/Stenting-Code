# Quick Start Guide

## For Developers

### Run Locally (3 Steps)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. **Open browser**
   - Automatically opens at `http://localhost:8501`

## For End Users

### Using the Deployed App

1. **Navigate to the app URL** (provided by your administrator)

2. **Upload an image**
   - Click "Choose a medical image"
   - Select PNG, JPG, or JPEG file
   - Rotate if needed using the rotate button

3. **Add annotations**
   - Click on the image where you want to mark a measurement
   - Fill out the form that appears:
     - Select anatomical location
     - Select side (Left/Right) if required
     - Enter pressure value in mmHg
   - Click "Save Annotation"

4. **Review your work**
   - Check the sidebar for all annotations
   - Delete any mistakes using the delete button

5. **Generate output**
   - Click "Generate and Save Annotated Image"
   - Download your files:
     - Annotated image (PNG)
     - Summary table (PNG)
     - Excel spreadsheet

## Tips

- **Green markers** = annotated points
- **Red markers** = unannotated points
- **Stenosis** locations are marked with a red "X"
- All data is processed locally - nothing is sent to servers
- You can rotate images in 90° increments

## Keyboard Shortcuts

- None currently (all interactions are mouse-based)

## File Formats

**Input:**
- PNG, JPG, JPEG images

**Output:**
- Annotated images: PNG
- Summary tables: PNG
- Data export: XLSX (Excel)

## Common Workflows

### Basic Annotation
1. Upload → Click → Annotate → Generate → Download

### Multiple Measurements
1. Upload → Click multiple points → Annotate each → Generate → Download

### Stenosis Marking
1. Upload → Click on stenosis → Select "Stenosis" → Save → Generate

## Need Help?

- Check the main README.md for detailed documentation
- See DEPLOYMENT.md for hosting instructions
- Contact your system administrator for technical support
