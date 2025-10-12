# How to Deploy Your MIT Dashboard Online

## Option 1: Streamlit Community Cloud (FREE & EASIEST)

### Steps:
1. **Push to GitHub:**
   - Create a new repository on GitHub
   - Upload your files: `app.py`, `MITs.xlsx`, `combined_mit_data.csv`, `requirements.txt`
   - Make sure your repository is public

2. **Deploy on Streamlit:**
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set main file path to: `app.py`
   - Click "Deploy!"

3. **Share the URL:**
   - You'll get a URL like: `https://your-app-name.streamlit.app`
   - Share this with your boss

### Requirements:
- GitHub account (free)
- Your repository must be public
- All data files must be in the repository

---

## Option 2: Heroku (FREE tier available)

### Steps:
1. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Update requirements.txt:**
   ```
   streamlit
   plotly
   pandas
   openpyxl
   ```

3. **Deploy to Heroku:**
   - Install Heroku CLI
   - Run: `heroku create your-app-name`
   - Run: `git push heroku main`

---

## Option 3: Railway (FREE tier available)

### Steps:
1. **Connect GitHub repository**
2. **Set build command:** `pip install -r requirements.txt`
3. **Set start command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. **Deploy automatically**

---

## Option 4: Local Network Sharing (Quick Test)

If you just want to test quickly:
1. Find your computer's IP address
2. Run: `streamlit run app.py --server.address=0.0.0.0`
3. Share: `http://YOUR_IP:8501`

**Note:** This only works on the same network.

---

## Recommended: Streamlit Community Cloud
- ✅ Completely FREE
- ✅ Easy setup (5 minutes)
- ✅ Automatic updates when you push to GitHub
- ✅ Professional URL
- ✅ No server management needed
