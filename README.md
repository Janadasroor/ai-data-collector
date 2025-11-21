# 🤖 AI Training Data Collector

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, production-ready web crawler designed to collect large-scale training data for AI models. Features continuous 24-hour operation, intelligent link discovery, code collection from repositories, and robust checkpoint/resume capabilities.

## ✨ Features

### 🚀 Core Capabilities
- **24-Hour Continuous Operation** - Runs uninterrupted with automatic time management
- **Intelligent Link Discovery** - Automatically discovers and follows relevant links
- **Code Collection** - Extracts code from GitHub, GitLab, and documentation sites
- **Multi-Source Crawling** - Supports 28+ diverse data sources out of the box
- **Checkpoint & Resume** - Survives interruptions and resumes from last state
- **Duplicate Detection** - Prevents collecting the same content twice

### 📊 Data Quality
- **Content Filtering** - Minimum length thresholds for quality control
- **Language Detection** - Automatically detects content language
- **Smart Parsing** - Extracts clean text from HTML with metadata
- **Size Limits** - Prevents oversized pages from consuming resources

### 🛡️ Robust & Polite
- **Rate Limiting** - Configurable delays between requests
- **Retry Logic** - Exponential backoff for failed requests
- **User Agent Rotation** - Mimics real browser traffic
- **Error Recovery** - Handles network issues gracefully
- **Progress Tracking** - Real-time statistics and periodic reports

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/JanadaSroor/ai-data-collector.git
cd ai-data-collector

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Usage

### Basic Usage

Start a 24-hour data collection:
```bash
python app.py
```

### Advanced Usage

**Test run (5 minutes):**
```bash
python app.py --duration 0.083
```

**Custom duration (12 hours):**
```bash
python app.py --duration 12
```

**Resume from checkpoint:**
```bash
python app.py --resume
```

**Custom config file:**
```bash
python app.py --config my_config.json
```

### Quick Start Script

Use the included startup script:
```bash
./start.sh
```

## 📊 Web Dashboard

Monitor your data collection in real-time with the professional web dashboard!

### Start Dashboard
```bash
./start_dashboard.sh
# Or directly: python dashboard_server.py
```

Access at: **http://localhost:8000**

### Dashboard Features
- 📈 **Real-time Statistics** - Live updates every 2 seconds via WebSocket
- 📊 **Interactive Charts** - Progress line chart and distribution doughnut chart
- 📋 **Recent Data Table** - View latest collected items
- 📝 **Live Logs** - Color-coded log streaming
- 🎨 **Modern UI** - Dark theme with glassmorphism effects
- 📱 **Responsive** - Works on desktop, tablet, and mobile

See [DASHBOARD.md](DASHBOARD.md) for complete documentation.

## ⚙️ Configuration

Edit `config.json` to customize crawler behavior:

```json
{
  "runtime": {
    "duration_hours": 24,
    "checkpoint_interval_minutes": 10,
    "stats_report_interval_minutes": 5
  },
  "crawling": {
    "max_concurrent_requests": 10,
    "min_delay_seconds": 1.0,
    "max_delay_seconds": 3.0,
    "max_urls_to_crawl": 100000,
    "follow_external_links": true
  },
  "data_quality": {
    "min_text_length": 200,
    "min_code_length": 50,
    "detect_language": true,
    "remove_duplicates": true
  }
}
```

### Key Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `duration_hours` | How long to run the crawler | 24 |
| `max_concurrent_requests` | Parallel requests limit | 10 |
| `min_delay_seconds` | Minimum delay between requests | 1.0 |
| `max_urls_to_crawl` | Maximum URLs to visit | 100,000 |
| `min_text_length` | Minimum text length to save | 200 |
| `remove_duplicates` | Enable duplicate detection | true |

## 📁 Output Files

The crawler generates several output files:

