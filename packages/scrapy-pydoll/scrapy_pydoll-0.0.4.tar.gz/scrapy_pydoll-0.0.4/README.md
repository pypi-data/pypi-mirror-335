# scrapy-pydoll

A Scrapy Download Handler which performs requests using [Pydoll](https://pypi.org/project/pydoll-python/). It can be used to handle pages that require JavaScript (among other things), while adhering to the regular Scrapy workflow (i.e. without interfering with request scheduling, item processing, etc).


## Requirements

- Python >= 3.12
- Scrapy >= 2.0 (!= 2.4.0)
- Pydoll-python >= 1.3.3
- Google Chrome

## Installation

```bash
pip install scrapy-pydoll
```

## Basic Configuration

Add the following to your Scrapy project's settings:

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_pydoll.handler.PydollDownloadHandler",
    "https": "scrapy_pydoll.handler.PydollDownloadHandler"
}

# Required for async support
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
```

## Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `PYDOLL_HEADLESS` | bool | `True` | Run Chrome in headless mode |
| `PYDOLL_PROXY` | str | `None` | Proxy server URL (e.g. "http://proxy:8080") |
| `PYDOLL_MAX_PAGES` | int | `4` | Maximum number of concurrent browser pages |
| `PYDOLL_NAVIGATION_TIMEOUT` | int | `30` | Page navigation timeout in seconds |
| `PYDOLL_ABORT_REQUEST` | str | `None` | Resource type to block (e.g. "image", "stylesheet", "script") |

## Usage Examples

### Basic Usage

```python
import scrapy
from scrapy_pydoll.page import PageMethod
from pydoll.constants import By

class MySpider(scrapy.Spider):
    name = "myspider"
    
    def start_requests(self):
        yield scrapy.Request(
            "https://example.com",
            meta={"pydoll": True}  # Enable Pydoll for this request
        )
```

### Wait for Elements

```python
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

### Take Screenshots

```python
yield scrapy.Request(
    url,
    meta={
        "pydoll": True,
        "pydoll_page_methods": [
            PageMethod("get_screenshot", "output.png"),
        ]
    }
)
```

### Block Resource Types

To block specific resource types (like images or scripts), use the `PYDOLL_ABORT_REQUEST` setting:

```python
# In your settings.py
PYDOLL_ABORT_REQUEST = "image"  # Blocks all image requests
```

### Complete Example

Here's a complete spider example that scrapes a JavaScript-rendered website:

```python
import scrapy
from scrapy_pydoll.page import PageMethod
from pydoll.constants import By

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        yield scrapy.Request(
            "http://example.com/js/",
            meta={
                "pydoll": True,
                "pydoll_page_methods": [
                    PageMethod("wait_element", By.XPATH, "//div[@class='quote']"),
                    PageMethod("get_screenshot", "quotes.png"),
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


# Supported Pydoll methods
Refer to the [upstream docs for the `Page` class](https://github.com/autoscrape-labs/pydoll?tab=readme-ov-file#page-interface)
to see available methods.