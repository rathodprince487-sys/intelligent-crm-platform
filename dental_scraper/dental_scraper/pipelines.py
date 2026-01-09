from itemadapter import ItemAdapter

class DentalScraperPipeline:
    def __init__(self):
        self.seen_phones = set()
        self.seen_names = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Normalize fields
        if adapter.get('clinic_name'):
            adapter['clinic_name'] = adapter['clinic_name'].strip()
            
        if adapter.get('phone_number'):
            # Basic cleaning
            adapter['phone_number'] = adapter['phone_number'].replace(" ", "").replace("-", "")

        # Deduplication
        phone = adapter.get('phone_number')
        name = adapter.get('clinic_name')
        
        # 1. Check Phone (Strong Signal)
        if phone:
            if phone in self.seen_phones:
                from scrapy.exceptions import DropItem
                raise DropItem(f"Duplicate item found with phone: {phone}")
            self.seen_phones.add(phone)
            
        # 2. Check Name (Weak Signal, but useful if phone is missing)
        # Note: We only check name if we haven't already dropped it by phone, 
        # but realistically valid business might lack phone.
        elif name:
             if name in self.seen_names:
                 from scrapy.exceptions import DropItem
                 raise DropItem(f"Duplicate item found with name: {name}")
             self.seen_names.add(name)
            
        return item
