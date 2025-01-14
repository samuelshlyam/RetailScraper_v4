import csv
import json
import os
import re

from bs4 import BeautifulSoup
from selenium import webdriver

class SKUManager:
    def __init__(self, brand_settings):
        self.brand_settings = brand_settings

    def generate_variations(self, input_sku, brand_rule):
        brand_names = brand_rule.get('names', [])
        input_variations=[input_sku]
        for brand_name in brand_names:
            input_variations.append(input_sku + " " + brand_name)
        brand_variations = self.create_brand_variations(input_sku, brand_rule)
        blind_variations = self.create_blind_variations(input_sku, brand_rule)
        total_variations = input_variations + brand_variations + blind_variations

        print(f"Total Variations before length {len(total_variations)}")
        total_variations = list(dict.fromkeys(total_variations))
        print(f"Total Variations after length {len(total_variations)}")

        return total_variations

    def generate_query(self, variation):
        query = f"\"{variation}\""
        query=f"https://www.google.com/search?q={query}"
        return query

    def create_brand_variations(self, sku, brand_rule):
        brand_names = brand_rule.get('names', [])
        cleaned_sku = clean_sku(sku)
        sku_format = brand_rule['sku_format']
        base_parts = sku_format['base']
        base_separator = sku_format.get('base_separator', '')
        color_separator = sku_format.get('color_separator', '')
        complex = brand_rule.get('complex', False)

        article_length = int(base_parts['article'][0].split(',')[0])
        model_length = int(base_parts['model'][0].split(',')[0])
        color_length = int(sku_format['color_extension'][0].split(',')[0])

        article_part = cleaned_sku[:article_length]
        model_part = cleaned_sku[article_length:article_length + model_length]
        color_part = cleaned_sku[article_length + model_length:article_length + model_length + color_length]
        if complex:
            return self.complex(article_length, model_length, cleaned_sku, base_separator)
        # Order: Brand Format with Color, Brand Format without Color
        brand_sku_list=[]
        for brand_name in brand_names:
            brand_sku_list.extend(
                [
                    article_part + base_separator + model_part + color_separator + color_part,
                    article_part + base_separator + model_part + color_separator + color_part + " " + brand_name,
                    article_part + base_separator + model_part,
                    article_part + base_separator + model_part + " " + brand_name
                ]
            )
        print(f"Brand List before length {len(brand_sku_list)}")
        brand_sku_list = list(dict.fromkeys(brand_sku_list))
        print(f"Brand List after length {len(brand_sku_list)}")
        return brand_sku_list

    def create_blind_variations(self, sku, brand_rule):
        delimiters=["."," ","-","_",""]
        brand_names=brand_rule.get('names',[])
        cleaned_sku = clean_sku(sku)
        sku_format = brand_rule['sku_format']
        base_separator = sku_format.get('base_separator', '')
        article_length = int(sku_format['base']['article'][0].split(',')[0])
        model_length = int(sku_format['base']['model'][0].split(',')[0])
        color_length = int(sku_format['color_extension'][0].split(',')[0])
        complex = brand_rule.get('complex', False)
        article_part = cleaned_sku[:article_length]
        model_part = cleaned_sku[article_length:article_length + model_length]
        color_part = cleaned_sku[article_length + model_length:article_length + model_length + color_length]
        if complex:
            return self.complex(article_length, model_length, cleaned_sku, base_separator)
        # Order: No space (Article Model Color), Space (Article Model Color), No space (Article Model), Space (Article Model)
        blind_sku_list=[]
        for brand_name in brand_names:
            for base_separator in delimiters:
                for color_separator in delimiters:
                    blind_sku_list.extend(
                        [
                            article_part + base_separator + model_part + color_separator + color_part,
                            article_part + base_separator + model_part + color_separator + color_part + " " + brand_name,
                            article_part + base_separator + model_part,
                            article_part + base_separator + model_part + " " + brand_name,
                        ]
                    )
        print(f"Blind List before length {len(blind_sku_list)}")
        blind_sku_list = list(dict.fromkeys(blind_sku_list))
        print(f"Blind List after length {len(blind_sku_list)}")
        return blind_sku_list

    def complex(self, article_length, model_length, cleaned_sku, base_separator):
        print(cleaned_sku)
        new_sku = remove_letters_from_end(cleaned_sku)

        article_part = new_sku[:article_length]
        model_part = new_sku[len(new_sku) - model_length:]
        return [
            article_part + base_separator + model_part,
            model_part
        ]
class BrandSettings:
    def __init__(self, settings):
        self.settings = settings

    def get_rules_for_brand(self, brand_name):
        for rule in self.settings['brand_rules']:
            if str(brand_name).lower() in str(rule['names']).lower():
                return rule
        return None
@staticmethod
def remove_letters_from_end(s):
    non_letter_index = None
    for i in range(len(s) - 1, -1, -1):
        if not s[i].isalpha():
            non_letter_index = i
            break

    # If there are no non-letter characters, return an empty string
    if non_letter_index is None:
        return s

    # Return the string up to the last non-letter character
    return s[:non_letter_index + 1]

def clean_sku(sku):
    sku = str(sku)
    print(f"Cleaning SKU: {sku}")
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', sku)
    print(f"Cleaned SKU: {cleaned}")
    return cleaned


def listify_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def parse_google_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g'):
        links = g.find_all('a')
        if links and 'href' in links[0].attrs:  # check if 'href' attribute exists
            results.append(links[0]['href'])
    return results

options = webdriver.ChromeOptions()
options.add_argument("--auto-open-devtools-for-tabs")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
options.add_argument("--start-maximized")
options.add_argument("--incognito")
options.add_argument("--enable-javascript")
options.add_argument('--no-sandbox')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless=new")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

#SKU, Brand, Location are passed in
#Test Product Variations
current_directory=os.getcwd()
settings_directory=os.path.join(current_directory,"brand_settings.json")
settings = json.loads(open(settings_directory).read())
brand_settings = BrandSettings(settings)
test_settings=brand_settings.get_rules_for_brand("Givenchy")
test_sku="BB50V9B1UC105"
test_SKUManager=SKUManager(test_settings)
variations=test_SKUManager.generate_variations(test_sku,test_settings)
final_output=[]
variations=variations[:25]
for variation in variations:
    query = test_SKUManager.generate_query(variation)
    driver=webdriver.Chrome(options=options)
    driver.get(query)
    page_source = driver.execute_script("return document.documentElement.outerHTML;")
    output_urls=parse_google_results(page_source)
    single_output={"Variation":variation,"Unfiltered URLs":output_urls}
    final_output.append(single_output)
print(final_output)


