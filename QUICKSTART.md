# Quick Start Guide

Get started with AI Data Collector in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- 1GB+ free disk space

## 🚀 Installation

### Step 1: Clone or Download

```bash
# If using git
git clone https://github.com/yourusername/ai-data-collector.git
cd ai-data-collector

# Or download and extract the ZIP file
```

### Step 2: Setup Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 First Run

### Test Run (5 minutes)

```bash
python app.py --duration 0.083
```

This will:
- ✅ Crawl for 5 minutes
- ✅ Collect data from multiple sources
- ✅ Create `training_data.jsonl`
- ✅ Generate statistics

### Check Results

```bash
# See how many items collected
wc -l training_data.jsonl

# View sample data
head -n 3 training_data.jsonl

# Check statistics
cat crawler_stats.json
```

## 📊 Monitor Progress

### Watch Live Logs
```bash
tail -f crawler.log
```

### Check Data Quality
```bash
# View latest collected items
tail -n 5 training_data.jsonl | jq .
```

## ⚙️ Customize

### Edit Configuration

Open `config.json` and modify:

```json
{
  "runtime": {
    "duration_hours": 24  // Change to your desired duration
  },
  "crawling": {
    "max_concurrent_requests": 10  // Adjust based on your internet
  }
}
```

### Add Your Own URLs

```json
{
  "seed_urls": [
    "https://your-website.com",
    "https://another-site.com"
  ]
}
```

## 🎬 Full 24-Hour Run

When ready for production:

```bash
# Start the collector
python app.py

# It will run for 24 hours
# Press Ctrl+C to stop early (saves checkpoint)
```

## 🔄 Resume After Interruption

```bash
# If interrupted, resume with:
python app.py --resume
```

## 📈 Expected Results

After 24 hours, you should have:
- 📄 ~200,000+ pages collected
- 💾 ~4GB of training data
- 🌐 Content from 20+ domains
- 💻 Thousands of code examples

## 🆘 Troubleshooting

### "No module named 'aiohttp'"
```bash
pip install -r requirements.txt
```

### "Permission denied: start.sh"
```bash
chmod +x start.sh
```

### Low collection rate
- Increase `max_concurrent_requests` in config.json
- Decrease `min_delay_seconds`
- Check your internet connection

## 📚 Next Steps

1. ✅ Read the full [README.md](README.md)
2. ✅ Check [CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md) for advanced setups
3. ✅ Review collected data quality
4. ✅ Customize for your specific use case

## 💡 Tips

- Start with a short test run to verify everything works
- Monitor the first few minutes to ensure quality data
- Adjust delays if you get rate limited
- Use `--resume` if you need to restart

## 🎉 You're Ready!

Your AI training data collector is now set up and ready to gather high-quality data for your machine learning projects!

For questions or issues, check the [README.md](README.md) or open an issue on GitHub.
