# Web Dashboard Guide

## 🚀 Quick Start

### Start the Dashboard

```bash
# Option 1: Use the startup script
./start_dashboard.sh

# Option 2: Direct command
python dashboard_server.py
```

The dashboard will be available at: **http://localhost:8000**

## 📊 Dashboard Features

### Real-Time Statistics
- **Pages Crawled** - Total number of pages collected
- **Code Files** - Number of code files extracted
- **Data Collected** - Total data size in MB
- **Speed** - Current crawling speed (pages/minute)
- **Total Items** - Total items in database
- **Queue Size** - URLs waiting to be crawled
- **Runtime** - Total elapsed time
- **Failed** - Number of failed requests

### Live Charts
- **Collection Progress** - Line chart showing pages crawled over time
- **Data Distribution** - Doughnut chart showing webpage vs code vs failed

### Recent Data Table
- View the last 20 collected items
- Shows URL, title, size, domain, and timestamp
- Auto-refreshes every 30 seconds
- Manual refresh button available

### Logs Viewer
- Real-time log streaming
- Color-coded by log level (INFO, WARNING, ERROR)
- Auto-scrolls to latest entries
- Shows last 50 log lines

## 🔧 Technical Details

### Backend (FastAPI)
- **Port**: 8000
- **WebSocket**: Real-time updates every 2 seconds
- **API Endpoints**:
  - `GET /` - Dashboard HTML
  - `GET /api/stats` - Current statistics
  - `GET /api/recent-data` - Recent collected data
  - `GET /api/config` - Current configuration
  - `GET /api/logs` - Recent log entries
  - `WS /ws` - WebSocket for real-time updates

### Frontend
- **Framework**: Vanilla JavaScript (no dependencies)
- **Charts**: Chart.js
- **Design**: Modern dark theme with glassmorphism
- **Responsive**: Works on desktop, tablet, and mobile

### WebSocket Protocol
The WebSocket sends JSON messages:
```json
{
  "type": "stats",
  "data": {
    "stats": {
      "pages_crawled": 100,
      "code_files_collected": 10,
      "total_mb": 5.2,
      "pages_per_minute": 50,
      ...
    },
    "queue_size": 1000,
    "visited_count": 100,
    "total_items": 100
  }
}
```

## 🎨 Customization

### Change Port
Edit `dashboard_server.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change 8000 to 8080
```

### Modify Update Frequency
Edit `dashboard_server.py` WebSocket section:
```python
await asyncio.sleep(2)  # Change 2 to desired seconds
```

### Customize Colors
Edit `static/style.css`:
```css
:root {
    --accent: #6366f1;  /* Change primary color */
    --bg-primary: #0a0e27;  /* Change background */
}
```

## 📱 Mobile Access

The dashboard is fully responsive. Access from mobile devices on the same network:

1. Find your computer's IP address:
   ```bash
   ip addr show | grep inet
   ```

2. Access from mobile browser:
   ```
   http://YOUR_IP:8000
   ```

## 🔒 Security Notes

**Important**: The dashboard runs without authentication by default.

For production use:
- Add authentication (JWT, OAuth, etc.)
- Use HTTPS with SSL certificates
- Restrict access by IP
- Use a reverse proxy (nginx, Apache)

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process using port
kill -9 <PID>
```

### WebSocket not connecting
- Check firewall settings
- Ensure port 8000 is open
- Check browser console for errors

### Charts not displaying
- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Verify internet connection

### No data showing
- Ensure crawler has run at least once
- Check that `training_data.jsonl` exists
- Verify `crawler_stats.json` exists

## 💡 Tips

1. **Keep dashboard running** while crawler is active for real-time monitoring
2. **Use multiple tabs** - dashboard in one, logs in another
3. **Bookmark** the dashboard URL for quick access
4. **Monitor queue size** to estimate remaining work
5. **Watch speed** to optimize crawler settings

## 🚀 Advanced Usage

### Run Dashboard on Different Machine
```bash
# On server
python dashboard_server.py

# Access from another machine
http://SERVER_IP:8000
```

### Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name dashboard.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "dashboard_server.py"]
```

## 📊 Monitoring Best Practices

1. **Check speed regularly** - Should be consistent
2. **Monitor failed requests** - High failures indicate issues
3. **Watch queue size** - Should decrease over time
4. **Review recent data** - Ensure quality is good
5. **Check logs** - Look for errors or warnings

---

**Enjoy your professional data collection dashboard!** 🎉
