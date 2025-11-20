# Deployment Guide

## Streamlit Community Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step-by-Step Instructions

#### 1. Prepare Your Repository

Ensure your repository has the following structure:
```
Stenting-Code/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

#### 2. Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Venous Stenting Visualization Tool"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

#### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Configure:
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom subdomain
5. Click "Deploy"

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

#### 4. Monitor Deployment

- Watch the deployment logs in the Streamlit Cloud dashboard
- First deployment typically takes 2-3 minutes
- The app will automatically redeploy when you push changes to GitHub

### Custom Domain (Optional)

If you want a custom domain instead of the `.streamlit.app` URL:

1. Upgrade to Streamlit Cloud Pro (if needed)
2. Go to app settings
3. Add your custom domain
4. Update your DNS records as instructed

## Alternative: Heroku Deployment

If you prefer Heroku or need a custom URL:

### Prerequisites
- Heroku account
- Heroku CLI installed

### Additional Files Needed

1. **Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

2. **Create `Procfile`:**
```
web: sh setup.sh && streamlit run app.py
```

### Deployment Steps

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Deploy
git push heroku main

# Open the app
heroku open
```

Your app will be live at: `https://your-app-name.herokuapp.com`

## Troubleshooting

### Common Issues

**Issue**: App won't start
- Check the logs in Streamlit Cloud dashboard
- Verify all dependencies are in `requirements.txt`
- Ensure `app.py` is in the root directory

**Issue**: Missing dependencies
- Add any missing packages to `requirements.txt`
- Push changes to GitHub (Streamlit Cloud auto-redeploys)

**Issue**: Slow performance
- Large images may take time to process
- Consider adding image size limits
- Streamlit Cloud free tier has resource limits

**Issue**: Font warnings
- This is normal and doesn't affect functionality
- The app uses fallback fonts automatically

## Performance Optimization

### For Production Use

1. **Add caching** to improve performance:
```python
@st.cache_data
def load_image(uploaded_file):
    return Image.open(uploaded_file)
```

2. **Limit file sizes** in the uploader:
```python
uploaded_file = st.file_uploader(
    "Choose an image", 
    type=["png", "jpg", "jpeg"],
    help="Maximum file size: 10MB"
)
```

3. **Monitor usage** via Streamlit Cloud analytics

## Security Considerations

- No patient data is stored on servers
- All processing happens client-side
- Downloads are generated on-demand
- No authentication required (add if needed for production)

## Updating the App

To update your deployed app:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will automatically detect the changes and redeploy.

## Support

For deployment issues:
- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
- GitHub Issues: Create an issue in your repository
