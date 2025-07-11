# coding: utf-8

import logging
import scrapy


class WebDirectorySpider(scrapy.Spider):
    name = "web_directory_spider"

    def __init__(self, url, *args, **kwargs):
        self.start_url = url
        self.start_urls = [url]
        super(WebDirectorySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        url = response.url
        logging.info(f"Parsing URL: {url}")
        if not url.startswith(self.start_url):
            # Skipping not child url
            return

        collection = {}
        if self.collection_name:
            collection[self.collection_key if self.collection_key else "name"] = self.collection_name

        assets = []
        links = []

        if url.endswith("/"):
            rows = response.css("table > tr")
            for row in rows:
                link_td = row.css("td > a[href]")
                if not link_td:
                    # Skipping header
                    continue

                link = link_td[0].attrib["href"]
                if link.startswith("/"):
                    # Skipping parent relative link
                    continue

                if not link.startswith("http"):
                    # If the link is relative, make it absolute.
                    link = url.rstrip("/") + "/" + link.lstrip("/")

                if link.endswith("/"):
                    # Building a list of links to crawl
                    links.append(link)
                else:
                    cells = row.css("td")
                    if cells:
                        # Push the extracted data to the default dataset.
                        assets.append(
                            {
                                "url": link,
                                "modified": cells[self.modified_col]
                                .css("::text")
                                .get()
                                .strip(),
                                "size": cells[self.size_col]
                                .css("::text")
                                .get()
                                .strip(),
                            }
                        )
                for link in links:
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse,
                    )

        if assets:
            collection["url"] = url
            collection["assets"] = assets
            yield collection
