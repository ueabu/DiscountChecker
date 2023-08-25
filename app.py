from flask import Flask, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from twilio.rest import Client
import config
from enum import Enum
import json


app = Flask(__name__)
app.config.from_object(config.Config)


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

    for item in new_entry_json:
        if 'ASIN' in item:
            handle_amazon_entry(item)          

    return "OK"


def handle_amazon_entry(new_entry):
    ref = db.reference('Amazon')
    amazon_ref = ref.child(new_entry['ASIN'])
    amazon_ref_data = amazon_ref.get()

    if amazon_ref_data is None:
        add_new_amazon_entry(new_entry)
        create_notification(Notification_type.CREATION, new_entry, current_entry=None)
    else:
        if(discount_present(amazon_ref_data['price'], new_entry['finalPrice']['value'])):
            create_notification(Notification_type.UPDATE, new_entry, amazon_ref_data)
            update_amazon_entry(new_entry)
    
    
def add_new_amazon_entry(new_entry):
    amazon_db_ref = db.reference('Amazon')
    amazon_db_ref_child = amazon_db_ref.child(new_entry['ASIN'])
    amazon_db_ref_child.set({
        'price': new_entry['finalPrice']['value'],
        'title': new_entry['title'],
        'url': new_entry['input']['url'],
        'image': new_entry['image']
    });

def update_amazon_entry(new_entry):
    amazon_db_ref = db.reference('Amazon')
    amazon_db_ref_child = amazon_db_ref.child(new_entry['ASIN'])
    amazon_db_ref_child.update({
        'price': new_entry['finalPrice']['value'],
    });

def create_notification(notification_type, new_entry, current_entry):
    if notification_type == Notification_type.CREATION:
        message_body = f'A new item has been added to the database!\n \nIts the : {new_entry["title"]}, {new_entry["input"]["url"]}'
        send_notification(message_body)
    elif notification_type == Notification_type.UPDATE:
        previous_price = current_entry["price"]
        new_price = new_entry['finalPrice']['value']
        price_difference = previous_price - new_price
        percentage_difference = round((price_difference / previous_price) * 100)
        message_body = f'Price Drop Alert 🚨 🚨 🚨\n \n{new_entry["title"]} \nhas dropped from ${current_entry["price"]} to ${new_entry["finalPrice"]["value"]}. ${price_difference} ({percentage_difference}%) drop\n \n{new_entry["input"]["url"]} '
        send_notification(message_body)
    else:
        print("Invalid notification type")

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
