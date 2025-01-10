import requests
from bs4 import BeautifulSoup
import re
import json
import os
import logging
import time
DEBUG = False
# Initialize logging
logging.basicConfig(level=logging.INFO)



def load_settings_separately(*file_paths):
    all_settings = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                settings = json.load(f)
            key_name = file_path.split('/')[-1].replace('.json', '')  # Extract filename to use as key
            all_settings[key_name] = settings
        except Exception as e:
            all_settings["error"] = str(e)
    return all_settings

def find_brand_rules(brand_name):
    logging.info(f"Searching for brand rules for {brand_name}...")
    for rule in settings['brand_rules']:
        if brand_name in rule['names']:
            logging.info(f"Found brand rules for {brand_name}.")
            return rule
    logging.info(f"No brand rules found for {brand_name}.")
    return None

def clean_sku(sku):
    logging.info(f"Cleaning SKU: {sku}")
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', sku)
    logging.info(f"Cleaned SKU: {cleaned}")
    return cleaned

def handle_brand_sku(sku, brand_name):
    logging.info(f"Handling SKU for brand: {brand_name}")

    brand_rule = find_brand_rules(brand_name)
    if not brand_rule:
        logging.error("Brand not found")
        return "Brand not found"

    cleaned_sku = clean_sku(sku)
    
    sku_format = brand_rule['sku_format']
    expected_lengths = brand_rule['expected_length']

    base_parts = sku_format['base']
    base_separator = sku_format.get('base_separator', 'None')
    if base_separator == 'None':
        base_separator = ''

    color_separator = sku_format.get('color_separator', 'None')
    if color_separator == 'None':
        color_separator = ''

    color_length = int(sku_format['color_extension'][0])

    # Build the SKU base part with "article" and "model"
    article_length = int(base_parts['article'][0])
    model_length = int(base_parts['model'][0])
    base_sku = cleaned_sku[:article_length] + base_separator + cleaned_sku[article_length:article_length + model_length]
    
    # Add color extension
    formatted_sku = base_sku + color_separator + cleaned_sku[article_length + model_length: article_length + model_length + color_length]
    print(formatted_sku)
    if len(formatted_sku) in expected_lengths['with_color']:
        logging.info(f"Formatted SKU with color extension: {formatted_sku}")
        return formatted_sku
    
    # Fallback to base SKU
    if len(base_sku) in expected_lengths['base']:
        logging.info(f"Falling back to base SKU: {base_sku}")
        return base_sku
    
    logging.error("Invalid SKU format")
    return "Invalid SKU format"

def go_to_target(Target_URL, delay, max_retries=5):
    """
    Fetch the contents of the target site and retry on specific error codes.

    :param Target_URL: The URL of the target site.
    :param max_retries: Maximum number of retries before giving up.
    :return: The response.
    """
    url = "https://api.webit.live/api/v1/realtime/web"
    error_codes = [500, 501, 555]
    
    payload = json.dumps({
      "parse": False,
      "url": Target_URL,
      "format": "html",
      "render": True,
      "country": "ALL",
      "locale": "en",     
    })
    
    if delay == True:
        print("Enabling Delay")
        payload = json.dumps({
      "parse": False,
      "url": Target_URL,
      "format": "html",
      "render": True,
      "country": "ALL",
      "locale": "en",
     "render_flow": [
          {
            "wait": {
                "delay": 8000 ####ONLY FOR MONCLER FIGURE OUT LATER
            }
      
      }]
      , 
      
    })
        
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im5pa0BsdXh1cnltYXJrZXQuY29tIiwiaXNfc3lzX2FkbWluIjpmYWxzZSwiYWNjb3VudF9uYW1lIjoibHV4dXJ5X21hcmtldCIsImFjY291bnRfZ3VpZCI6IjIxYjBiZmZhMmZmMzRlM2ZiODAxMjIzYWExMmQ0YzdjIiwicm9sZSI6ImFkbWluIiwibmFtZSI6Im5payBwb3BvdiIsImV4cCI6MTY5OTA0MjUzOSwiaWF0IjoxNjk4NzgzMzM5LCJpc3MiOiJhcGkubmltYmxld2F5LmNvbSJ9.zGTlxVpAUSsdl3qtclan8u4Sc_sBb9Ok3eSe9FCgUTE',
      #'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    
    retries = 0
    while retries < max_retries:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        if response.status_code not in error_codes:
            return response
        retries += 1
        print(f"Retry {retries} for target URL: {Target_URL} due to status code: {response.status_code}")
    
    # If the code reaches this point, all retries have been exhausted
    raise Exception(f"Failed after {max_retries} retries. Last status code: {response.status_code}")

