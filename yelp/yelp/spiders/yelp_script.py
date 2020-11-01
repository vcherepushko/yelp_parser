import scrapy
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class YelpSpider(scrapy.Spider):    
    name = 'yelp'
    allowed_domains = ['yelp.com']
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'
    
    # Splash script that expands Amenities and About sections
    script = '''
        function main(splash, args)
          splash.private_mode_enabled = false
          url = args.url
          assert(splash:go(url))
          assert(splash:wait(1))
          amenities = splash:select('section > div > div.lemon--div__373c0__1mboc.border-color--default__373c0__3-ifU + a.lemon--a__373c0__IEZFH.link__373c0__1G70M.link-color--blue-dark__373c0__85-Nu.link-size--default__373c0__7tls6')
          if amenities ~= nil then
            amenities:click()
          end
          assert(splash:wait(1))
          about = splash:select('section.lemon--section__373c0__fNwDM.margin-t4__373c0__1TRkQ.padding-t4__373c0__3hVZ3.border--top__373c0__3gXLy.border-color--default__373c0__3-ifU > div.lemon--div__373c0__1mboc.border-color--default__373c0__3-ifU > button.button__373c0__3lYgT.secondary__373c0__1bsQo')
          if about ~= nil then
            about:click()
          end
          assert(splash:wait(1))
          splash:set_viewport_full()
          return splash:html()
        end
    '''

    def __init__(self, *args, **kwargs):
        super(YelpSpider, self).__init__(*args, **kwargs)
        self.business_url = kwargs.get('business_url')

    def start_requests(self):
        yield SplashRequest(self.business_url, 
                            callback=self.parse, 
                            endpoint="execute", 
                            args={'lua_source': self.script}, 
                            headers={'User-Agent': self.user_agent}
        )

    def parse(self, response):
        name = response.xpath('//h1[@class="lemon--h1__373c0__2ZHSL heading--h1__373c0__dvYgw undefined heading--inline__373c0__10ozy"]/text()').get()
        business_page = response.url
        business_id = business_page.split('/')[-1]
        img = response.xpath('//div[@class="lemon--div__373c0__1mboc photoHeader__373c0__YdvQE border-color--default__373c0__3-ifU"]/div/div/div[1]/a/img/@src').get()
        phone = response.xpath('//div[@class="lemon--div__373c0__1mboc css-1vhakgw border--top__373c0__3gXLy border-color--default__373c0__3-ifU"][2]/div/div[@class="lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-fill__373c0__3Sfw1 border-color--default__373c0__3-ifU"]/p[2]/text()').get()
        
        address = response.xpath('//address/p/span/text()').getall()
        
        avg_rating = response.xpath('//div[@class="lemon--div__373c0__1mboc arrange__373c0__2C9bH gutter-1-5__373c0__2vL-3 vertical-align-middle__373c0__1SDTo margin-b1__373c0__1khoT border-color--default__373c0__3-ifU"]/div/span/div/@aria-label').get().split()[0]
        num_reviews = response.xpath('//div[@class="lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-fill__373c0__3Sfw1 border-color--default__373c0__3-ifU"]/div[2]/div/p/text()').get().split()[0]
        categories = response.xpath('//span[@class="lemon--span__373c0__3997G display--inline__373c0__3JqBP margin-r1__373c0__zyKmV border-color--default__373c0__3-ifU"]/span/a/text()').getall()
        website = response.xpath('//div[@class="lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-fill__373c0__3Sfw1 border-color--default__373c0__3-ifU"]/p[2]/a/text()').get()
        
        days = response.xpath('//table[@class="lemon--table__373c0__2clZZ hours-table__373c0__1S9Q_ table__373c0__3JVzr table--simple__373c0__3lyDA"]/tbody/tr/th/p/text()').getall()
        hours = response.xpath('//li[@class="lemon--li__373c0__1r9wz border-color--default__373c0__3-ifU"]/p/text()').getall()
        schedule = list(zip(days, hours)) 
        
        about_spec_hist = response.xpath('//p[@class="lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa- text-display--paragraph__373c0__1t3BO text-size--large__373c0__3t60B"]/text()').getall()
        about_manager = response.xpath('//p[@class="lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa- text-display--paragraph__373c0__1t3BO text-size--large__373c0__3t60B"]/span/text()').getall()
        about = '\n'.join(about_spec_hist + about_manager)

        amenities = response.xpath('//div[@class="lemon--div__373c0__1mboc arrange__373c0__2C9bH gutter-2__373c0__1DiLQ layout-wrap__373c0__1as1X layout-2-units__373c0__38itL border-color--default__373c0__3-ifU"]/div/div/div/span/text()').getall()

        yield {
            "name": name,
            "business_page": business_page,
            "business_id": business_id,
            "img": img,
            "phone": phone,
            "address": address,
            "avg_rating": avg_rating,
            "num_reviews": num_reviews,
            "categories": categories,
            "website": website,
            "schedule": schedule,
            "about": about,
            "amenities": amenities
        }


if __name__ == "__main__":
    input_url = input('Enter a business url: ')
    business_id = input_url.split('/')[-1] # This is used to name an output json file
    
    settings = get_project_settings()
    
    # Set output settings
    settings.update({
        'FEEDS': {
            f'{business_id}.json': {'format': 'json'}
        }
    })

    process = CrawlerProcess(settings)
    process.crawl(YelpSpider, business_url=input_url)
    process.start()