from fastapi import FastAPI
import requests
import json
import time

app = FastAPI()

import os

API_KEY = os.getenv("apikey")

API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
CACHE = None
LAST_FETCH_TIME = None
CACHE_TTL = 86400

def fetch_exchange_rates():
    """Fetch the exchange rates from the API."""
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_cached_rates():
    """Return cached rates if they exist and are not expired."""
    global CACHE, LAST_FETCH_TIME

    if CACHE is None or (time.time() - LAST_FETCH_TIME) > CACHE_TTL:
        rates_data = fetch_exchange_rates()
        if rates_data:
            CACHE = rates_data
            LAST_FETCH_TIME = time.time() 
        else:
            return {"error": "Failed to fetch exchange rates"}
    
    return CACHE

@app.get("/exchange-rates")
async def get_exchange_rates():
    """Endpoint to fetch the exchange rates."""
    rates = get_cached_rates()
    return rates

@app.get("/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Endpoint to convert currency from one to another."""
    rates = get_cached_rates()

    if "error" in rates:
        return {"error": "Failed to fetch exchange rates"}

    try:
        from_rate = rates["conversion_rates"][from_currency]
        to_rate = rates["conversion_rates"][to_currency]
        converted_amount = amount * (to_rate / from_rate)
        converted_amount = str(converted_amount)
        return {"converted_amount": converted_amount}
    except KeyError:
        return {"error": "Invalid currency code"}