- **`training_data.jsonl`** - Main output file with collected data (JSONL format)
- **`crawler_state.json`** - Checkpoint file for resume capability
- **`crawler_stats.json`** - Final statistics summary
- **`crawler.log`** - Detailed execution logs

### Data Format

Each line in `training_data.jsonl` is a JSON object:

```json
{
  "type": "webpage",
  "url": "https://example.com/article",
  "timestamp": "2025-11-21T19:00:00.000000",
  "title": "Article Title",
  "description": "Meta description",
  "keywords": "keyword1, keyword2",
  "content": "Main article text...",
  "language": "en",
  "size_bytes": 5432,
  "source_domain": "example.com"
}
```

For code files:
```json
{
  "type": "code",
  "url": "https://github.com/user/repo/file.py",
  "timestamp": "2025-11-21T19:00:00.000000",
  "file_extension": ".py",
  "language": "en",
  "code": "def example():\n    pass",
  "size_bytes": 1234,
  "source_domain": "github.com"
}
```

## 📊 Monitoring Progress

### Real-time Logs
```bash
tail -f crawler.log
```

### Check Data Collected
```bash
# Count collected items
wc -l training_data.jsonl

# View latest entries
tail -n 5 training_data.jsonl | jq .
```

### View Statistics
```bash
cat crawler_stats.json | jq .
```

## 🎯 Data Sources

The crawler includes 28 high-quality seed URLs by default:

### Documentation & Learning
- Python.org official documentation
- PyTorch documentation
- TensorFlow API docs
- MDN Web Docs (JavaScript)
- Real Python tutorials
- freeCodeCamp

### Code Repositories
- GitHub topics (Python, ML, AI)
- Stack Overflow questions

### Communities
- Dev.to articles
- Reddit (r/programming, r/MachineLearning)
- Hacker News

### Frameworks & Libraries
- FastAPI, Flask, Django
- NumPy, Pandas, Scikit-learn
- React, Node.js
- Rust, Go documentation

## 🔧 Advanced Features

### Checkpoint & Resume

The crawler automatically saves checkpoints every 10 minutes. If interrupted:

```bash
# Resume from last checkpoint
python app.py --resume
```

### Graceful Shutdown

Press `Ctrl+C` to stop gracefully. The crawler will:
1. Save current state to checkpoint
2. Write final statistics
3. Close all connections cleanly

### Custom Data Sources

Add your own URLs to `config.json`:

```json
{
  "seed_urls": [
    "https://your-site.com",
    "https://another-site.com"
  ],
  "allowed_domains": [
    "your-site.com",
    "another-site.com"
  ]
}
```

## 📈 Performance

Test run results (3 minutes):
- **Pages Crawled:** 492
- **Code Files:** 39
- **Data Collected:** 9.22 MB
- **Speed:** 157 pages/minute
- **Failed Requests:** 5 (1% failure rate)

Projected 24-hour performance:
- **Estimated Pages:** ~226,000
- **Estimated Data:** ~4.2 GB
- **Unique Domains:** 20+

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal & Ethical Considerations

**Important:** Always ensure you have permission to scrape websites and comply with their terms of service.

This crawler:
- ✅ Respects rate limits and implements delays
- ✅ Rotates user agents to avoid overwhelming servers
- ✅ Implements exponential backoff for failed requests
- ✅ Can be configured to respect robots.txt (recommended)

**Your Responsibilities:**
- Check website terms of service before crawling
- Respect copyright and intellectual property
- Use collected data ethically and legally
- Consider privacy implications of collected data

## 🐛 Troubleshooting

### Common Issues

**Import Error: No module named 'aiohttp'**
```bash
pip install -r requirements.txt
```

**Permission Denied: start.sh**
```bash
chmod +x start.sh
```

**Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with [aiohttp](https://docs.aiohttp.org/) for async HTTP
- HTML parsing by [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- Language detection by [langdetect](https://github.com/Mimino666/langdetect)

---

**Made with ❤️ for the AI/ML community**
