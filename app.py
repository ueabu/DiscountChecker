from flask import Flask, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from twilio.rest import Client
import config
from enum import Enum
import json
import logging
 

app = Flask(__name__)
app.config.from_object(config.Config)
logger = logging.getLogger()


# Fetch the service account key JSON file contents
cred = credentials.Certificate(json.loads(app.config['SERVICE_ACCOUNT']))
# Initialize the app with a service account, granting admin privileges

firebase_admin.initialize_app(cred, {
    'databaseURL': app.config['DATABASE_URL']
})

#TWILLO ACCOUNT
# Your Account SID from twilio.com/console
twilo_account_sid = app.config['TWILO_ACCOUNT_SID']
# Your Auth Token from twilio.com/console
twilo_auth_token  = app.config['TWILO_AUTH_TOKEN']

@app.route('/')
def index():
    return 'Up and Running!'

@app.route('/checkdiscount', methods = ['POST'])
def check_discount_entry():
    
    new_entry_json = request.json
    logging.info(new_entry_json)

    for item in new_entry_json:
        if 'ASIN' in item:
            print('Amazon Item')
            handle_amazon_entry(item)
        elif 'sku' in item and 'ikea' in item['input']['url']:
            print('Ikea Item')
            handle_ikea_entry(item)
        elif 'sku' in item and 'walmart' in item['input']['url']:
            print('Walmart Item')
            handle_walmart_entry(item)
        elif 'ebay' in item['product_url']:
            print('Ebay Item')
            handle_ebay_search(item) 
    return "OK"

def handle_amazon_entry(new_entry):
    ref = db.reference('Amazon')
    amazon_ref = ref.child(new_entry['ASIN'])
    amazon_ref_data = amazon_ref.get()
    if amazon_ref_data is None:
        add_new_amazon_entry(new_entry)
        create_notification_amazon(Notification_type.CREATION, new_entry, current_entry=None)
    else:
        if(discount_present(amazon_ref_data['price'], new_entry['finalPrice']['value'])):
            create_notification_amazon(Notification_type.UPDATE, new_entry, amazon_ref_data)
            update_amazon_entry(new_entry)  


def handle_ikea_entry(new_entry):
    ref = db.reference('Ikea')
    ikea_ref = ref.child(new_entry['sku'])
    ikea_ref_data = ikea_ref.get()
    if ikea_ref_data is None:
        add_new_ikea_entry(new_entry)
        create_notification_ikea(Notification_type.CREATION, new_entry, current_entry=None)
    else:
        if(discount_present(ikea_ref_data['price'], new_entry['final_price']['value'])):
            create_notification_ikea(Notification_type.UPDATE, new_entry, ikea_ref_data)
            update_ikea_entry(new_entry)


def handle_walmart_entry(new_entry):
    ref = db.reference('Walmart')
    walmart_ref = ref.child(new_entry['sku'])
    walmart_ref_data = walmart_ref.get()
    if walmart_ref_data is None:
        add_new_walmart_entry(new_entry)
        create_notification_walmart(Notification_type.CREATION, new_entry, current_entry=None)
    else:
        if(discount_present(walmart_ref_data['price'], new_entry['final_price']['value'])):
            create_notification_walmart(Notification_type.UPDATE, new_entry, walmart_ref_data)
            update_walmart_entry(new_entry)

def handle_ebay_search(new_entry):
    total_price = new_entry['price']['value'] + new_entry['shipping_price']['value']

    if(total_price < 500 and new_entry['listing_type'] == 'buy it now' and new_entry['condition'] == 'Good - Refurbished'):
        create_notification_ebay_search(new_entry)

    
def add_new_amazon_entry(new_entry):
    amazon_db_ref = db.reference('Amazon')
    amazon_db_ref_child = amazon_db_ref.child(new_entry['ASIN'])
    amazon_db_ref_child.set({
        'price': new_entry['finalPrice']['value'],
        'title': new_entry['title'],
        'url': new_entry['input']['url'],
        'image': new_entry['image']
    })

def add_new_ikea_entry(new_entry):
    ikea_ref = db.reference('Ikea')
    ikea_ref_child = ikea_ref.child(new_entry['sku'])
    ikea_ref_child.set({
        'price': new_entry['final_price']['value'],
        'title': new_entry['model_name'],
        'url': new_entry['input']['url'],
        'image': new_entry['image_urls']
    })


