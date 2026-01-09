import scrapy

class DentalScraperItem(scrapy.Item):
    clinic_name = scrapy.Field()
    phone_number = scrapy.Field()
    address = scrapy.Field()
    email = scrapy.Field()
    website_url = scrapy.Field()
    place_url = scrapy.Field()  # For debugging/reference
