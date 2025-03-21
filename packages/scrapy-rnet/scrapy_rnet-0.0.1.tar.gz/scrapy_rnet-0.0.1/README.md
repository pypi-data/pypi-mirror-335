# scrapy-rnet

A Scrapy download handler that enables browser TLS fingerprint impersonation using the [`rnet`](https://github.com/0x676e67/rnet) library.

## Features

- Seamlessly integrates with Scrapy's download system
- Impersonates browser TLS signatures to evade detection
- Supports multiple browser versions for impersonation

## Installation

```bash
pip install scrapy-rnet
```

## Requirements

- Python 3.12+
- rnet >= 2.1.0
- scrapy >= 2.12.0

## Usage

### Basic Setup

1. Configure the download handlers in your Scrapy settings:

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_rnet.handler.ImpersonateDownloadHandler",
    "https": "scrapy_rnet.handler.ImpersonateDownloadHandler",
}
USER_AGENT = None

# Required for async operation
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
```

2. Enable impersonation for specific requests by adding `impersonate` to the request metadata:

```python
from rnet import Impersonate, ImpersonateOS

yield scrapy.Request(
    url="https://example.com",
    meta={
        "impersonate": Impersonate.Chrome132,
        "impersonate_os": ImpersonateOS.Windows # Optional
    },
    callback=self.parse
)
```

### Example Spider

```python
import scrapy
from scrapy.http import Request, Response
from rnet import Impersonate, ImpersonateOS

class BrowserImpersonationSpider(scrapy.Spider):
    name = "browser_impersonation"
    
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_rnet.handler.ImpersonateDownloadHandler",
            "https": "scrapy_rnet.handler.ImpersonateDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "USER_AGENT": None
    }
    
    def start_requests(self):
        urls = [
            "https://example.com",
            "https://httpbin.org/headers"
        ]
        
        for url in urls:
            yield Request(
                url=url,
                meta={
                    "impersonate": Impersonate.Chrome132,
                    "impersonate_os": ImpersonateOS.Windows # Optional
                },
                callback=self.parse
            )
    
    def parse(self, response):
        yield {
            "url": response.url,
            "status": response.status,
            "flags": response.flags
        }
```

## Available Impersonation Options

The package supports a wide range of browser versions and operating systems:

### Browser Versions

| **Browser**   | **Versions**                                                                                     |
|---------------|--------------------------------------------------------------------------------------------------|
| **Chrome**    | `Chrome100`, `Chrome101`, `Chrome104`, `Chrome105`, `Chrome106`, `Chrome107`, `Chrome108`, `Chrome109`, `Chrome114`, `Chrome116`, `Chrome117`, `Chrome118`, `Chrome119`, `Chrome120`, `Chrome123`, `Chrome124`, `Chrome126`, `Chrome127`, `Chrome128`, `Chrome129`, `Chrome130`, `Chrome131`, `Chrome132`, `Chrome133`, `Chrome134` |
| **Edge**      | `Edge101`, `Edge122`, `Edge127`, `Edge131`, `Edge134`                                                       |
| **Safari**    | `SafariIos17_2`, `SafariIos17_4_1`, `SafariIos16_5`, `Safari15_3`, `Safari15_5`, `Safari15_6_1`, `Safari16`, `Safari16_5`, `Safari17_0`, `Safari17_2_1`, `Safari17_4_1`, `Safari17_5`, `Safari18`, `SafariIPad18`, `Safari18_2`, `Safari18_1_1`, `Safari18_3`, `Safari18_3_1` |
| **OkHttp**    | `OkHttp3_9`, `OkHttp3_11`, `OkHttp3_13`, `OkHttp3_14`, `OkHttp4_9`, `OkHttp4_10`, `OkHttp4_12`, `OkHttp5`         |
| **Firefox**   | `Firefox109`, `Firefox117`, `Firefox128`, `Firefox133`, `Firefox135`, `FirefoxPrivate135`, `FirefoxAndroid135`, `Firefox136`, `FirefoxPrivate136`|


### Operating Systems
- `Windows`
- `MacOS`
- `Linux`
- `Android`
- `IOS`


## Credits

[0x676e67](https://github.com/0x676e67) for [Rnet](https://github.com/0x676e67/rnet)