def add_new_walmart_entry(new_entry):
    walmart_ref = db.reference('Walmart')
    walmart_ref_child = walmart_ref.child(new_entry['sku'])
    walmart_ref_child.set({
        'price': new_entry['final_price']['value'],
        'title': new_entry['product_name'],
        'url': new_entry['input']['url'],
        'image': new_entry['main_image']
    })

def update_amazon_entry(new_entry):
    amazon_db_ref = db.reference('Amazon')
    amazon_db_ref_child = amazon_db_ref.child(new_entry['ASIN'])
    amazon_db_ref_child.update({
        'price': new_entry['finalPrice']['value'],
    })

def update_ikea_entry(new_entry):
    ikea_ref = db.reference('Ikea')
    ikea_ref_child = ikea_ref.child(new_entry['sku'])
    ikea_ref_child.update({
        'price': new_entry['final_price']['value'],
    })

def update_walmart_entry(new_entry):
    walmart_ref = db.reference('Walmart')
    walmart_ref_child = walmart_ref.child(new_entry['sku'])
    walmart_ref_child.update({
        'price': new_entry['final_price']['value'],
    })

def create_notification_amazon(notification_type, new_entry, current_entry):
    if notification_type == Notification_type.CREATION:
        message_body = f'A new item has been added to the database!\n \nIts the : {new_entry["title"]}, {new_entry["input"]["url"]}'
        send_notification(message_body)
    elif notification_type == Notification_type.UPDATE:
        previous_price = current_entry["price"]
        new_price = new_entry['finalPrice']['value']
        price_difference = round(previous_price - new_price)
        percentage_difference = round((price_difference / previous_price) * 100)
        message_body = f'Price Drop Alert 🚨 🚨 🚨\n \n{new_entry["title"]} \nhas dropped from ${current_entry["price"]} to ${new_entry["finalPrice"]["value"]}. ${price_difference} ({percentage_difference}%) drop\n \n{new_entry["input"]["url"]} '
        send_notification(message_body)
    else:
        print("Invalid notification type")


def create_notification_ikea(notification_type, new_entry, current_entry):
    if notification_type == Notification_type.CREATION:
        message_body = f'A new item has been added to the database!\n \nIts the : {new_entry["model_name"]}, {new_entry["input"]["url"]}'
        send_notification(message_body)
    elif notification_type == Notification_type.UPDATE:
        previous_price = current_entry["price"]
        new_price = new_entry['final_price']['value']
        price_difference = previous_price - new_price
        percentage_difference = round((price_difference / previous_price) * 100)
        message_body = f'Price Drop Alert 🚨 🚨 🚨\n \n{new_entry["model_name"]} \nhas dropped from ${current_entry["price"]} to ${new_entry["final_price"]["value"]}. ${price_difference} ({percentage_difference}%) drop\n \n{new_entry["input"]["url"]} '
        send_notification(message_body)
    else:
        print("Invalid notification type")

def create_notification_walmart(notification_type, new_entry, current_entry):
    if notification_type == Notification_type.CREATION:
        message_body = f'A new item has been added to the database!\n \nIts the : {new_entry["product_name"]}, {new_entry["input"]["url"]}'
        send_notification(message_body)
    elif notification_type == Notification_type.UPDATE:
        previous_price = current_entry["price"]
        new_price = new_entry['final_price']['value']
        price_difference = previous_price - new_price
        percentage_difference = round((price_difference / previous_price) * 100)
        message_body = f'🚨 🚨 🚨\n \n{new_entry["product_name"]} ${new_entry["final_price"]["value"]}. \n{new_entry["input"]["url"]} '
        send_notification(message_body)
    else:
        print("Invalid notification type")

def create_notification_ebay_search(new_entry):

    message_body = f'New Entry for {new_entry["input"]["keyword"]} \n Price:  {new_entry["price"]["value"]} \n Shipping: {new_entry["shipping_price"]["value"]} \n Condition: {new_entry["condition"]} \n \n {new_entry["product_url"]}'
    send_notification(message_body)

def discount_present(initial_price, todays_price):
    if(todays_price < initial_price):
        return True
    else:
        return False




def send_notification(message_body):
    client = Client(twilo_account_sid, twilo_auth_token)
    message = client.messages.create(
        from_= app.config['TWILO_FROM_NUMBER'],
        body=message_body,
        to=app.config['TWILO_TO_NUMBER']
    )

class Notification_type(Enum):
    CREATION = 1
    UPDATE = 2
