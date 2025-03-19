import scrapy
import re
import gzip
import requests
from io import BytesIO
from django.conf import settings


class SitemapSpider(scrapy.Spider):
    name = 'sitemaps'
    start_urls = ['https://www.mindbodyonline.com/sitemap_index.xml']

    def parse(self, response):
        sitemap_urls = re.findall(r'<loc>(.*?)</loc>', response.text)

        for sitemap_url in sitemap_urls:
            if sitemap_url.endswith('.gz'):
                yield scrapy.Request(sitemap_url, callback=self.parse_gzip)
            else:
                yield scrapy.Request(sitemap_url, callback=self.parse_xml)

    def parse_xml(self, response):
        filename = self.sanitize_url(response.url) + '.xml'
        with open(filename, 'wb') as f:
            f.write(response.body)

    def parse_gzip(self, response):
        
        # Decompress the gzipped content
        uncompressed_data = gzip.decompress(response.body)
        
        # Convert the bytes to a string
        uncompressed_string = uncompressed_data.decode('utf-8')
        
        # Extract sitemap URLs from the uncompressed content
        sitemap_urls = re.findall(r'<loc>(.*?)</loc>', uncompressed_string)

        for sitemap_url in sitemap_urls:
            response = requests.get(sitemap_url)
            if response.status_code == 200:
                # Decompress the gzipped content
                with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as gz:
                    # Process the decompressed content
                    with open(settings.BASE_DIR/f'sitemaps/{self.sanitize_url(sitemap_url)}.xml', 'wb') as f:
                        f.write(gz.read())
                           
 
            

    def sanitize_url(self, url):
        return re.sub(r'[^a-zA-Z0-9]', '_', url)
    

    
