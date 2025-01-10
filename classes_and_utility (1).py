
# Import statements
from typing import Any
import requests, datetime
from bs4 import BeautifulSoup
import json
import csv
import re
import logging
import random
from urllib.parse import urlparse
import time
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import datetime
import subprocess
from openpyxl.drawing.image import Image as OpenpyxlImage
from PIL import Image as PILImage
import unittest
import io
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.utils.units import pixels_to_EMU, cm_to_EMU
#Should be unnecessary
class Product:
    def __init__(self, input_sku, brand):
        self.input_sku = input_sku
        self.brand = brand
        self.variations = []
        self.title = None
        self.images = []
        self.prices = []
        self.currency = None
        self.url = None
        self.description = None
        self.source_type = None  # New attribute to store the source type
        self.seller = None  # New attribute to store the seller information
        self.excel_row_number=None
    def add_variation(self, variation):
        self.variations.append(variation)

    def set_details(self, title, images, prices, currency, url, description, seller):
        self.title = title
        self.images = images
        self.prices = prices
        self.currency = currency
        self.url = url
        self.description = description
        self.seller = seller  

    def is_complete(self):
        return bool(self.prices and self.url)


class BrandSettings:
    def __init__(self, settings):
        self.settings = settings

    def get_rules_for_brand(self, brand_name):
        for rule in self.settings['brand_rules']:
            if str(brand_name).lower() in str(rule['names']).lower():
                return rule
        return None 
import threading   

    
# settings = json.loads(open('msrp_project\msrp_app\settings.json').read())
# brand_settings = BrandSettings(settings)
# brand_rules = brand_settings.get_rules_for_brand("Dolce & Gabbana")
# html=Azure_Replace.send_request("https://modesens.com/product/bottega-veneta-loop-mini-intrecciato-crossbody-bag-red-61320856/", brand_rules)
# modesens=ModesensParser(html)
# print(modesens.product_details)
# with open('GGGGGGG.html', 'w',encoding='utf-8') as file:
#    file.write(html)
