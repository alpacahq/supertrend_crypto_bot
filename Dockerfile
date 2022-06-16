FROM python:3.7.6

ADD crypto_bot.py .

RUN pip install alpaca-trade-api

CMD [ "python", "./crypto_bot.py" ]