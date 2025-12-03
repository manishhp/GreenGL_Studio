# 🌱 GreenGL Studio - Carbon-Aware GPU Scheduler

**Make your AI training greener by running when the grid is cleanest!**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Run GreenGL Studio
```bash
streamlit run greengl_studio.py
```

The app will open automatically at `http://localhost:8501`

## 📋 What's Included

### Core Files (Must Include)
- ✅ `greengl_studio.py` - Main Streamlit web application
- ✅ `get_best_start_time.py` - Carbon scheduling logic
- ✅ `sample_ml_script.py` - Example script for testing
- ✅ `requirements.txt` - All dependencies
- ✅ `cats/` directory - CATS library code

### Documentation
- 📄 `README_GREENGL.md` - This file (setup guide)
- 📄 `PITCH_GUIDE.md` - Hackathon pitch script
- 📄 `WOW_FACTOR_UPDATE.md` - Feature documentation
- 📄 `GREENGL_QUICKSTART.md` - User quick start
- 📄 `GREENGL_STUDIO_README.md` - Full documentation

### Optional Files
- 📄 `demo.py` - CLI demo tool
- 📄 `example_usage.py` - Usage examples
- 📄 Various markdown docs

## 🎯 Features

- 🌍 **24-hour carbon intensity forecast** with RED/GREEN zones
- 🖥️ **Live simulation console** showing scheduler in action
- 📊 **Interactive charts** comparing "dirty" vs "clean" energy
- 💰 **Carbon savings calculator** (typically 60-70% reduction)
- 🎬 **Replay animation** for demos
- 📁 **Simple file upload** for Python scripts

## 🎬 Demo Instructions

### For Hackathon Judges:
1. Run `streamlit run greengl_studio.py`
2. Upload `sample_ml_script.py`
3. Set duration to 60 minutes
4. Click "🌍 Schedule Job"
5. See the magic:
   - RED ZONE (dirty grid) vs GREEN ZONE (clean grid)
   - Live console logs showing GPU sleeping/waking
   - 64% carbon reduction

### Key Demo Points:
- **NOW** = Red zone (245 gCO2/kWh) - Fossil fuels
- **2 AM** = Green zone (89 gCO2/kWh) - Renewables
- **Savings** = 64% CO2 reduction just by timing!

## 🏗️ Architecture

```
GreenGL Studio
├── greengl_studio.py          # Streamlit UI
├── get_best_start_time.py     # Scheduling logic
├── cats/                       # CATS library
│   ├── forecast.py            # WindowedForecast algorithm
│   ├── CI_api_query.py        # Carbon intensity API
│   └── ...                    # Other CATS modules
└── requirements.txt           # Dependencies
```

## 📦 Dependencies Explained

### Core (Required)
- **streamlit** - Web UI framework
- **plotly** - Interactive charts
- **pandas** - Data handling
- **requests-cache** - API caching
- **PyYAML** - Configuration

### What Gets Installed
```bash
pip install -r requirements.txt
```
Installs everything needed for GreenGL Studio to work.

## 🔧 For Developers

### Running Tests
```bash
# Test the scheduling function
python get_best_start_time.py

# Test with examples
python example_usage.py

# Interactive CLI demo
python demo.py
```

### Customization
Edit `greengl_studio.py` to customize:
- Duration ranges (line ~350)
- Power consumption assumptions (line ~100)
- Chart styling (various sections)
- Console log messages (line ~200)

## 🌐 For Deployment

### Local Network Access
Others on your network can access at:
```
http://YOUR_LOCAL_IP:8501
```
(shown in terminal when you run streamlit)

### Cloud Deployment Options
- **Streamlit Cloud** (Free): https://streamlit.io/cloud
- **Heroku**: Add `Procfile` and `setup.sh`
- **AWS/GCP**: Use standard Python deployment

## ❓ Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
streamlit run greengl_studio.py --server.port 8502
```

### Charts not showing
```bash
pip install --upgrade plotly
```

### CATS import errors
Make sure you're in the `cats` directory or install it:
```bash
pip install -e .
```

## 🎓 How It Works

1. **Upload Script** - Any Python file
2. **Set Duration** - How long it will run
3. **AI Analysis** - Checks grid carbon intensity forecast
4. **Optimal Scheduling** - Finds greenest time window
5. **Visual Results** - Shows savings with charts and console

### The Algorithm
Uses CATS (Climate-Aware Task Scheduler):
- Gets 48-hour carbon intensity forecast
- Creates overlapping time windows
- Calculates average CI for each window
- Finds minimum = optimal time
- Typically 2-6 AM (renewable energy peak)

## 💡 Real Impact

### Single Job
- Duration: 2 hours
- NOW: 250 gCO2/kWh = 300g CO2
- OPTIMAL: 90 gCO2/kWh = 108g CO2
- **Savings: 192g CO2 (64%)**

### Scaled Up (100 users)
- Daily: ~19 kg CO2 saved
- Annual: ~7 tons CO2 saved
- Equivalent: ~17,000 km not driven

## 🏆 Credits

Built on top of:
- **CATS** - Climate-Aware Task Scheduler (Cambridge/Oxford)
- **Streamlit** - Web app framework
- **Plotly** - Visualization library
- **National Grid ESO** - Carbon intensity API

## 📄 License

MIT License - Same as CATS project

## 🤝 Contributing

Want to improve GreenGL Studio?
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

- Check documentation in `GREENGL_STUDIO_README.md`
- Review pitch guide in `PITCH_GUIDE.md`
- See examples in `example_usage.py`

## 🌟 Star This Repo!

If GreenGL Studio helps you make computing greener, give it a ⭐!

---

**🌱 Making computing greener, one job at a time!**
