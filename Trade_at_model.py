import pandas as pd
import requests
import hmac
import hashlib
import base64
import time
import logging
import schedule
import json
import datetime
import time
import pywhatkit
from datetime import datetime,timedelta

# Logging yapılandırması
logging.basicConfig(filename="okx_trader.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("OKX Trader başlatıldı")

# OKX API kimlik bilgileri
with open('info_secret.json', 'r') as file:
    config = json.load(file)
    OKX_API_KEY = config['OKX_API_KEY']
    OKX_API_SECRET = config['OKX_API_SECRET']
    OKX_PASSPHRASE = config['OKX_PASSPHRASE']                               #okx

# CSV dosyasının yolu
CSV_FILE_PATH = "future_predictions.csv"
hedef_numara = "+905313298461"

# Alım veya satım yapılacak sembol ve miktar
SYMBOL = "XRP-TRY"
QUANTITY = 1  # İşlem miktarı (örneğin, 1 XRP)

#OKX API ile emir verme fonksiyonu
def place_order(side):
    try:
        url = "https://www.okx.com/api/v5/trade/order"
        timestamp = str(int(time.time()))
        method = "POST"
        body = {
            "instId": SYMBOL,
            "tdMode": "cash",
            "side": side,
            "ordType": "market",
            "sz": str(QUANTITY)
        }
        body_str = json.dumps(body)
        sign_str = timestamp + method + "/api/v5/trade/order" + body_str
        sign = base64.b64encode(hmac.new(OKX_API_SECRET.encode(), sign_str.encode(), hashlib.sha256).digest()).decode()
        headers = {
            "OK-ACCESS-KEY": OKX_API_KEY,
            "OK-ACCESS-SIGN": sign,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=body_str)
        response_data = response.json()
        
        
        logging.info(f"OKX TR işlem sonucu: {response_data}")
        return response_data
    except Exception as e:
        logging.error(f"OKX TR işlem hatası: {e}")
        print(f"OKX TR işlem hatası: {e}")
        return None

def alim_mesaji_gonder(xrp_adet:float):
    simdi = datetime.now()
    mesaj = f"{xrp_adet} adet XRP alım yapılıyor"
    gonderilecek_saat = simdi.hour
    gonderilecek_dakika = simdi.minute + 1
    try:
        pywhatkit.sendwhatmsg(hedef_numara, mesaj, gonderilecek_saat, gonderilecek_dakika)
        print("Mesaj gönderildi")
        print(mesaj)
    except Exception as e:
        print(f"Mesaj gönderilirken hata oluştu: {e}")

def satim_mesaji_gonder(xrp_adet:float):
    simdi = datetime.now()
    mesaj = f"{xrp_adet} adet XRP satım yapılıyor"
    gonderilecek_saat = simdi.hour
    gonderilecek_dakika = simdi.minute + 1
    try:
        pywhatkit.sendwhatmsg(hedef_numara, mesaj, gonderilecek_saat, gonderilecek_dakika)
        print("Mesaj gönderildi")
        print(mesaj)
    except Exception as e:
        print(f"Mesaj gönderilirken hata oluştu: {e}")

def get_today_prediction():
    try:
        df = pd.read_csv(CSV_FILE_PATH, parse_dates=["Date"])
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Bugünün ve dünün tahminlerini al
        today_pred = df[df["Date"].dt.date == today]
        yesterday_pred = df[df["Date"].dt.date == yesterday]
        
        if today_pred.empty or yesterday_pred.empty:
            logging.warning("Bugün veya dün için tahmin bulunamadı.")
            print("Bugün veya dün için tahmin bulunamadı.")
            return None, None
        
        today_price = today_pred.iloc[0]["Price"]
        yesterday_price = yesterday_pred.iloc[0]["Price"]
        return today_price, yesterday_price
    except Exception as e:
        logging.error(f"CSV okuma hatası: {e}")
        print(f"CSV okuma hatası: {e}")
        return None, None


# Günlük işlem fonksiyonu
def daily_trade():
    today_price, yesterday_price = get_today_prediction()
    if today_price is None or yesterday_price is None:
        return
    
    if today_price > yesterday_price:
        logging.info("Günlük bazda fiyat yükselişi bekleniyor, alım emri veriliyor.")
        print("Günlük bazda fiyat yükselişi bekleniyor, alım emri veriliyor.")
        place_order("buy")
        alim_mesaji_gonder(QUANTITY)
    elif today_price < yesterday_price:
        logging.info("Günlük bazda fiyat düşüşü bekleniyor, satım emri veriliyor.")
        print("Günlük bazda fiyat düşüşü bekleniyor, satım emri veriliyor.")
        place_order("sell")
        satim_mesaji_gonder(QUANTITY)
    else:
        logging.info("Fiyat değişimi yok, işlem yapılmıyor.")
        print("Fiyat değişimi yok, işlem yapılmıyor.")


schedule.every().day.at("21:46").do(daily_trade)

# Zamanlayıcıyı çalıştır
while True:
    schedule.run_pending()
    time.sleep(15)  #günlük baz