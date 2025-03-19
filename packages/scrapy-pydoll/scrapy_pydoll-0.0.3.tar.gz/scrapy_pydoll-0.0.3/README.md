# scrapy-pydoll

A Scrapy download handler that integrates [pydoll-python](https://pypi.org/project/pydoll-python/) for handling JavaScript-rendered pages in Scrapy spiders.

## Installation

```bash
pip install scrapy-pydoll
```

## Requirements

- Python >= 3.12
- scrapy >= 2.12.0 
- pydoll-python >= 1.3.2

## Usage

1. Configure the download handler in your Scrapy settings:

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_pydoll.handler.PydollDownloadHandler",
    "https": "scrapy_pydoll.handler.PydollDownloadHandler"
}

# Required for async support
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
```

2. Enable Pydoll for specific requests by setting `pydoll=True` in the request meta:

```python
import scrapy
from scrapy_pydoll.page import PageMethod
from pydoll.constants import By

class MySpider(scrapy.Spider):
    name = "myspider"
    
    def start_requests(self):
        url = "https://example.com"
        yield scrapy.Request(
            url,
            meta={
                "pydoll": True,
                "pydoll_page_methods": [
                    PageMethod("wait_element", By.XPATH, "//div[@class='content']"),
                ]
            }
        )
```

## Configuration

The following settings can be configured in your Scrapy settings:

- `PYDOLL_HEADLESS` (bool): Run Chrome in headless mode (default: `True`)
- `PYDOLL_PROXY` (str): Proxy server URL (default: `None`) 
- `PYDOLL_MAX_PAGES` (int): Maximum number of concurrent browser pages (default: `4`)
- `PYDOLL_NAVIGATION_TIMEOUT` (int): Page navigation timeout in seconds (default: `60`)

## Features

- Handles JavaScript-rendered pages using Chrome DevTools Protocol
- Supports custom page methods via `PageMethod` class
- Configurable concurrent page limits
- Proxy support
- Detailed logging and statistics

## Example

Here's a complete spider example that scrapes quotes from a JavaScript-rendered page:

```python
import scrapy
from scrapy_pydoll.page import PageMethod
from pydoll.constants import By

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        url = "http://quotes.toscrape.com/js/"
        yield scrapy.Request(
            url,
            meta={
                "pydoll": True,
                "pydoll_page_methods": [
                    PageMethod("wait_element", By.XPATH, "//div[@class='quote']"),
                ]
            }
        )

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            yield {
                "text": quote.xpath(".//span[@class='text']/text()").get(),
                "author": quote.xpath(".//small[@class='author']/text()").get(),
            }
```

## License

This project is licensed under the MIT License.