import time
from datetime import datetime, timedelta
import requests

# Başlangıç ve bitiş tarihleri için zaman damgalarını hesapla
today = datetime.today()
ten_years_ago = today - timedelta(days=365 * 10)
period1 = int(time.mktime(ten_years_ago.timetuple()))
period2 = int(time.mktime(today.timetuple()))

# Yahoo Finance indirme URL'sini oluştur
url = f"https://query1.finance.yahoo.com/v7/finance/download/XRP-USD?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"

# CSV dosyasını indir
response = requests.get(url)

# Verileri XRP.csv dosyasına kaydetme
with open("XRP.csv", "wb") as f:
    f.write(response.content)

print("XRP'nin geçmiş verileri XRP.csv dosyasına kaydedildi.")