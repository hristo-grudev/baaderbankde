import scrapy

from scrapy.loader import ItemLoader

from ..items import BaaderbankdeItem
from itemloaders.processors import TakeFirst


class BaaderbankdeSpider(scrapy.Spider):
	name = 'baaderbankde'
	start_urls = ['https://www.baaderbank.de/Investor-Relations/Presseinformationen-Archiv-232']

	def parse(self, response):
		post_links = response.xpath('//div[@class="teaser-item clearfix"]')
		for post in post_links:
			url = post.xpath('.//a[@class="btn btn-primary right pull-right"]/@href').get()
			date = post.xpath('.//div[@class="date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[text()="»"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="news-content"]//h2/text()').get()
		description = response.xpath('//div[@class="news-content"]//text()[normalize-space() and not(ancestor::h2)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BaaderbankdeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
