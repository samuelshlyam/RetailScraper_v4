import csv
import re


class SKUManager:
    def __init__(self, brand_settings):
        self.brand_settings = brand_settings

    def generate_variations(self, input_sku, brand_rule):
        brand_variations = self.handle_brand_sku(input_sku, brand_rule)
        blind_variations = self.handle_sku(input_sku, brand_rule)
        total_variations = brand_variations + blind_variations
        # modified_variations = []  # Create a new list for the modified variations
        # for variation in total_variations:
        #    modified_variations.append(f"site:farfetch.com {variation}")
        ## Combine the original and modified variations
        # total_variations += modified_variations
        return total_variations

    def handle_brand_sku(self, sku, brand_rule):
        cleaned_sku = self.clean_sku(sku)
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
        return [
            article_part + base_separator + model_part + color_separator + color_part,
            article_part + base_separator + model_part
        ]

    def handle_sku(self, sku, brand_rule):
        cleaned_sku = self.clean_sku(sku)
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
        return [
            article_part + model_part + color_part,
            article_part + ' ' + model_part + ' ' + color_part,
            article_part + model_part,
            article_part + ' ' + model_part
        ]

    def complex(self, article_length, model_length, cleaned_sku, base_separator):
        print(cleaned_sku)
        new_sku = SKUManager.remove_letters_from_end(cleaned_sku)

        article_part = new_sku[:article_length]
        model_part = new_sku[len(new_sku) - model_length:]
        return [
            article_part + base_separator + model_part,
            model_part
        ]

    @staticmethod
    def remove_letters_from_end(s):
        non_letter_index = None
        for i in range(len(s) - 1, -1, -1):
            if not s[i].isalpha():
                non_letter_index = i
                break

        # If there are no non-letter characters, return an empty string
        if non_letter_index is None:
            return ""

        # Return the string up to the last non-letter character
        return s[:non_letter_index + 1]

    @staticmethod
    def clean_sku(sku):
        sku = str(sku)
        Logger.log(f"Cleaning SKU: {sku}")
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', sku)
        Logger.log(f"Cleaned SKU: {cleaned}")
        return cleaned

    @staticmethod
    def listify_file(file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
        return data

