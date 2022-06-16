# Import Dependencies
import smtplib
import pandas as pd
import pandas_ta as ta
import alpaca_trade_api as tradeapi
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# API Credentials
API_KEY='***********'
SECRET_KEY='***********'
api = tradeapi.REST(API_KEY, SECRET_KEY,'https://paper-api.alpaca.markets')

# Define crypto related variables
symbol = 'BTCUSD'
qty_per_trade = 1

# Check Whether Account Currently Holds Symbol
def check_positions(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0

# Supertrend Indicator Bot Function
def supertrend_bot(bar):
    try:
        # Get the Latest Data
        dataframe = api.get_crypto_bars(symbol, tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Minute)).df
        dataframe = dataframe[dataframe.exchange == 'CBSE']
        sti = ta.supertrend(dataframe['high'], dataframe['low'], dataframe['close'], 7, 3)
        dataframe = pd.concat([dataframe, sti], axis=1)

        position = check_positions(symbol=symbol)
        should_buy = bar['c'] > dataframe["SUPERT_7_3.0"][-1]
        should_sell = bar['c'] < dataframe["SUPERT_7_3.0"][-1]
        print(f"Price: {bar['c']}")
        print("Super Trend Indicator: {}".format(dataframe["SUPERT_7_3.0"][-1]))
        print(f"Position: {position} | Should Buy: {should_buy}")

        # Check if No Position and Buy Signal is True
        if position == 0 and should_buy == True:
            api.submit_order(symbol, qty=qty_per_trade, side='buy')
            message = f'Symbol: {symbol} | Side: Buy | Quantity: {qty_per_trade}'
            print(message)
            # send_mail(message)

        # Check if Long Position and Sell Signal is True
        elif position > 0 and should_sell == True:
            api.submit_order(symbol, qty=qty_per_trade, side='sell')
            message = f'Symbol: {symbol} | Side: Sell | Quantity: {qty_per_trade}'
            print(message)
            # send_mail(message)
        print("-"*20)

    except Exception as e:
        print (e)
        # send_mail(f"Trading Bot failed due to {e}")

# Send an Update Email After Every Trade
def send_mail(message_text):
    # Define email related variables
    sender_email = '***********'
    sender_password = '***********'
    receiver_email = '***********'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = 'Crypto Trading Algorithm'
    message['To'] = receiver_email
    message['Subject'] = 'Supertrend Indicator Bot'

    # Add body to email and send
    mail_content = message_text
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_email, sender_password)
    text = message.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
    print ('Mail Sent')

    return {"Success": True}

# Create instance of Alpaca data streaming API
alpaca_stream = tradeapi.Stream(API_KEY, SECRET_KEY, raw_data=True, crypto_exchanges=['CBSE'])

# Create handler for receiving live bar data
async def on_crypto_bar(bar):
    print(bar)
    supertrend_bot(bar)

send_mail("Trading Bot is Live")

# Subscribe to data and assign handler
alpaca_stream.subscribe_crypto_bars(on_crypto_bar, symbol)

# Start streaming of data
alpaca_stream.run()