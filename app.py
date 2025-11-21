import asyncio
import aiohttp
import aiofiles
import json
import logging
import random
import re
import signal
import sys
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from pathlib import Path

try:
    import tldextract
    from langdetect import detect, LangDetectException
    LANG_DETECT_AVAILABLE = True
except ImportError:
    LANG_DETECT_AVAILABLE = False
    print("Warning: langdetect not available. Language detection disabled.")

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Statistics:
    """Track crawler statistics"""
    def __init__(self):
        self.pages_crawled = 0
        self.pages_failed = 0
        self.code_files_collected = 0
        self.total_bytes = 0
        self.duplicates_skipped = 0
        self.start_time = time.time()
        self.last_report_time = time.time()
        
    def to_dict(self):
        elapsed = time.time() - self.start_time
        return {
            "pages_crawled": self.pages_crawled,
            "pages_failed": self.pages_failed,
            "code_files_collected": self.code_files_collected,
            "total_bytes": self.total_bytes,
            "total_mb": round(self.total_bytes / (1024 * 1024), 2),
            "duplicates_skipped": self.duplicates_skipped,
            "elapsed_seconds": int(elapsed),
            "elapsed_hours": round(elapsed / 3600, 2),
            "pages_per_minute": round(self.pages_crawled / (elapsed / 60), 2) if elapsed > 0 else 0
        }
    
    def report(self):
        stats = self.to_dict()
        logger.info("=" * 80)
        logger.info(f"📊 PROGRESS REPORT")
        logger.info(f"   Pages Crawled: {stats['pages_crawled']}")
        logger.info(f"   Code Files: {stats['code_files_collected']}")
        logger.info(f"   Data Collected: {stats['total_mb']} MB")
        logger.info(f"   Failed: {stats['pages_failed']}")
        logger.info(f"   Duplicates Skipped: {stats['duplicates_skipped']}")
        logger.info(f"   Runtime: {stats['elapsed_hours']} hours")
        logger.info(f"   Speed: {stats['pages_per_minute']} pages/min")
        logger.info("=" * 80)