# Note: The function above won't run successfully in this environment since we don't have access to the API.
# Make sure to replace 'YOUR_API_KEY' with your actual API key when you integrate this into your environment.




def go_to_cache_results(Cache_URL, max_retries=5):
    """
    Fetch the contents of the target site and retry on specific error codes.

    :param Target_URL: The URL of the target site.
    :param max_retries: Maximum number of retries before giving up.
    :return: The response.
    """
    Cache_URL = (f"cache:{Cache_URL}")
    print(Cache_URL)
    
    url = "https://api.webit.live/api/v1/realtime/web"
    error_codes = [500, 501, 555]
    
    payload = json.dumps({
      "parse": False,
      "url": Cache_URL,
      "format": "html",
      "render": True,
      "country": "ALL",
      "locale": "en",     
       "render_flow": [
          {
            "wait": {
                "delay": 5000 ####ONLY FOR MONCLER FIGURE OUT LATER
            }
      
      }]
      , 
      
    })
    
        
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im5pa0BsdXh1cnltYXJrZXQuY29tIiwiaXNfc3lzX2FkbWluIjpmYWxzZSwiYWNjb3VudF9uYW1lIjoibHV4dXJ5X21hcmtldCIsImFjY291bnRfZ3VpZCI6IjIxYjBiZmZhMmZmMzRlM2ZiODAxMjIzYWExMmQ0YzdjIiwicm9sZSI6ImFkbWluIiwibmFtZSI6Im5payBwb3BvdiIsImV4cCI6MTY5OTA0MjUzOSwiaWF0IjoxNjk4NzgzMzM5LCJpc3MiOiJhcGkubmltYmxld2F5LmNvbSJ9.zGTlxVpAUSsdl3qtclan8u4Sc_sBb9Ok3eSe9FCgUTE',
      #'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    
    retries = 0
    while retries < max_retries:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        if response.status_code not in error_codes:
            return response
        retries += 1
        print(f"Retry {retries} for Cache URL: {Cache_URL} due to status code: {response.status_code}")
    
    # If the code reaches this point, all retries have been exhausted
    raise Exception(f"Failed after {max_retries} retries. Last status code: {response.status_code}")

# Note: The function above won't run successfully in this environment since we don't have access to the API.
# Make sure to replace 'YOUR_API_KEY' with your actual API key when you integrate this into your environment.



def google_search(query, max_retries=5):
    """
    Conduct a Google search and retry on specific error codes.

    :param query: The search query.
    :param max_retries: Maximum number of retries before giving up.
    :return: The response.
    """
    url = "https://api.webit.live/api/v1/realtime/web"
    error_codes = [500, 501, 555]
    payload = json.dumps({
      "parse": False,
      "url": "https://www.google.com/search?q=" + str(query),
      "format": "html",
      "render": False,
      "country": "ALL",
      "locale": "en"
    })
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im5pa0BsdXh1cnltYXJrZXQuY29tIiwiaXNfc3lzX2FkbWluIjpmYWxzZSwiYWNjb3VudF9uYW1lIjoibHV4dXJ5X21hcmtldCIsImFjY291bnRfZ3VpZCI6IjIxYjBiZmZhMmZmMzRlM2ZiODAxMjIzYWExMmQ0YzdjIiwicm9sZSI6ImFkbWluIiwibmFtZSI6Im5payBwb3BvdiIsImV4cCI6MTY5OTA0MjUzOSwiaWF0IjoxNjk4NzgzMzM5LCJpc3MiOiJhcGkubmltYmxld2F5LmNvbSJ9.zGTlxVpAUSsdl3qtclan8u4Sc_sBb9Ok3eSe9FCgUTE'
    }
    retries = 0
    while retries < max_retries:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.status_code)
        if response.status_code not in error_codes:
            return response
        retries += 1
        print(f"Retry {retries} for query: {query} due to status code: {response.status_code}")
    
    # If the code reaches this point, all retries have been exhausted
    raise Exception(f"Failed after {max_retries} retries. Last status code: {response.status_code}")




