from flask import Flask, request, render_template, jsonify
import yfinance as yf
import pmdarima as pm
from datetime import date
import requests
import json
import smtplib

app = Flask(__name__)

import logging

# Configure Flask app logging
app.logger.setLevel(logging.INFO)  # Set the desired logging level
handler = logging.FileHandler("/var/log/wowfingpt/flask.log")  # Specify the Flask log file
handler.setLevel(logging.INFO)  # Set the desired logging level for Flask
app.logger.addHandler(handler)

def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start_date, end_date)
    data.reset_index(inplace=True)
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/use')
def use():
    return render_template('use.html')

@app.route('/whitepaper')
def example():
    return render_template('whitepaper.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/predict', methods=['GET'])
def predict():
    symbol = request.args.get('symbol')
    days = int(request.args.get('days'))
    
    end_date = date.today().strftime("%Y-%m-%d")
    start_date = '2018-01-01'
    
    data = load_data(symbol, start_date, end_date)
    auto_arima_close = pm.auto_arima(data['Close'], stepwise=False, seasonal=False)
    auto_arima_open = pm.auto_arima(data['Open'], stepwise=False, seasonal=False)
    auto_arima_low = pm.auto_arima(data['Low'], stepwise=False, seasonal=False)
    forecast_close = auto_arima_close.predict(n_periods=days)
    forecast_open = auto_arima_open.predict(n_periods=days)
    forecast_low = auto_arima_low.predict(n_periods=days)
    
    return jsonify({'close': forecast_close.tolist(), 'open': forecast_open.tolist(), 'low': forecast_low.tolist()})

@app.route("/chat/<prompt>")
def chat_data(prompt):
    text = json.loads(requests.get("http://vamsishaik.pythonanywhere.com/prompt?user="+prompt).content)['response']
    return text

@app.route("/mail", methods=["POST"])
def send_mail():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'codewithsam110g@gmail.com'

    # Gmail account credentials
    gmail_username = 'codewithsam110g@gmail.com'
    gmail_password = 'jyjypahyogheoylx'

    # Extract data from the form
    name = request.form.get('name')
    email = request.form.get('email')
    message_content = request.form.get('message')

    # Construct the email body
    subject = f'White Paper requested by {name}'
    body = f'Name: {name}\nEmail: {email}\nMessage: {message_content}'

    TO = "beautiful110g@gmail.com"
    BODY = '\r\n'.join(['To: %s' % TO,
                                'From: %s' % sender_email,
                                'Subject: %s' % subject,
                                '', body])

    try:
        # Establish a connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)

        server.ehlo()
        server.starttls()

        # Login to your Gmail account
        server.login(gmail_username, gmail_password)

        # Send the email
        server.sendmail(sender_email, "train@wowexp.ai", BODY)

        # Quit the server
        server.quit()

        return "Email sent successfully!"

    except Exception as e:
        return f"An error occurred: {e}"
