import json
import os
from urllib.parse import urlparse
class FilterURLS:
    def filter_urls(self, urls, brand_settings, whitelisted_domains):
        variation=urls.get("Variation")
        unfiltered_urls=urls.get("Unfiltered URLs")
        brand_domains = [domain.replace('www.', '') for domain in brand_settings.get("domain_hierarchy", [])]
        whitelisted_domains = [domain.replace('www.', '') for domain in whitelisted_domains]
        filtered_urls=[]
        if isinstance(unfiltered_urls, str):
            unfiltered_urls = unfiltered_urls.split(',')

        for url in unfiltered_urls:
            url = str(url).strip()
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                print(f"Domain: {domain}")
                if domain in brand_domains:
                    filtered_urls.append({"Variation":variation,"URL":url, "Level":"brand"})
                elif domain in whitelisted_domains:
                    filtered_urls.append({"Variation":variation,"URL":url, "Level":"whitelist"})
                elif 'modesens' in domain:
                    filtered_urls.append({"Variation":variation,"URL":url, "Level":"modesens"})
                else:
                    filtered_urls.append({"Variation":variation,"URL":url, "Level":"unapproved"})
            except Exception as e:
                print(f"Error parsing URL '{url}': {e}")
        return filtered_urls

    def filter_urls_by_currency(self, currency_items, sorted_input):
        filtered_output=[]
        for input in sorted_input:
            url=input.get("URL","")
            input["Currency"]="Wrong Currency"
            for item in currency_items:
                # print(f'item: {item} url: {url}')
                # print(f'item: {type(item)} url: {type(url)}')
                # print(url)
                if str(item.lower()) in str(url).lower():
                    print(f"item: {item} url: {url}")
                    input["Currency"]="Correct Currency"
                    break
            filtered_output.append(input)

        return filtered_output

    def sortURLs(self,filtered_input):
        flattened = []
        for sublist in filtered_input:
            flattened.extend(sublist)

        url_map = {}
        for entry in flattened:
            url = entry.get("URL", "").strip()
            variation = entry.get("Variation", "").strip()
            level = entry.get("Level", "").strip()

            if not url:
                continue

            if url not in url_map:
                url_map[url] = {
                    "URL": url,
                    "Variations": set(),
                    "Level": level,
                }

            url_map[url]["Variations"].add(variation)

        result = []
        for url_info in url_map.values():
            result.append({
                "URL": url_info["URL"],
                "Variations": sorted(url_info["Variations"]),
                "Level": url_info["Level"],
            })
        level_priority = {
            "brand": 0,
            "whitelist": 1,
            "modesens": 2,
            "unapproved": 3
        }
        def get_min_priority(level):
            return level_priority.get(level, 999)
        result.sort(key=lambda item: get_min_priority(item["Level"]))
        return result

class BrandSettings:
    def __init__(self, settings):
        self.settings = settings

    def get_rules_for_brand(self, brand_name):
        for rule in self.settings['brand_rules']:
            if str(brand_name).lower() in str(rule['names']).lower():
                return rule
        return None


