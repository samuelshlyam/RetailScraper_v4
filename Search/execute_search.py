
class SearchEngine:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    def create_brand_search_query(self, sku, brand_settings, iteration):
        if iteration <= 1:  # For the first two iterations, include brand and site operator
            domain = brand_settings.get("domain_hierarchy", [])[0] if brand_settings.get("domain_hierarchy") else ""
            query = f"site:{domain} \"{sku}\""
        else:  # For the rest, just use the SKU
            query = f"\"{sku}\""
        # else:
        #    query = f"site:farfetch.com\"{sku.strip('site:farfetch.com')}\""
        return f"https://www.google.com/search?q={query}"

    def choose_random_header(self):
        ua = random.choice(self.user_agents)
        # return ua.replace(";", "")
        return ua

    def filter_urls_by_brand_and_whitelist(self, urls, brand_settings, whitelisted_domains):
        brand_domains = [domain.replace('www.', '') for domain in brand_settings.get("domain_hierarchy", [])]
        whitelisted_domains = [domain.replace('www.', '') for domain in whitelisted_domains]
        approved_brand_urls = []
        approved_whitelist_urls = []
        # approved_farfetch_urls=[]
        approved_modesens_urls = []
        if isinstance(urls, str):
            urls = urls.split(',')

        for url in urls:
            url = str(url).strip()
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                Logger.log(f"Domain: {domain}")
                if domain in brand_domains:
                    approved_brand_urls.append([url, "brand"])
                elif domain in whitelisted_domains:
                    approved_whitelist_urls.append([url, "whitelist"])
                # elif "farfetch" in domain:
                #    approved_farfetch_urls.append([url, "farfetch"])
                elif 'modesens' in domain:
                    approved_modesens_urls.append([url, "modesens"])
            except Exception as e:
                Logger.log(f"Error parsing URL '{url}': {e}")
        # Combine brand URLs and whitelist URLs
        approved_urls = approved_brand_urls + approved_whitelist_urls + approved_modesens_urls  # +approved_farfetch_urls
        return approved_urls

    def filter_urls_by_currency(self, currency_items, urls):
        filtered_urls = []
        Logger.log(f'Filtered {urls}')
        for url in urls:
            Logger.log(f"url: {url}")
            for item in currency_items:
                # print(f'item: {item} url: {url}')
                # print(f'item: {type(item)} url: {type(url)}')
                # print(url)
                if str(item.lower()) in str(url[0]).lower():
                    Logger.log(f"item: {item} url: {url}")
                    filtered_urls.append(url)
                    break

        return filtered_urls
