# 5. spiders/link_spider.py
# coding: utf-8
import logging
import scrapy
from urllib.parse import urljoin, urlparse
import mimetypes
import os

class LinkSpider(scrapy.Spider):
    name = "link_spider"
    
    DOWNLOADABLE_EXTENSIONS = {
        '.pdf', '.csv', '.html', '.htm', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.txt', '.zip', '.rar', '.tar', '.gz', '.json',
        '.xml', '.mp3', '.mp4', '.avi', '.mov', '.jpg', '.jpeg', '.png',
        '.gif', '.svg', '.sql', '.db'
    }

    def __init__(self, url, *args, **kwargs):
        self.start_url = url
        self.start_urls = [url]
        self.base_domain = urlparse(url).netloc
        self.visited_urls = set()
        self.downloadable_files = []
        super(LinkSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        current_url = response.url
        logging.info(f"Parsing URL: {current_url}")

        if current_url in self.visited_urls:
            return
        self.visited_urls.add(current_url)

        if urlparse(current_url).netloc != self.base_domain:
            return

        links = response.css('a[href]::attr(href)').getall()
        
        for link in links:
            # NOUVEAU : Filtrer les liens invalides
            if link.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
        
            absolute_url = urljoin(current_url, link)
            
            # NOUVEAU : Vérifier que l'URL est valide
            parsed = urlparse(absolute_url)
            if not parsed.scheme or not parsed.netloc:
                continue
        
            if absolute_url == current_url:
                continue
                
            if self._is_downloadable_file(absolute_url):
                yield scrapy.Request(
                    url=absolute_url,
                    method='HEAD',
                    callback=self._check_file_size,
                    meta={'file_url': absolute_url}
                )
            else:
                parsed_link = urlparse(absolute_url)
                if (parsed_link.netloc == self.base_domain and 
                    absolute_url not in self.visited_urls):
                    yield scrapy.Request(
                        url=absolute_url,
                        callback=self.parse
                    )

    def _is_downloadable_file(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        _, ext = os.path.splitext(path)
        if ext in self.DOWNLOADABLE_EXTENSIONS:
            return True
            
        mime_type, _ = mimetypes.guess_type(url)
        if mime_type:
            return not mime_type.startswith('text/html')
            
        return False

    def _check_file_size(self, response):
        file_url = response.meta['file_url']
        
        content_length = response.headers.get('Content-Length')
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        
        file_size = None
        if content_length:
            try:
                file_size = int(content_length.decode('utf-8'))
            except (ValueError, AttributeError):
                file_size = None

        file_info = {
            'url': file_url,
            'size_bytes': file_size,
            'size_human': self._format_file_size(file_size) if file_size else 'Unknown',
            'content_type': content_type,
            'source_page': response.request.headers.get('Referer', '').decode('utf-8') if response.request.headers.get('Referer') else self.start_url
        }
        
        logging.info(f"Found downloadable file: {file_url} ({file_info['size_human']})")
        yield file_info

    def _format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
