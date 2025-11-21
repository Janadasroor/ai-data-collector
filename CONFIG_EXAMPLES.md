# Example Configuration for AI Data Collector

This is an example configuration file. Copy this to `config.json` and customize for your needs.

## Quick Profiles

### Conservative (Polite Crawling)
```json
{
  "crawling": {
    "max_concurrent_requests": 3,
    "min_delay_seconds": 2.0,
    "max_delay_seconds": 5.0
  }
}
```

### Balanced (Default)
```json
{
  "crawling": {
    "max_concurrent_requests": 10,
    "min_delay_seconds": 1.0,
    "max_delay_seconds": 3.0
  }
}
```

### Aggressive (Fast Collection)
```json
{
  "crawling": {
    "max_concurrent_requests": 20,
    "min_delay_seconds": 0.5,
    "max_delay_seconds": 1.5
  }
}
```

## Custom Data Sources

### Academic Papers
```json
{
  "seed_urls": [
    "https://arxiv.org/list/cs.AI/recent",
    "https://arxiv.org/list/cs.LG/recent"
  ],
  "allowed_domains": [
    "arxiv.org"
  ]
}
```

### News Sites
```json
{
  "seed_urls": [
    "https://news.ycombinator.com/",
    "https://techcrunch.com/",
    "https://www.theverge.com/"
  ],
  "allowed_domains": [
    "news.ycombinator.com",
    "techcrunch.com",
    "theverge.com"
  ]
}
```

### Code Repositories
```json
{
  "seed_urls": [
    "https://github.com/topics/python",
    "https://github.com/topics/machine-learning",
    "https://gitlab.com/explore/projects/topics/AI"
  ],
  "allowed_domains": [
    "github.com",
    "gitlab.com"
  ],
  "code_extensions": [
    ".py", ".js", ".java", ".cpp", ".go", ".rs"
  ]
}
```
