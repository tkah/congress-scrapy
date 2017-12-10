# US Congressional Bill and Member Scrapers

Two scrapers that output [Congressional Bill data](https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS) and Congressional Member data ([house](http://clerk.house.gov/xml/lists/MemberData.xml), [senate](https://www.senate.gov/general/contact_information/senators_cfm.xml)) to a Postgres database. Scrapers written using [Scrapy](https://scrapy.org/) following [this tutorial](http://newcoder.io/scrape/intro/).

## Running

* Install the python dependencies: `pip install -r requirements.txt`
* Create a `settings.py` file in the following directories - `bill_scraper/scraper_app/` and `member_scraper/scraper_app/`.
   * `bill_scraper/scraper_app/settings.py`:
     ```python
        BOT_NAME = 'congressionalbills'
        SPIDER_MODULES = ['scraper_app.spiders']
        DATABASE = {
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': '[YOUR POASTGRES USER]',
            'password': '[YOUR POSTGRES PASSWORD]',
            'database': '[YOUR POASTGRES DB]'
        }
        ITEM_PIPELINES = { 'scraper_app.pipelines.BillPipeline': 200 }
        CONGRESS = '[YOUR CONGRESS NUMBER]'
     ```
   * `member_scraper/scraper_app/settings.py`:
     ```python
        BOT_NAME = 'congressionalmembers'
        SPIDER_MODULES = ['scraper_app.spiders']
        DATABASE = {
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': '[YOUR POASTGRES USER]',
            'password': '[YOUR POSTGRES PASSWORD]',
            'database': '[YOUR POASTGRES DB]'
        }
        ITEM_PIPELINES = { 'scraper_app.pipelines.MemberPipeline': 200 }
     ```
* Run each pipeline from within its respective directory - `bill_scraper` or `member_scraper`.
* Bill Scraper command: `scrapy crawl congressionalbills`
* Member Scraper command: `scrapy crawl congressionalmembers`