# TradingView Scraper
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/github/license/mnwato/tradingview-scraper.svg?color=brightgreen)](https://opensource.org/licenses/MIT)


This is a Python library for scraping ideas and indicators from [TradingView.com](https://www.tradingview.com). The goal is to develop this package to scrape anything on [TradingView.com](https://www.tradingview.com) with real-time responses.  
**Thanks to contributors!**


## To-Do List
- Export
  - [x] Export as a `CSV` file
  - [x] Export as `JSON`
- Scrape Symbol Subpages:
  - [x] [Ideas](https://www.tradingview.com/symbols/BTCUSD/ideas/)
  - [x] [Indicators](https://www.tradingview.com/symbols/BTCUSD/technicals/)
  - [ ] [Overview](https://www.tradingview.com/symbols/BTCUSD/)
  - [x] [News](https://www.tradingview.com/symbols/BTCUSD/news/)
  - [x] [Earning-calendar](https://in.tradingview.com/earnings-calendar/)
  - [ ] [Minds](https://www.tradingview.com/symbols/BTCUSD/minds/)
  - [x] [Technical](https://www.tradingview.com/symbols/BTCUSD/technicals/)
  - [ ] [Market](https://www.tradingview.com/symbols/BTCUSD/markets/)
  - [ ] [Screener](https://www.tradingview.com/screener/)
  - [x] Get 'OHLC', 'Indicators' using TradingView WebSocket
  - [x] Export historical OHLC candle and Indicator values
  
  Additional suggestions welcome!

### To be aware of the latest changes, go to the [end of this page](https://github.com/mnwato/tradingview-scraper#changes).

## Features

- **Idea page Scraping**
  - Title
  - Paragraph
  - Preview Image
  - Author
  - Comments Count
  - Boosts Count
  - Publication Datetime
  - Is Updated
  - Idea Strategy

- **News page Scraping**
  - Breadcrumbs
  - Title
  - Published datetime
  - Related symbols
  - Body
  - Tags

- **Webpage Scraping Options**
  - Scrape All Pages
  - Scrape a Specific Range of Pages

- **Indicator Extraction**
  - Extract values for indicators like `RSI`, `Stoch.K`, etc. 
  - [Full list of indicators](https://github.com/mnwato/tradingview-scraper/blob/dev/tradingview_scraper/indicators.txt)

- **Real-Time data Extraction**
  - OHLCV
  - Watchlist
  - Indicators

- **Export Formats**
  - CSV
  - JSON

- **Output Format**
  - Returns data in JSON format

Here’s a revised version of the Installation section that enhances clarity and encourages user engagement:


## Installation

To get started with the TradingView Scraper library, follow these simple steps:

1. **Open your terminal**: Launch your preferred command line interface.

2. **Install the package**: Run the following command to install the TradingView Scraper:
   ```sh
   pip install tradingview-scraper
   ```

3. **Upgrade if necessary**: If you already have the library installed and want to upgrade to the latest version, use:
   ```sh
   pip install --upgrade --no-cache tradingview-scraper
   ```

Here’s a revised version of the Examples section, focusing on clarity, ease of understanding, and providing essential information about default values:


## Examples

### 1. Fast Running (Default Parameters)
To quickly scrape ideas using default settings, use the following code:
```python
from symbols.ideas import Ideas

# Initialize the Ideas scraper with default parameters
ideas_scraper = Ideas()  # Default: export_result=False, export_type='json'
ideas = ideas_scraper.scrape()  # Default symbol: 'BTCUSD'
print("Ideas:", ideas)
```
**Default Parameters:**
- `export_result`: `False` (no file will be saved)
- `export_type`: `'json'` (output format)

### 2. Getting Ideas for a Specific Symbol, Export Type, and Pages
To scrape ideas for a specific symbol and export them as a CSV file, you can specify the parameters:
```python
from symbols.ideas import Ideas

# Initialize the Ideas scraper with custom parameters
ideas_scraper = Ideas(
  export_result=True,  # Set to True to save the results
  export_type='csv'    # Specify the export type (json or csv)
)

# Scrape ideas for the ETHUSD symbol, from page 1 to page 2
ideas = ideas_scraper.scrape(
  symbol="ETHUSD",
  startPage=1,
  endPage=2,
  sort="popular"  #  Could be 'popupar' or 'recent'
)
print("Ideas:", ideas)
```

**Output Format:**
The output will always be a list of Python dictionaries, structured as follows:
```json
[
  {
      "title": "Bitcoin -65% crash, ETH -83%, DOGE -89%, SHIBA -90%",
      "paragraph": "Name your altcoin in the comment section, and I will do a technical analysis for you!\n\nThe crypto market looks ...",
      "preview_image": "https://s3.tradingview.com/6/6VQphWH6_mid.png",
      "author": "Xanrox",
      "comments_count": "295",
      "boosts_count": "678",
      "publication_datetime": "2024-08-18T05:55:19.000Z",
      "is_updated": "True",
      "idea_strategy": "Short"
  }
]
```
- When `export_result=True`, the default `export_type` is `'json'`, and a JSON file will be saved in the `/export` directory. To save as CSV, set `export_type='csv'`.

### 3. Getting Indicators Status
To scrape the status of specific indicators, use the following code:
```python
from tradingview_scraper.symbols.technicals import Indicators

# Initialize the Indicators scraper with export options
indicators_scraper = Indicators(export_result=True, export_type='json')

# Scrape indicators for the BTCUSD symbol from the BINANCE exchange
indicators = indicators_scraper.scrape(
    exchange="BINANCE",
    symbol="BTCUSD",
    timeframe="1d",
    indicators=["RSI", "Stoch.K"]
)
print("Indicators:", indicators)
```

**Output:**
```json
{"RSI": "46.34926112", "Stoch.K": "40.40173723"}
```

### 4. Getting All Indicators
If you want to retrieve all available indicators for a symbol, set `allIndicators=True`:
```python
from tradingview_scraper.symbols.technicals import Indicators

# Scrape all indicators for the BTCUSD symbol
indicators_scraper = Indicators(export_result=True, export_type='json')
indicators = indicators_scraper.scrape(
    symbol="BTCUSD",
    timeframe="4h",
    allIndicators=True
)
print("All Indicators:", indicators)
```

### 5. Getting News Headlines/Content
```python
# Create an instance of the NewsScraper with export options
news_scraper = NewsScraper(export_result=True, export_type='json')

# Retrieve news headlines from a specific provider
news_headlines = news_scraper.scrape_headlines(
    symbol='BTCUSD',      # Uncomment and specify if needed
    exchange='BINANCE', # Uncomment and specify if needed
    # provider='newsbtc',  # Specify the news provider
    # area='world',  # Specify the geographical area
    # section='all',  # Specify the section of news
    sort='latest'
)

# Retrieve detailed news content for a specific story
news_content = news_scraper.scrape_news_content(
    story_path=news_headlines[0]['storyPath']  # Specify the story path from scraped headlines
)
```
- Retrieve news by symbol:
  - Both `symbol` and `exchange` are required parameters
- Filter result by:
  - `area`, `provider` and `section` can be specified to refine the news results.

#### Output (news headline):
```json
[
  {
    "breadcrumbs": "News > U.Today > Bitcoin ETFs Record Enormous Outflows",
    "title": "Bitcoin ETFs Record Enormous Outflows",
    "published_datetime": "Wed, 04 Sep 2024 07:55:38 GMT",
    "related_symbols": [
      {
        "name": "BTCUSDT",
        "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCUSDT.svg"
      }
    ],
    "body": ["""<List of text page content>"""],
    "tags": ["Crypto", "U.Today"]}
]
```
#### Output (news content):
```json
[
  {
    "id": "tag:reuters.com,2024:newsml_L1N3KM09S:0",
    "title": "Goldman Sachs sees biggest boost to US economy from Harris win",
    "provider": "reuters",
    "sourceLogoId": "reuters",
    "published": 1725443676,
    "source": "Reuters",
    "urgency": 2,
    "permission": "preview",
    "relatedSymbols": [
      {
        "symbol": "BITMEX:XBTETH.P",
        "currency-logoid": "country/US",
        "base-currency-logoid": "crypto/XTVCBTC"
      },
      {
        "symbol": "ICEUS:DXY",
        "logoid": "indices/u-s-dollar-index"
      }
    ],
    "storyPath": "/news/reuters.com,2024:newsml_L1N3KM09S:0-goldman-sachs-sees-biggest-boost-to-us-economy-from-harris-win/"
  }
]
```

### 6. Fetching Real-Time Trading Data
- The `RealTimeData` class offers functionality to fetch real-time trading data from various exchanges. This section provides usage examples demonstrating how to retrieve the latest trade information and OHLCV (Open, High, Low, Close, Volume) data.

#### Retrieve OHLCV Data:
- **Timestamp**
- **Open**
- **High**
- **Low**
- **Close**
- **Volume**
##### Example:
#### Method 1: Simple OHLCV Retrieval
This method is straightforward and streams only OHLC data.
```python
from tradingview_scraper.symbols.stream import RealTimeData
# Create an instance of the RealTimeData class
real_time_data = RealTimeData()

# Retrieve OHLCV data for a specific symbol
data_generator = real_time_data.get_ohlcv(exchange_symbol="BINANCE:BTCUSDT")
```
#### Method 2: Streaming OHLC and Indicators Simultaneously
- Streams both OHLC data and indicators
- Exports historical data in specific timeframe (price candles and indicator history).
- Specifies the number of OHLCV historical candles to export.
- Requires JWT token for indicator access.
```python
from tradingview_scraper.symbols.stream import Streamer
# Create an instance of the Streamer class
streamer = Streamer(
    export_result=False,
    export_type='json',
    websocket_jwt_token="Your-Tradingview-Websocket-JWT"
    )

data_generator = streamer.stream(
    exchange="BINANCE",
    symbol="BTCUSDT",
    timeframe="4h",
    numb_price_candles=100,
    indicator_id="STD;RSI",
    indicator_version="31.0"
    )
```
#### Important Notes
- **Export Historical Data**: Set `export_result=True` if only historical data is needed. (returns json instead of generator)
- **Stream Only OHLCV**: Do not include `indicator_id` or `indicator_version`.

#### Indicator Search
- For assistance in finding your preferred indicator, visit: [TradingView Indicator Search](https://www.tradingview.com/pubscripts-suggest-json/?search=rsi).


#### Retrieve Watchlist Market Info
  - You can send a list of exchange:symbol to get real-time market information, including:
  - volume
  - `lp_time` (Last Price Time)
  - `lp` (Last Price)
  - `ch` (Change in Price)
  - `chp` (Change in Percent)
##### Example:
```python
from tradingview_scraper.symbols.stream import RealTimeData
# Create an instance of the RealTimeData class
real_time_data = RealTimeData()

# Define the exchange symbols for which to fetch data
exchange_symbol = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "FXOPEN:XAUUSD"]

# Retrieve the latest trade information for a specific symbol
data_generator = real_time_data.get_latest_trade_info(exchange_symbol=exchange_symbol)
```

#### Printing Results
- To display the real-time data packets, iterate over the generator as follows:
```python
for packet in data_generator:
    print('-' * 50)
    print(packet)
```
#### Output Examples
##### Output (OHLCV):
```text
{'m': 'du', 'p': ['cs_qgmbtglzdudl', {'sds_1': {'s': [{'i': 9, 'v': [1734082440.0, 100010.0, 100010.01, 100006.27, 100006.27, 1.3242]}], 'ns': {'d': '', 'indexes': 'nochange'}, 't': 's1', 'lbs': {'bar_close_time': 1734082500}}}]}
```
##### Output (Watchlist market info):
```text
{'m': 'qsd', 'p': ['qs_folpuhzgowtu', {'n': 'BINANCE:BTCUSDT', 's': 'ok', 'v': {'volume': 6817.46425, 'lp_time': 1734082521, 'lp': 99957.9, 'chp': -0.05, 'ch': -46.39}}]}
```

### 7. Getting Calendar events

#### Scraping Earnings events
```python
from tradingview_scraper.symbols.cal import CalendarScraper

calendar_scraper = CalendarScraper()

# Scrape earnings from all markets.
res = calendar_scraper.scrape_earnings(
  values=["logoid", "name", "earnings_per_share_fq"]
)


# Scrape upcoming week earnings from the american market
from datetime import datetime, timedelta

timestamp_now = datetime.now().timestamp()
timestamp_in_7_days = (datetime.now() + timedelta(days=7)).timestamp()

res = calendar_scraper.scrape_earnings(
  timestamp_now,
  timestamp_in_7_days,
  ["america"],
  values=["logoid", "name", "earnings_per_share_fq"]
  )
```

#### Scraping Dividend events
```python
from tradingview_scraper.symbols.cal import CalendarScraper

calendar_scraper = CalendarScraper()

# Scrape dividends from all markets.
res = calendar_scraper.scrape_dividends(
  values=["logoid", "name", "dividends_yield"]
)


# Scrape upcoming week dividends from the american market
from datetime import datetime, timedelta

timestamp_now = datetime.now().timestamp()
timestamp_in_7_days = (datetime.now() + timedelta(days=7)).timestamp()

res = calendar_scraper.scrape_dividends(
  timestamp_now,
  timestamp_in_7_days,
  ["america"],
  values=["logoid", "name", "dividends_yield"]
  )
```

## Changes:
- Release `0.4.8`:
  Fix bug while fetching ADX+DI indicators
  Add timeframe param for streamer export data
- Release `0.4.7`:
  Fix bug undefined RealTimeData class
- Release `0.4.6`:
  Add value argument to specify calander fields
  Add Streamer class for getting OHLCV and indicator simultaneously
  Integrate realtime data and historical exporter into Streamer class
- Release `0.4.2`:
  Add calander (Dividend, Earning)
  Make requirements non-explicit
  Lint fix
  Add tests (ideas, realtime_price, indicators)
  Add reconnection method for realtime price scraper
- Release `0.4.0`:
  Update exchange list
  Add real-time price streaming
- Release `0.3.2`:  
  Support timeframe to get Indicators
- Release `0.3.0`:   
  Add news scraper
- Release `0.2.9`:   
  Refactor for new TradingView structure
- Release `0.1.0`:  
  The name of `ClassA` changed to `Ideas`

## License:
```
[MIT]
```
