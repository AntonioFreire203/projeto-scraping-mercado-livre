import scrapy
from datetime import datetime
import re
from typing import List, Dict, Any


class NetshoesSpider(scrapy.Spider):
    name:str = "netshoes"
    allowed_domains: List[str] = ["www.netshoes.com.br"]
    start_urls: List[str] = ["https://www.netshoes.com.br/running/tenis-performance?genero=masculino"]
    page_count: int = 1
    max_pages: int = 10

    def parse(self, response)  :
        # Pegue os links 
        product_links: List[str] = response.css('div.card a::attr(href)').getall()

        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

        # Verifica se deve continuar para a próxima página
        if self.page_count < self.max_pages:
            self.page_count += 1
            next_page = f"https://www.netshoes.com.br/running/tenis-performance?genero=masculino&page={self.page_count}"
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_product(self, response)  :
        
        product_attributes = response.css('ul.features--attributes li')
        
        if product_attributes:
            brand_element:str = product_attributes[-1]
            brand:str = brand_element.css('a::text').get()
        else:
            brand_name_list: List[str] = response.css('h1.product-name::text').get().split()
            if brand_name_list[1] == 'Masculino':
                brand = brand_name_list[2]
            else:
                brand = brand_name_list[1]

        yield {
            'brand': brand,
            'name': response.css('h1.product-name::text').get(),
            'new_price_reais': response.css('div.price-box__saleInCents span.saleInCents-value::text').get().strip(),
            'reviews_rating_number': response.css('div[aria-label="Avaliações"] div[aria-label="Média"]::text').get().strip(),
            'reviews_amount': response.css('p[aria-label="Número de reviews"]::text').get().strip(),
            'page_count': self.page_count,
            '_source_name': self.name,
            '_source_link': self.start_urls[0],
            '_data_coleta': datetime.now()
        }
    
