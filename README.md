# yelp_parser
Parsing Yelp business pages with Scrapy

First, make sure the dependencies are installed:
1. Scrapy: https://github.com/scrapy/scrapy
2. Splash (for loading JavaScript content): https://splash.readthedocs.io/en/stable/install.html
3. scrapy-splash (so that Splash works with Scrapy): https://github.com/scrapy-plugins/scrapy-splash

Before running the script:
1. Start Splash container in Docker: https://splash.readthedocs.io/en/stable/install.html
2. In yelp/settings.py, set SPLASH_URL to the address and port where Splash is available.

Running the script:
1. Run yelp/spiders/yelp_script.py.
2. Enter business url.
3. Output is saved as a json file in the same folder as the script.
4. If you run the script again, ReactorNotRestartable error will be raised. To run the parser again, simply restart kernel where script was executed.

What parser does:
- Scrapes the following data:
  - name
  - business_page
  - business_id
  - img
  - phone
  - address
  - avg_rating
  - num_reviews
  - categories
  - website
  - schedule
  - about
  - amenities
- Address is scraped as-is without diving it into street, city, state, etc. because there's each business fills this field differently.
- None of the pages contained email field and so it's not scraped.
- Splash is used to access dynamically loaded content (Amenities and More and About the Business).
- Parser also handles pages where Amenities and More and About the Business sections are not expandable (like on this page: https://www.yelp.com/biz/heises-plumbing-san-francisco)

3 sample output json files are available in yelp/spiders/.