#Test Filter and Sorting
current_directory=os.getcwd()
brand_settings_directory=os.path.join(current_directory,"brand_settings.json")
currency_settings_directory=os.path.join(current_directory,"currency_filter_settings.json")
brand_settings = json.loads(open(brand_settings_directory).read())
brand_settings = BrandSettings(brand_settings)
currency_settings=json.loads(open(currency_settings_directory).read())
currency_items=currency_settings["US"]
test_settings=brand_settings.get_rules_for_brand("Givenchy")
input=[{'Variation': 'BB50V9B1UC105', 'Unfiltered URLs': ['https://www.thebs.com/us/raffia-basket-bag-with-leather-handles-givenchy-413829', 'https://www.italist.com/us/women/bags/shoulder-bags/voyou-basket-bag/13634594/13802285/givenchy/?srsltid=AfmBOoolF1Tv1YXIGplwNlZCtylCUUhaC44CdYAxAZ1q0-PxLD4FrLeJ', 'https://us.levelshoes.com/givenchy-medium-voyou-basket-bag-beige-other-women-tote-bags-jrb8tv.html?srsltid=AfmBOooc2vtOE7opjXJFp_6PSI17Pxy8F86ojaoK_WkN6g5xKUm13PDL', 'https://michelefranzesemoda.com/en/products/givenchy-borsa-a-spalla-voyou-medium-givenchy-br-bb50v9b1uc-105?srsltid=AfmBOopWv_U5hgCnsUr71FM3ZnPv_6GMNahwcj4Dy5q6iDILVC_WX6kU', 'https://modesens.com/product/givenchy-medium-voyou-basket-bag-yellow-87602076/?srsltid=AfmBOopCMg1aNNMOef-6WkENogISl4H0KesuDOA3CZVhSk_NSBwjLRfk', 'https://poshmark.com/listing/GIVENCHY-Givenchy-Plage-medium-capsule-Voyou-shopper-653cbe90af9ad1683c643c43?srsltid=AfmBOopXYibWAJTjfKVHpfRSvvQUu47sGye_skFeO627qZipvMuATq5v', 'https://www.reversible.com/shopping/women/item/givenchy-medium-voyou-basket-bag-in-raffia-798467495?srsltid=AfmBOoop56bqs8jH8NRpkAbCMZ4iCvvzUq3GnPKU74OR4UPE2kNWeaak', 'https://michelefranzesemoda.com/en-gb/products/givenchy-borsa-a-spalla-voyou-medium-givenchy-br-bb50v9b1uc-105?srsltid=AfmBOorEl_UJx2E50SCnbGkeDf7e9Fje_jmgBG3bk3l8-yJ3ZGWp30a0', 'https://www.baltini.com/en-eu/products/givenchy-voyou-medium-shoulder-bag-1735869891182417819?srsltid=AfmBOorX97_lsSU9GHkiR6Zjow_1L52hRNBGHw7urKyVpWqWITQgnqyo', 'https://www.reversible.com/gb/shopping/women/item/798467495?srsltid=AfmBOorHfzILOs4rwalHbT5skWBb-aY-TWV9rGkG_HAoFPDNP2L4eIRY', '/search?sca_esv=db7ed66b9cb86445&q=Givenchy+Women%27s+Voyou+Small+Basket+Bag&stick=H4sIAAAAAAAAAONgFuLVT9c3NMwpKcmyMEkzUIJwy9MK44sM8wy1ZLOTrfSLM_ILCjLz0vXTC5KtilJzEktSU3SLU0uKF7Gqu2eWpeYlZ1QqhOfnpuapFyuE5VfmlyoE5ybm5Cg4JRZnp5YAqXQAUFNpOGkAAAA&sa=X&ved=2ahUKEwjojI6N3POKAxU3UGwGHaCeLMkQnj8oAHoECEwQBw', '#']}, {'Variation': 'BB50V9B1UC105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V9B1UC105 Givenchy', 'Unfiltered URLs': ['https://dreamroom.club/product/sumka-givenchy-givenchy-plage-medium-capsule-voyou-shopper-bezheva/?srsltid=AfmBOop8T-0So731WJyDdN3uqy9u8r44i441lZ2Q3UqMSpuQApK5WTq8']}, {'Variation': 'BB50V9B1UC105 GIVENCHY', 'Unfiltered URLs': ['https://dreamroom.club/product/sumka-givenchy-givenchy-plage-medium-capsule-voyou-shopper-bezheva/?srsltid=AfmBOoociDJx6uM2UglPYazSXC1MWpa0cqtg83O9x2eY8o8d4hoQULv5']}, {'Variation': 'BB50V9B1UC-105', 'Unfiltered URLs': ['https://www.givenchy.com/us/en-US/medium-voyou-basket-bag-in-raffia/BB50V9B1UC-105.html', 'https://fashionporto.com/shop/women/bags/beach-bags/torba-bb50v9b1uc-105/', 'https://www.grifo210.com/en-ww/products/givenchy-medium-voyou-basket-bag-bb50v9b1uc-105?srsltid=AfmBOopkscCv-JLto_35URo5TEg7UvzqsTULI-yFHK53cOVXAkD74vQS', 'https://michelefranzesemoda.com/en/products/givenchy-borsa-a-spalla-voyou-medium-givenchy-br-bb50v9b1uc-105?srsltid=AfmBOooYGFoXW1fQ1HxpyWUbh6gts1T5__UOr94YH1LgRXCKMEEraY7S', 'https://modesens.com/product/givenchy-women-straw-medium-voyou-basket-shopping-bag-brown-107056049/?srsltid=AfmBOoqLSb9cV_TfYnLTl_5IYri1j1mPynGD2yUscm9CSB9MiIYUbaVf', 'https://sisol.al/products/givenchy-1', 'https://www.pinterest.com/pin/sensi-studio-small-basket-bag-ksilaukku-whitesandvalkoinen-zalandofi-in-2024--181269954338919712/', 'https://vn.labellastella.com/en/products/givenchy-medium-straw-basket-handbag', 'https://www.buyma.com/r/BB50V9B1UC%20105/?srsltid=AfmBOorVLhv6lDZStM8UdeBqESiIKd1VqvNhEIKc1KRMwEFWu6cmY-_R']}, {'Variation': 'BB50V9B1UC-105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V9B1UC', 'Unfiltered URLs': ['https://www.givenchy.com/us/en-US/medium-voyou-basket-bag-in-raffia/BB50V9B1UC-001.html', 'https://www.farfetch.com/shopping/women/givenchy-medium-voyou-raffia-basket-bag-item-20509273.aspx', 'https://modecraze.com/products/medium-voyou-raffia-shoulder-bag-bb50v9b1uc-white?srsltid=AfmBOorG2Z5Xtrxjsg50e_Qt4Lr8rJ0bFgwx1kQ2cJl1n3Xv-Xu1r3-k', 'https://www.cettire.com/products/givenchy-medium-voyou-basket-bag-927373935', 'https://www.goat.com/apparel/givenchy-medium-voyou-basket-bag-black-bb50v9b1uc-001', 'https://www.lagrange12.com/en_ca/straw-medium-voyou-basket-shopping-bag-bb50v9b1uc-001.html', 'https://global.jentestore.com/products/1505608', 'https://www.gebnegozionline.com/en_us/straw-medium-voyou-basket-shopping-bag-bb50v9b1uc-001.html', 'https://fashionporto.com/shop/women/bags/beach-bags/torba-bb50v9b1uc-001/', '/search?sca_esv=db7ed66b9cb86445&q=Givenchy+Women%27s+Voyou+Small+Basket+Bag&stick=H4sIAAAAAAAAAONgFuLVT9c3NMwpKcmyMEkzUIJwy9MK44sM8wy1ZLOTrfSLM_ILCjLz0vXTC5KtilJzEktSU3SLU0uKF7Gqu2eWpeYlZ1QqhOfnpuapFyuE5VfmlyoE5ybm5Cg4JRZnp5YAqXQAUFNpOGkAAAA&sa=X&ved=2ahUKEwj-xrqT3POKAxWXR2wGHeI4EEIQnj8oAHoECEQQBw', '#']}, {'Variation': 'BB50V9B1UC GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V9B1UC-105 Givenchy', 'Unfiltered URLs': ['https://www.buyma.com/item/106733789/?srsltid=AfmBOooqQYDclPk2tj_HeNRU0WprOxmIZ98B8EupKAHVuMabCtE2wIjr', 'https://snkrdunk.com/apparels/363384/sales-histories?slide=right', 'https://snkrdunk.com/apparels/363384']}, {'Variation': 'BB50V9B1UC Givenchy', 'Unfiltered URLs': ['https://www.buyma.com/item/111933350/?srsltid=AfmBOoo3aYh8GmT7ZRVTWo6ELhojolvhytA_CawzTngTS7rFGaymMg0h', 'https://www.redpaper.com.br/96315231659.htm', 'https://www.tehnodar.rs/81134302387.htm', 'https://sangriafilms.com/?_ga=2.198040047.1958808748.1721886654-862398307.1699453578&_bdsid=2ulvIJ.n~ZXCIW.1721886656070.1721886848&_bd_prev_page=https://sangriafilms.com/detail.php?86640165781.htm']}, {'Variation': 'BB50V9B1UC-105 GIVENCHY', 'Unfiltered URLs': ['https://www.buyma.com/item/106733789/?srsltid=AfmBOooqPlcyBNVYd8q2loZOItGiqTD-rLUEqAayPG8hHb5xeHbZMFHQ', 'https://snkrdunk.com/apparels/363384/sales-histories?slide=right', 'https://snkrdunk.com/apparels/363384']}, {'Variation': 'BB50V9B1UC GIVENCHY', 'Unfiltered URLs': ['https://www.buyma.com/item/111933350/?srsltid=AfmBOooSbsW1TfCDZA3j2yWGN8hQMNtAKjuLAB7ZeafQkVY2FGfTstK-', 'https://www.redpaper.com.br/96315231659.htm', 'https://www.tehnodar.rs/81134302387.htm', 'https://sangriafilms.com/?_ga=2.198040047.1958808748.1721886654-862398307.1699453578&_bdsid=2ulvIJ.n~ZXCIW.1721886656070.1721886848&_bd_prev_page=https://sangriafilms.com/detail.php?86640165781.htm']}, {'Variation': 'BB50V.9B1UC.105', 'Unfiltered URLs': ['http://www.jecr.org/eadjbrshop/pr/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/mz/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'https://tgkb5.ru/index.php/ecfjbtshop/uy/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/hk/p/voyou-medium-shopper-bag-givenchy-bag-1652078']}, {'Variation': 'BB50V.9B1UC.105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC', 'Unfiltered URLs': ['http://www.jecr.org/eadjbrshop/pr/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/mz/p/voyou-medium-shopper-bag-givenchy-bag-1656039', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/hk/p/voyou-medium-shopper-bag-givenchy-bag-1652078']}, {'Variation': 'BB50V.9B1UC GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC 105', 'Unfiltered URLs': ['http://www.jecr.org/eadjbrshop/pr/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/mz/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'https://tgkb5.ru/index.php/ecfjbtshop/uy/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/hk/p/voyou-medium-shopper-bag-givenchy-bag-1652078']}, {'Variation': 'BB50V.9B1UC 105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC-105', 'Unfiltered URLs': ['http://www.jecr.org/eadjbrshop/pr/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/mz/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'https://tgkb5.ru/index.php/ecfjbtshop/uy/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/hk/p/voyou-medium-shopper-bag-givenchy-bag-1652078']}, {'Variation': 'BB50V.9B1UC-105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC_105', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC_105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC105', 'Unfiltered URLs': []}, {'Variation': 'BB50V.9B1UC105 GIV', 'Unfiltered URLs': []}, {'Variation': 'BB50V 9B1UC.105', 'Unfiltered URLs': ['http://www.jecr.org/eadjbrshop/pr/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/tw/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'https://tgkb5.ru/index.php/ecfjbtshop/uy/p/voyou-medium-shopper-bag-givenchy-bag-1652078', 'http://www.anatomia.fmed.edu.uy/bcejbjshop/hk/p/voyou-medium-shopper-bag-givenchy-bag-1652078']}]
whitelisted_domains = [
        "fwrd.com",
        "saksfifthavenue.com",
        "saksoff5th.com",
        "nordstrom.com",
        "nordstromrack.com"
    ]
test_Filter=FilterURLS()
filtered_input=[]
for URLs in input:
    filtered_urls=test_Filter.filter_urls(URLs,test_settings,whitelisted_domains)
    filtered_input.append(filtered_urls)
print(filtered_input)
sorted_input=test_Filter.sortURLs(filtered_input)
print(sorted_input)
final_output=test_Filter.filter_urls_by_currency(currency_items,sorted_input)
print(final_output)
