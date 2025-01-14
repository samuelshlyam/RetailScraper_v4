from bs4 import BeautifulSoup


class ProductSchema:
    def __init__(self, product_schemas, source):
        self.product_schemas = product_schemas
        self.source = source
        self.parsed_products = self.parse_product_schemas(self.product_schemas)

    def get_parsed_products(self):
        return self.parsed_products

    def parse_product_schemas(self, product_schemas):
        parsed_products = []

        for schema in product_schemas:
            if schema.get('@type') == 'Product':
                offers_info = self.extract_offers(schema)
                for offer in offers_info:

                    if (offer.get('@type') == 'Offer'):
                        prices = self.get_prices(offer)
                        currency = self.get_currency(offer)
                        seller = self.get_seller(offer)
                        description = self.get_description(offer)
                        title = self.get_title(offer)
                        images = self.get_images(offer)
                        url = self.get_url(offer)
                        product_details = self.create_product_details(title, images, prices, currency, url, description,
                                                                      seller, schema)
                        parsed_products.append(product_details)

                    elif (offer.get('@type') == 'AggregateOffer'):
                        for suboffer in self.extract_offers(offer):
                            prices = self.get_prices(suboffer)
                            currency = self.get_currency(suboffer)
                            seller = self.get_seller(suboffer)
                            description = self.get_description(suboffer)
                            title = self.get_title(suboffer)
                            images = self.get_images(suboffer)
                            url = self.get_url(suboffer)
                            product_details = self.create_product_details(title, images, prices, currency, url,
                                                                          description, seller, schema)
                            parsed_products.append(product_details)
        return parsed_products

    def get_title(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() not in ['seller', 'brand']:
                    if key == 'name':
                        return value
                    else:
                        result = self.get_title(value)
                        if result:
                            return result
        else:
            return None

    def get_images(self, data):
        images = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'image' and isinstance(value, (list, str)):
                    if isinstance(value, list):
                        images.extend(value)
                    else:
                        images.append(value)
                else:
                    images.extend(self.get_images(value))
        elif isinstance(data, list):
            for item in data:
                images.extend(self.get_images(item))
        return images

    def get_prices(self, data):
        prices = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ['price', 'lowprice', 'highprice'] and isinstance(value, str):
                    prices.append(value.replace("$", "").replace(",", "").replace(" ", ""))
                elif key.lower() in ['price', 'lowprice', 'highprice'] and isinstance(value, (int, float)):
                    prices.append(value)
                else:
                    prices.extend(self.get_prices(value))
        elif isinstance(data, list):
            for item in data:
                prices.extend(self.get_prices(item))
        return prices

    def get_currency(self, data):
        if isinstance(data, dict):
            currency = data.get('priceCurrency', None)
            if currency:
                return currency
            for value in data.values():
                result = self.get_currency(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.get_currency(item)
                if result:
                    return result

    def get_url(self, data):
        if self.source == "modesens":
            if isinstance(data, dict):
                url = data.get('url', None)
                if url:
                    return f"https://modesens.com{url}"
                for value in data.values():
                    result = self.get_url(value)
                    if result:
                        return f"https://modesens.com{url}"
            elif isinstance(data, list):
                for item in data:
                    result = self.get_url(item)
                    if result:
                        return f"https://modesens.com{url}"
        else:
            if isinstance(data, dict):
                url = data.get('url', None)
                if url:
                    return f"{url}"
                for value in data.values():
                    result = self.get_url(value)
                    if result:
                        return f"{url}"
            elif isinstance(data, list):
                for item in data:
                    result = self.get_url(item)
                    if result:
                        return f"{url}"

    def get_description(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'description':
                    return value
                else:
                    result = self.get_description(value)
                    if result:
                        return result

    def get_seller(self, data):
        if isinstance(data, dict):
            seller = data.get('seller', None)
            if isinstance(seller, dict) and 'name' in seller:
                return seller['name']
            for value in data.values():
                result = self.get_seller(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.get_seller(item)
                if result:
                    return result

    def extract_offers(self, data):
        offers = []

        if isinstance(data, dict):
            if 'offers' in data:
                # Directly append the offer or aggregate offer object
                offer_data = data['offers']
                if isinstance(offer_data, list):
                    offers.extend(offer_data)  # List of individual offers
                else:
                    offers.append(offer_data)  # Single or aggregate offer
            else:
                # Recursively search for offers in other dictionary values
                for value in data.values():
                    offers.extend(self.extract_offers(value))

        elif isinstance(data, list):
            # If the data is a list, apply the function to each element
            for item in data:
                offers.extend(self.extract_offers(item))

        return offers

    def create_product_details(self, title, images, prices, currency, url, description, seller, schema):
        product_details = {
            'title': title,
            'images': images,
            'prices': prices,
            'currency': currency,
            'url': url,
            'description': description,
            'seller': seller.lower() if seller else None
        }
        for key, value in product_details.items():
            if value in [None, [], "", {}]:
                if key == 'title':
                    product_details[key] = self.get_title(schema)
                elif key == 'images':
                    product_details[key] = self.get_images(schema)
                elif key == 'prices':
                    product_details[key] = self.get_prices(schema)
                elif key == 'currency':
                    product_details[key] = self.get_currency(schema)
                elif key == 'url':
                    product_details[key] = self.get_url(schema)
                elif key == 'description':
                    product_details[key] = self.get_description(schema)
                elif key == 'seller':
                    seller = self.get_seller(schema)
                    product_details[key] = seller.lower() if seller else seller
        return product_details


class ModesensParser():
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.blocks = self.extract_blocks()
        self.product_details = self.get_product_details()

    def extract_blocks(self):
        blocks = self.soup.find_all('div', class_='d-inline-block')
        return blocks

    def get_product_details(self):
        product_details = []

        for block in self.blocks:
            # Handle different types of price blocks
            product_detail = {}
            price_box = block.find('div', class_='price-box') or block.find('span', class_='price-box')
            merchant_name = block.find('div', class_='merchant-name')

            # Extracting seller
            seller = merchant_name.get_text(strip=True) if merchant_name else None
            prices = []
            if price_box:
                # Find all span elements that potentially contain prices
                price_spans = price_box.find_all('span', class_='position-relative') or [price_box]
                for span in price_spans:
                    # Extracting numeric part of the price
                    price_text = span.get_text(strip=True)
                    match = re.search(r'\d+(?:\.\d+)?', price_text)

                    if match:
                        price = float(match.group())
                        prices.append(price)

                    # Extracting currency symbol
                    currency = price_text[0] if price_text else None

            # Store the highest price, seller, and currency
            if prices:
                highest_price = max(prices)
                product_detail['price'] = highest_price
                product_detail['seller'] = seller
                product_detail['currency'] = currency
                product_details.append(product_detail)

        return product_details
class DataFetcher:
    @staticmethod
    def parse_google_results(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        for g in soup.find_all('div', class_='g'):
            links = g.find_all('a')
            if links and 'href' in links[0].attrs:  # check if 'href' attribute exists
                results.append(links[0]['href'])
        return results
    def extract_product_schema(self, html_content):
        product_schemas = []  # List to store all found product schemas

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            schema_tags = soup.find_all('script', {'type': 'application/ld+json'})

            for tag in schema_tags:
                try:
                    data = json.loads(tag.text)
                    if data.get('@type') == 'Product':
                        # Log the raw product schema for debugging
                        logging.debug("Raw Product Schema: %s", json.dumps(data, indent=4))
                        product_schemas.append(data)
                except json.JSONDecodeError:
                    continue

            if not product_schemas:
                logging.warning("No Product schema found in the HTML content.")
                return None

            return product_schemas
        except Exception as e:
            logging.error(f"Error extracting product schemas from HTML: {e}")
            return None