class EnhancedDataCollector:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.stats = Statistics()
        
        # URL management
        self.urls_to_visit = set(self.config["seed_urls"])
        self.visited_urls = set()
        self.failed_urls = {}  # URL -> failure count
        self.content_hashes = set()  # For duplicate detection
        
        # Runtime control
        self.running = True
        self.start_time = None
        self.end_time = None
        
        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.config["crawling"]["max_concurrent_requests"])
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found!")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown on Ctrl+C"""
        logger.info("\n🛑 Shutdown signal received. Saving state and exiting gracefully...")
        self.running = False
    
    def get_random_headers(self) -> Dict[str, str]:
        """Returns headers with a random User-Agent"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is in allowed list"""
        if not self.config["crawling"]["follow_external_links"]:
            return True
            
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for allowed in self.config["allowed_domains"]:
            if allowed in domain:
                return True
        return False
    
    def is_code_url(self, url: str) -> bool:
        """Check if URL points to a code file"""
        path = urlparse(url).path.lower()
        for ext in self.config["code_extensions"]:
            if path.endswith(ext):
                return True
        return False
    
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract and normalize links from HTML"""
        links = set()
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup.find_all(['a', 'link'], href=True):
                href = tag['href']
                # Normalize URL
                absolute_url = urljoin(base_url, href)
                
                # Remove fragments
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                       parsed.params, parsed.query, ''))
                
                # Filter valid URLs
                if clean_url.startswith(('http://', 'https://')) and self.is_allowed_domain(clean_url):
                    links.add(clean_url)
        except Exception as e:
            logger.debug(f"Error extracting links: {e}")
        
        return links
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def get_content_hash(self, content: str) -> str:
        """Generate hash for duplicate detection"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language of text"""
        if not LANG_DETECT_AVAILABLE or not self.config["data_quality"]["detect_language"]:
            return None
        try:
            return detect(text)
        except LangDetectException:
            return None
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch URL with retry logic"""
        async with self.semaphore:
            retries = 0
            retry_limit = self.config["crawling"]["retry_limit"]
            
            while retries < retry_limit:
                try:
                    timeout = aiohttp.ClientTimeout(total=self.config["crawling"]["request_timeout_seconds"])
                    async with session.get(url, headers=self.get_random_headers(), timeout=timeout) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Check size limit
                            size_mb = len(content.encode('utf-8')) / (1024 * 1024)
                            if size_mb > self.config["data_quality"]["max_page_size_mb"]:
                                logger.warning(f"Page too large ({size_mb:.2f}MB): {url}")
                                return None
                            return content
                        elif response.status in [429, 503]:
                            wait_time = 2 ** retries
                            logger.warning(f"Rate limited on {url}. Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            retries += 1
                        else:
                            logger.warning(f"Failed {url}: Status {response.status}")
                            return None
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on {url}")
                    retries += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.debug(f"Error fetching {url}: {e}")
                    retries += 1
                    await asyncio.sleep(1)
            
            return None
    
    def parse_code_content(self, content: str, url: str) -> Optional[Dict]:
        """Parse code file content"""
        try:
            # Detect file extension
            path = urlparse(url).path
            extension = Path(path).suffix
            
            # Basic quality check
            if len(content) < self.config["data_quality"]["min_code_length"]:
                return None
            
            # Detect language
            language = self.detect_language(content[:500]) if len(content) > 500 else None
            
            return {
                "type": "code",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "file_extension": extension,
                "language": language,
                "code": content[:50000],  # Limit code size
                "size_bytes": len(content.encode('utf-8')),
                "source_domain": urlparse(url).netloc
            }
        except Exception as e:
            logger.debug(f"Error parsing code from {url}: {e}")
            return None
    
    def parse_content(self, html: str, url: str) -> Optional[Dict]:
        """Extract relevant data from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted tags
            for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                script.decompose()
            
            # Get Title
            title = soup.title.string if soup.title else "No Title"
            
            # Get meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag['content']
            
            # Get keywords
            keywords = ""
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                keywords = keywords_tag['content']
            
            # Get Main Text Content
            text_content = ""
            
            # Priority: Article tag -> Main tag -> Body
            main_node = soup.find('article') or soup.find('main') or soup.body
            
            if main_node:
                text_content = main_node.get_text(separator=' ')
            
            cleaned_text = self.clean_text(text_content)
            
            # Quality Check
            if len(cleaned_text) < self.config["data_quality"]["min_text_length"]:
                return None
            
            # Duplicate detection
            if self.config["data_quality"]["remove_duplicates"]:
                content_hash = self.get_content_hash(cleaned_text)
                if content_hash in self.content_hashes:
                    self.stats.duplicates_skipped += 1
                    return None
                self.content_hashes.add(content_hash)
            
            # Detect language
            language = self.detect_language(cleaned_text[:1000])
            
            return {
                "type": "webpage",
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "title": self.clean_text(title),
                "description": self.clean_text(meta_desc),
                "keywords": keywords,
                "content": cleaned_text,
                "language": language,
                "size_bytes": len(cleaned_text.encode('utf-8')),
                "source_domain": urlparse(url).netloc
            }
        
        except Exception as e:
            logger.debug(f"Error parsing {url}: {e}")
            return None
    
    async def save_data(self, data: Dict):
        """Append data to JSONL file asynchronously"""
        if not data:
            return
        
        try:
            async with aiofiles.open(self.config["output"]["data_file"], 'a', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            # Update statistics
            self.stats.total_bytes += data.get('size_bytes', 0)
            if data.get('type') == 'code':
                self.stats.code_files_collected += 1
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    async def save_checkpoint(self):
        """Save crawler state for resume capability"""
        try:
            state = {
                "timestamp": datetime.utcnow().isoformat(),
                "visited_urls": list(self.visited_urls),
                "urls_to_visit": list(self.urls_to_visit),
                "failed_urls": self.failed_urls,
                "statistics": self.stats.to_dict(),
                "start_time": self.start_time.isoformat() if self.start_time else None
            }
            
            async with aiofiles.open(self.config["output"]["checkpoint_file"], 'w', encoding='utf-8') as f:
                await f.write(json.dumps(state, indent=2, ensure_ascii=False))
            
            logger.info(f"💾 Checkpoint saved: {len(self.visited_urls)} visited, {len(self.urls_to_visit)} queued")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    async def load_checkpoint(self) -> bool:
        """Load crawler state from checkpoint"""
        try:
            checkpoint_path = Path(self.config["output"]["checkpoint_file"])
            if not checkpoint_path.exists():
                return False
            
            async with aiofiles.open(checkpoint_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                state = json.loads(content)
            
            self.visited_urls = set(state.get("visited_urls", []))
            self.urls_to_visit = set(state.get("urls_to_visit", []))
            self.failed_urls = state.get("failed_urls", {})
            
            # Restore statistics
            stats_data = state.get("statistics", {})
            self.stats.pages_crawled = stats_data.get("pages_crawled", 0)
            self.stats.pages_failed = stats_data.get("pages_failed", 0)
            self.stats.code_files_collected = stats_data.get("code_files_collected", 0)
            self.stats.total_bytes = stats_data.get("total_bytes", 0)
            self.stats.duplicates_skipped = stats_data.get("duplicates_skipped", 0)
            
            if state.get("start_time"):
                self.start_time = datetime.fromisoformat(state["start_time"])
            
            logger.info(f"✅ Checkpoint loaded: {len(self.visited_urls)} visited, {len(self.urls_to_visit)} queued")
            return True
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return False
    
    async def process_url(self, session: aiohttp.ClientSession, url: str):
        """Process a single URL"""
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        # Random delay for politeness
        delay = random.uniform(
            self.config["crawling"]["min_delay_seconds"],
            self.config["crawling"]["max_delay_seconds"]
        )
        await asyncio.sleep(delay)
        
        logger.info(f"🔍 Crawling [{len(self.visited_urls)}]: {url[:100]}")
        
        # Fetch content
        content = await self.fetch(session, url)
        if not content:
            self.stats.pages_failed += 1
            self.failed_urls[url] = self.failed_urls.get(url, 0) + 1
            return
        
        # Parse based on content type
        data = None
        if self.is_code_url(url):
            data = self.parse_code_content(content, url)
        else:
            data = self.parse_content(content, url)
            
            # Extract links for further crawling
            if data and self.config["crawling"]["follow_external_links"]:
                new_links = self.extract_links(content, url)
                # Add new links to queue (limit to prevent infinite crawling)
                for link in new_links:
                    if link not in self.visited_urls and len(self.urls_to_visit) < self.config["crawling"]["max_urls_to_crawl"]:
                        self.urls_to_visit.add(link)
        
        # Save data
        if data:
            await self.save_data(data)
            self.stats.pages_crawled += 1
            logger.info(f"✅ Saved: {url[:80]}")
    
    async def periodic_checkpoint(self):
        """Periodically save checkpoints"""
        interval = self.config["runtime"]["checkpoint_interval_minutes"] * 60
        while self.running:
            await asyncio.sleep(interval)
            if self.running:
                await self.save_checkpoint()
    
    async def periodic_stats_report(self):
        """Periodically report statistics"""
        interval = self.config["runtime"]["stats_report_interval_minutes"] * 60
        while self.running:
            await asyncio.sleep(interval)
            if self.running:
                self.stats.report()
    
    def should_continue(self) -> bool:
        """Check if crawler should continue running"""
        if not self.running:
            return False
        
        # Check time limit
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            max_duration = timedelta(hours=self.config["runtime"]["duration_hours"])
            if elapsed >= max_duration:
                logger.info(f"⏰ Time limit reached ({self.config['runtime']['duration_hours']} hours)")
                return False
        
        # Check if we have URLs to visit
        if not self.urls_to_visit:
            logger.info("📭 No more URLs to visit")
            return False
        
        # Check max URLs limit
        if len(self.visited_urls) >= self.config["crawling"]["max_urls_to_crawl"]:
            logger.info(f"🎯 Max URLs limit reached ({self.config['crawling']['max_urls_to_crawl']})")
            return False
        
        return True
    
    async def run(self, resume: bool = False):
        """Main crawler orchestrator"""
        logger.info("🚀 Starting Enhanced AI Data Collector")
        logger.info(f"⏱️  Duration: {self.config['runtime']['duration_hours']} hours")
        logger.info(f"🌐 Seed URLs: {len(self.config['seed_urls'])}")
        logger.info(f"📊 Max concurrent requests: {self.config['crawling']['max_concurrent_requests']}")
        
        # Load checkpoint if resuming
        if resume:
            await self.load_checkpoint()
        
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.config["runtime"]["duration_hours"])
        
        logger.info(f"🕐 Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🕐 End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        # Start background tasks
        checkpoint_task = asyncio.create_task(self.periodic_checkpoint())
        stats_task = asyncio.create_task(self.periodic_stats_report())
        
        async with aiohttp.ClientSession() as session:
            while self.should_continue():
                # Get batch of URLs to process
                batch_size = min(
                    self.config["crawling"]["max_concurrent_requests"] * 2,
                    len(self.urls_to_visit)
                )
                
                if batch_size == 0:
                    break
                
                # Get URLs from queue
                urls_batch = []
                for _ in range(batch_size):
                    if self.urls_to_visit:
                        urls_batch.append(self.urls_to_visit.pop())
                
                # Process batch concurrently
                tasks = [self.process_url(session, url) for url in urls_batch]
                await asyncio.gather(*tasks, return_exceptions=True)
        
        # Cleanup
        self.running = False
        checkpoint_task.cancel()
        stats_task.cancel()
        
        # Final checkpoint and stats
        await self.save_checkpoint()
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 CRAWLING COMPLETE!")
        self.stats.report()
        
        # Save final statistics
        try:
            async with aiofiles.open(self.config["output"]["stats_file"], 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.stats.to_dict(), indent=2))
        except Exception as e:
            logger.error(f"Error saving final stats: {e}")


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced AI Data Collector')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--duration', type=float, help='Override duration in hours')
    
    args = parser.parse_args()
    
    # Check dependencies
    try:
        import aiohttp
        import aiofiles
        import bs4
    except ImportError:
        print("❌ Missing dependencies. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    collector = EnhancedDataCollector(config_path=args.config)
    
    # Override duration if specified
    if args.duration:
        collector.config["runtime"]["duration_hours"] = args.duration
    
    await collector.run(resume=args.resume)


if __name__ == "__main__":
    asyncio.run(main())