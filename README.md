# DiscountChecker
An API that receives price data for an item from BrightData. It then checks to see if the stored price in the database is lower that the received price. If it is, it sends a notification via whatsapp to me!

For Code Explaination see: https://youtu.be/dcnORcRpU34

## Setting Up Locally
Requirements and Prerequistes
1. Source to get e-commerce data from. Checkout https://brdta.com/umaabu to learn more! 
2. A firebase realtime database. Follow https://firebase.google.com/ to create a firebase project then create a firebase realtime database.
3. A Twilio account for notifications. Create a Twilio account at https://www.twilio.com/en-us then create a phone number you can send SMS or Whatsapp message with. 

Create a `.env` file and add the following variables

```
DATABASE_URL = DB_URL_FROM_FIREBASE
TWILO_ACCOUNT_SID = TWILLO_ACCOUNT_SID_FROM_TWILIO
TWILO_AUTH_TOKEN = TWILLO_AUTH_TOKEN_FROM_TWILIO
TWILO_FROM_NUMBER = TWILIO_FROM_NUMBER
TWILO_TO_NUMBER = YOUR_PHONE_NUMBER

SERVICE_ACCOUNT = '{
    Service Account Data From firebase json file. 
}'
```

1. Create a virtual environment using `python3 -m venv antenv`
2. Activate the Virtual Environment Mac: `source antevn/bin/activate` Windows: `antenv/Scripts/activate`
3. Upgrade pip `python3 -m pip install --upgrade pip`
4. Install requirements in the requirements.txt file `pip install -r requirement.txt`
5. Run the app `python3 -m flask --app app.py run`

It should be running on `http://127.0.0.1:5000`.
`http://127.0.0.1:5000/` - Should return up and running is the server is up
`http://127.0.0.1:5000/checkdiscount` - The endpoint that recieves the discount data.

Happy Coding!