#* <h3 class="LC20lb MBeuO DKV0Md"> Result Title
#* jsaction="rcuQ6b:npT2md;PYDNKe:bLV6Bd;mLt3mc"> Result URL
#* <div class="VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac">  Result Description

def parse_SERP(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all search result containers (usually a div or a similar element that wraps each result)
        result_containers = soup.find_all('div', class_='g')
        
        results = []
        
        for container in result_containers:
            # Find Result Title (h3 with class LC20lb MBeuO DKV0Md)
            title_element = container.find('h3', class_='LC20lb MBeuO DKV0Md')
            result_title = title_element.text if title_element else None
            
            # Find the parent div containing the URL information
            url_parent_div = container.find('span', jscontroller='msmzHf')
            
            if url_parent_div:
                # Find the anchor (a) element within the parent div
                anchor_element = url_parent_div.find('a', jsname="UWckNb")
                result_url = anchor_element.get('href') if anchor_element else None
            else:
                result_url = None
            
            # Find Result Description (div with class VwiC3b yXK7lf lyLwlc yDYNvb W8l4ac or with an additional class)
            description_element = container.select_one('div.VwiC3b.yXK7lf.lyLwlc.yDYNvb.W8l4ac, div.VwiC3b.yXK7lf.lyLwlc.yDYNvb.W8l4ac.lEBKkf')
            result_description = description_element.text if description_element else None
            
            result = {
                'Result Title': result_title,
                'Result URL': result_url,
                'Result Description': result_description
            }
            
            results.append(result)
        
        return results
    except Exception as e:
        print(f'Error parsing HTML: {e}')
        return None


def write_to_file(file_name, text):
    try:
        with open(file_name, 'w', encoding="utf-8") as file:
            file.write(text)
        print(f'Successfully wrote to {file_name}')
    except Exception as e:
        print(f'Error writing to {file_name}: {e}')
def filter_and_prioritize_SERP(results, product_id, domain_hierarchy=None, brand=None, category=None, currency=None):
    """
    Filter and prioritize the search results based on product ID, brand, category, currency, and domain hierarchy.
    
    Parameters:
    - results (list): List of dictionaries containing 'Result Title', 'Result URL', and 'Result Description'.
    - product_id (str): Product ID to filter results.
    - domain_hierarchy (list, optional): List of domains in order of priority.
    - brand (str, optional): Brand name to filter results.
    - category (str, optional): Category name to filter results.
    - currency (str, optional): Currency symbol or code to filter results.
    
    Returns:
    - list: List of dictionaries containing filtered and prioritized results.
    """
    
    criteria = [product_id, brand, category, currency]
    criteria = [c for c in criteria if c is not None]
    
    # Filter results based on provided information
    filtered_results = [result for result in results if all(any(criterion in (result[key] or '') for key in result) for criterion in criteria)]
    
    if not filtered_results:
        print("No matches found")
        
        return []

    if domain_hierarchy:
        # Prioritize results based on domain hierarchy
        filtered_results.sort(key=lambda x: domain_hierarchy.index(x['Result URL'].split('/')[2]) if x['Result URL'].split('/')[2] in domain_hierarchy else len(domain_hierarchy))

    return filtered_results


#def retry_search(search_func, max_retries, delay, backoff_factor=1):
#    retries = 0
#    while retries <= max_retries:
#        result = search_func()  # Replace this with the actual search function
#        if result:  # Assuming non-empty result means success
#            return result
#        retries += 1
#        time.sleep(delay)
#        delay *= backoff_factor
#
#    print("Max retries reached. No matches found.")
#    return []

def extract_product_schema(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Open a file with write mode ('w') and UTF-8 encoding
    #with open('example.txt', 'w', encoding='utf-8') as file:
        # Write some text to the file
       #file.write(str(soup))
#   
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    
    for script in script_tags:
        try:
            schema_data = json.loads(script.string)
            if schema_data.get('@type') == 'Product':
                return schema_data               
        except json.JSONDecodeError:
            continue
            
    return None

def universal_parser(html_content, settings, domain):
    """
    Parse the provided HTML content based on the settings for the given domain.

    :param html_content: String containing the HTML content.
    :param settings: Hierarchical dictionary containing the parsing instructions for multiple domains.
    :param domain: String representing the domain for which the parsing should be done.
    :return: Dictionary containing the extracted information.
    """
    if DEBUG == True:
        write_to_file("DEBUG.txt", str(html_content))
    
    # Get the settings for the specified domain
    domain_settings = settings.get(domain, {})
    # If no settings for the domain, return an empty dictionary
    if not domain_settings:
        return {}
    if domain_settings =="schema":
        extracted_data = extract_product_schema(html_content)
        return extracted_data
        
    soup = BeautifulSoup(html_content, 'html.parser')

    extracted_data = {}

    for field, field_settings in domain_settings.items():
        # Determine if we need to find one or multiple tags
        is_multiple = field_settings.get("multiple", False)
        
        # If a container is specified in settings, navigate to it first
        if "container" in field_settings:
            container_settings = field_settings["container"]
            container_tag = soup.find(container_settings["tag"], id=container_settings.get("id"))
        else:
            container_tag = soup
        
        # Extract data based on settings within the container
        if field_settings.get("id"):
            tag = container_tag.find_all(field_settings["tag"], id=field_settings["id"]) if is_multiple else container_tag.find(field_settings["tag"], id=field_settings["id"])
        elif field_settings.get("class"):
            tag = container_tag.find_all(field_settings["tag"], class_=field_settings["class"]) if is_multiple else container_tag.find(field_settings["tag"], class_=field_settings["class"])
        else:
            tag = container_tag.find_all(field_settings["tag"]) if is_multiple else container_tag.find(field_settings["tag"])

        if is_multiple:
            extracted_data[field] = [t[field_settings["attribute"]] for t in tag if field_settings["attribute"] in t.attrs]
        else:
            if tag:
                if field_settings.get("attribute", "text") == "text":
                    extracted_data[field] = tag.get_text(strip=True)
                else:
                    extracted_data[field] = tag[field_settings["attribute"]]
            else:
                extracted_data[field] = None

    return extracted_data

def write_to_master_json(parsed_data, product_id, search_query, filename="big_master.json"):
    """
    Write the parsed data to a master JSON file using the product ID as the identifier.

    :param parsed_data: Dictionary containing the extracted data or JSON-formatted string.
    :param product_id: Product ID to be used as the key.
    :param search_query: Original search query.
    :param filename: Name of the master JSON file.
    :return: None
    """
    
    # Step 1: Check if the master JSON file already exists
    if os.path.exists(filename):
        # If the file exists, open it in read mode and load its contents into a dictionary
        with open(filename, 'r', encoding='utf-8') as file:
            master_data = json.load(file)
    else:
        # If the file doesn't exist, initialize an empty dictionary
        master_data = {}

    # Step 1.5: Check the type of parsed_data
    # If it's a string, try to load it as JSON
    if isinstance(parsed_data, str):
        try:
            parsed_data = json.loads(parsed_data)
        except json.JSONDecodeError:
            print("Invalid JSON string. Writing the string as-is.")
    
    # Step 2: Update the master data dictionary
    # Use the product ID as the key and store parsed data and the original search query as values
    master_data[product_id] = {
        "parsed_data": parsed_data,
        "original_search_query": search_query
    }

    # Step 3: Write the updated master data back to the JSON file
    # Open the file in write mode
    with open(filename, 'w', encoding='utf-8') as file:
        # Use json.dump to write the dictionary to the file as a JSON-formatted string
        # 'ensure_ascii=False' keeps non-ASCII characters, and 'indent=4' makes the JSON human-readable
        json.dump(master_data, file, ensure_ascii=False, indent=4)

    # Step 4: Print a message indicating that the data has been written
    print(f"Data for product ID {product_id} written to {filename}.")




def write_to_master_json_old(parsed_data, product_id, search_query, filename="big_master.json"):
   ##### REMOVE LATER IF OTHER FUNCTIONS WORKS WELL
   
    """
    Write the parsed data to a master JSON file using the product ID as the identifier.

    :param parsed_data: Dictionary containing the extracted data.
    :param product_id: Product ID to be used as the key.
    :param search_query: Original search query.
    :param filename: Name of the master JSON file.
    :return: None
    """
    # If the file already exists, load its contents
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            master_data = json.load(file)
    else:
        master_data = {}

    # Update the master data with the new parsed data
    master_data[product_id] = {
        "parsed_data": parsed_data,
        "original_search_query": search_query
    }

    # Write the updated master data back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(master_data, file, ensure_ascii=False, indent=4)

    print(f"Data for product ID {product_id} written to {filename}.")
def extract_url_from_string(input_string):
    # Define a regular expression pattern to match the URL
    url_pattern = r"'Result URL': '([^']+)'"

    # Use the re.search() function to find the URL
    match = re.search(url_pattern, input_string)

    # Check if a match was found
    if match:
        # Extract the URL from the match object
        url = match.group(1)
        return url
    else:
        return None    
    
    
def load_product_ids(filename):
    """
    Load a list of product IDs from a text file.

    :param filename: Path to the text file containing the product IDs.
    :return: List of product IDs.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        product_ids = [line.strip() for line in file.readlines()]
    return product_ids

def load_brand_names(filename):
    """
    Load a list of product IDs from a text file.

    :param filename: Path to the text file containing the product IDs.
    :return: List of product IDs.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        brand_names = [line.strip() for line in file.readlines()]
    return brand_names

def process_product_ids(product_ids_file, brand_name_file,error_log_file="error_ids.txt"):
    """
    Process a list of product IDs: create search queries, search on Google, parse results, and save to JSON.

    :param product_ids_file: Path to the text file containing the product IDs.
    :param domain: The domain to be used in the search queries.
    :return: None
    """
    product_ids = load_product_ids(product_ids_file)
    error_ids = []
    
    brand_names = load_brand_names(brand_name_file)
    

    for index,product_id in enumerate(product_ids):
        try:
            # Create the search query       
            formatted_sku = handle_brand_sku(product_id, brand_names[index])#DO NOT LEAVE GUCCI HARDCODED
            brand_rule = find_brand_rules(brand_names[index])
            if not brand_rule:
                logging.error("Brand not found")
                return "Brand not found"
            domain = brand_rule['domain_hierarchy'][0]
            delay = brand_rule['delay']
            print(f'Delay: {delay}')
            
            print(f'{brand_names[index]} {formatted_sku} {domain}')
            
            query = f'site:{domain} "{formatted_sku}"'

            # Perform the Google search
            response = google_search(query)
            results = parse_SERP(response.text)
            print(results)
            # Filter and prioritize the results
            filtered_results = filter_and_prioritize_SERP(results, product_id=formatted_sku)#, currency='us')##FORMATED SKU OR PRODUCTID??

            # Extract the target URL and get its content
            Target_URL = extract_url_from_string(str(filtered_results))
            if Target_URL:
                target_body = go_to_target(Target_URL,delay).text

                # Parse the target page content
                parsed_data = universal_parser(target_body, settings_multi_domain, domain)
                
                if parsed_data:
                # Write the parsed data to the master JSON file
                    write_to_master_json(parsed_data, product_id, query)
                else:
                    #cache_body = go_to_cache_results(Target_URL).text
                    #parsed_data = universal_parser(cache_body, settings_multi_domain, domain)
                    write_to_master_json(parsed_data, product_id, query)

            else:
                print(f"URL not found for product ID: {formatted_sku}.")
                error_ids.append(product_id)
        except Exception as e:
            print(f"Error processing product ID {formatted_sku}: {e}")
            error_ids.append(product_id)       
                 
        # Write error IDs to the error log file
    with open(error_log_file, 'w') as file:
        for error_id in error_ids:
            file.write(f"{error_id}\n")

    print("Processing completed.")








#
## Load settings from JSON file
#logging.info("Loading settings from JSON file...")
#with open("settings.json", "r") as f:
#    settings = json.load(f)
    
    
all_settings = load_settings_separately('settings.json', 'settings_multi_domain.json')
settings = all_settings['settings']
settings_multi_domain = all_settings['settings_multi_domain']



process_product_ids("ids.txt", "brands.txt")