import os
from pymongo import MongoClient
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
import random



# General Variables
smtp_server = "smtp.gmail.com"
smtp_port = 465  # or 587 for STARTTLS
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Verify the MongoDB URI
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri.startswith('mongodb://') and not mongo_uri.startswith('mongodb+srv://'):
    raise ValueError("Invalid MongoDB URI. It must start with 'mongodb://' or 'mongodb+srv://'")

# MongoDB connection
def connect_to_mongo(uri):
    """Connect to MongoDB and return the client."""
    try:
        client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
        client.admin.command('ping')  # Ping to test connection
        return client
    except ServerSelectionTimeoutError as err:
        print(f"Server selection error: {err}")
        raise

def product_carts_len(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  ul_element = soup.find('ul', class_='search-controls-pagination_nav_component__list')
  
  # Find all li elements within the ul
  if ul_element is None:
    return 1
  li_elements = ul_element.find_all('li')
  # Get the last li element
  last_li = li_elements[-2].text.strip()
  
  return (last_li)

def get_categories(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  categories_list= soup.find_all('a','category-categories_with_icons_block_component__categoryLink')
  categories = [category.text.strip() for category in categories_list]
  return categories

def scrape_themeforest(url , category , all_cat):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    items = []

    for item in soup.find_all('div', class_='shared-item_cards-card_component__root'):
      if item is not None:
        name = item.find('h3').text.strip()
        author =item.find('a', class_='shared-item_cards-author_category_component__link').text.strip()
        price =item.find('div', class_='shared-item_cards-price_component__root').text.strip()
        rating = item.find('div' , class_='shared-stars_rating_component__starRating')
        if rating is not None:
          rating = rating.get('aria-label')
        else:
          rating = 'No rating'

        sales =item.find('div', class_='shared-item_cards-sales_component__root').text.strip()
        last_update =item.find('div', class_='shared-item_cards-list-image_card_component__lastUpdated shared-item_cards-list-image_card_component__tinyText').text.strip()
      
        ul_element = item.find('ul', class_='shared-item_cards-key_features_component__root')
        # Find all li elements within the ul
        if ul_element is None:
            features = ['No features']
        else :
          li_elements = ul_element.find_all('li')
          # Extract and print the text of each li
          features = [li.text.strip() for li in li_elements]


        items.append({
            'name': name,
            'author': author,
            'category':all_cat,
            'sub_category':category,
            'sales': sales,
            'rating': rating,
            'price': price,
            'last_update': last_update,
            'tags': ', '.join(features)
        })
      else:
        print("Element not found")

    return items

def main():
  print('Lets Go')
  all_items = []
  all_categories =['site-templates','wordpress',
                   'ui-templates','template-kits',
                   'ecommerce','marketing',
                   'cms-themes','muse-templates',
                   'blogging','jamstack',
                   'courses','forums']

  for cat in all_categories:
    categories = get_categories(f'https://themeforest.net/category/{cat}')
    categories = list(set(categories))
    for category in categories:
      if category == 'Blog / Magazine':
        category = 'blog-magazine'
      
      category = category.replace(" ", "-").lower()
      print(f'{cat} : {category}')

      carts_len = product_carts_len(f'https://themeforest.net/category/{cat}/{category}?sort=sales')

      for page in range(1, int(carts_len)): 
        url = f'https://themeforest.net/category/{cat}/{category}?page={page}&sort=sales#content'
        items = scrape_themeforest(url ,category , cat)
        all_items.extend(items)
        sleep(random.uniform(1, 3))  

  all_categories2 =['jamstack',
                   'courses',
                   'forums']
  for cat in all_categories2 :
    carts_len = product_carts_len(f'https://themeforest.net/category/{cat}')
    category = cat
    print(f'{cat} : {category}')
    for page in range(1, int(carts_len)): 
      url = f'https://themeforest.net/category/{cat}?page={page}#content'
      items = scrape_themeforest(url ,category , cat)
      all_items.extend(items)
      sleep(random.uniform(1, 3)) 
  return all_items
  
# Save to CSV
def save_to_csv(all_items):
  with open('themeforest_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'author', 'category','sub_category', 'sales', 'rating', 'price', 'last_update', 'tags'])
    writer.writeheader()
    writer.writerows(all_items)

if __name__ == '__main__':
    theme_data= main()

    
    client = connect_to_mongo(mongo_uri)
    
    # Choose your database and collection
    db = client['themeforest']
    collection = db['themes']
    item =0
    for template in theme_data:
        # Check if the document already exists in the collection
        existing_document = collection.find_one(template)
        
        if existing_document:
            item = item +1
            print(f"Document Number:: {item}/{len(theme_data)}")
        else:
           # Insert the document if it doesn't exist
            result = collection.insert_one(template)
            print(f"Document inserted with _id: {result.inserted_id}")

