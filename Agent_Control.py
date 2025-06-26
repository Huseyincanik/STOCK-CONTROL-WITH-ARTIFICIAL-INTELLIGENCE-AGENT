import tweepy
import logging
import time
import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import datetime
import time
import pywhatkit
import hmac
import hashlib
import base64

# Logging yapılandırması
logging.basicConfig(filename="agent.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Agent başlatıldı")

with open('info_secret.json', 'r') as file:
    config = json.load(file)
    api_key = config['api_key']
    api_secret = config['api_secret']
    access_token = config['access_token']
    BEARER_TOKEN = config['BEARER_TOKEN']
    access_token_secret = config['access_token_secret']
    GOOGLE_API_KEY = config['GOOGLE_API_KEY']
    OKX_API_KEY = config['OKX_API_KEY']
    OKX_API_SECRET = config['OKX_API_SECRET']
    OKX_PASSPHRASE = config['OKX_PASSPHRASE']
    
                               
hedef_numara = "+905313298461"


# Tweepy Client ile V2 API'sine bağlanın
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# LangChain ve Google Gemini ayarları
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Daha güncel bir model kullanıyorum
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# LangChain prompt şablonu (daha kesin JSON çıktısı için)
prompt = PromptTemplate(
    input_variables=["tweet"],
    template="""Bu tweet XRP veya Bitcoin ile ilgili mi? Eğer öyleyse, alım mı satım mı yapılmalı? 
Tweet: {tweet}
Cevap formatı: ```json
{{"is_relevant": true/false, "action": "buy"/"sell"/""}}
```
- Eğer tweet XRP veya Bitcoin'den bahsediyorsa, is_relevant=true olmalı.
- Alım için olumlu bir ifade (örneğin, "rise", "bullish") varsa action="buy", satış için olumsuz bir ifade (örneğin, "fall", "bearish") varsa action="sell" olmalı.
- Eğer tweet ilgili değilse veya net bir alım/satım sinyali yoksa, action="" olmalı.
Örnek:
```json
{{"is_relevant": true, "action": "buy"}}
```"""
)

# RunnableSequence oluştur
chain = RunnableSequence(prompt | llm)

def place_order(symbol, side, quantity):
    # Zaman damgasını milisaniye cinsinden oluştur (OKX gereksinimi)
    timestamp = str(int(time.time() * 1000))
    
    try:
        url = "https://www.okx.com/api/v5/trade/order"
        
        # İstek verisi
        data = {
            "instId": symbol,
            "tdMode": "cash",
            "side": side,
            "ordType": "market",
            "sz": str(quantity)
        }
        
        # İmza oluşturma (OKX'in zorunlu kıldığı güvenlik adımı)
        message = timestamp + "POST" + "/api/v5/trade/order" + json.dumps(data, separators=(',', ':'))
        signature = hmac.new(
            bytes(OKX_API_SECRET, 'utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        headers = {
            "OK-ACCESS-KEY": OKX_API_KEY,
            "OK-ACCESS-SIGN": signature_b64,  # Dinamik olarak oluşturulan imza
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        # Hızlı yanıt kontrolü
        if response.status_code != 200:
            logging.warning(f"OKX TR uyarı: {response.status_code} - {response.text}")
            
        response_data = response.json()
        logging.info(f"OKX TR işlem sonucu: {response_data}")
        return response_data
        
    except Exception as e:
        logging.error(f"OKX TR işlem hatası: {e}")
        print(f"OKX TR işlem hatası: {e}")
        return None



def mesaj_gonder(xrp_adet:float):
    simdi = datetime.datetime.now()
    mesaj = f"{xrp_adet} adet XRP alım yapılıyor"
    gonderilecek_saat = simdi.hour
    gonderilecek_dakika = simdi.minute + 1
    try:
        pywhatkit.sendwhatmsg(hedef_numara, mesaj, gonderilecek_saat, gonderilecek_dakika)
        print("Mesaj gönderildi")
        print(mesaj)
    except Exception as e:
        print(f"Mesaj gönderilirken hata oluştu: {e}")

# Tweet analizi ve işlem yapma
def analyze_and_trade(tweet_text):
    try:
        # Gemini'den yanıtı al
        response = chain.invoke({"tweet": tweet_text}).content

        # Yanıtı JSON olarak parse et
        try:
            # JSON bloğunu temizle (```json ve ``` kısımlarını kaldır)
            if response.startswith("```json") and response.endswith("```"):
                response = response[7:-3].strip()
            result = json.loads(response)
        except json.JSONDecodeError as e:
            logging.error(f"JSON parse hatası: {response}")
            print(f"JSON parse hatası: {response}")
            return {"is_relevant": False, "action": ""}

        # Yanıtın doğru formatta olduğundan emin ol
        if not isinstance(result, dict) or "is_relevant" not in result:
            logging.error(f"Geçersiz yanıt formatı: {result}")
            print(f"Geçersiz yanıt formatı: {result}")
            return {"is_relevant": False, "action": ""}

        if result.get("is_relevant", False):
            xrp_adet=1                     
            action = result.get("action", "").lower()
            if action in ["buy", "sell"]:
                
                place_order("XRP-TRY", action, xrp_adet)  
                logging.info(f"{action.capitalize()} emri verildi: {tweet_text}")
                print(f"{action.capitalize()} emri verildi: {tweet_text}")
                mesaj_gonder(xrp_adet)       #Whatsapp mesaji gidecek
            else:
                logging.info(f"Geçersiz işlem: {action} | Tweet: {tweet_text}")
                print(f"Geçersiz işlem: {action} | Tweet: {tweet_text}")
        else:
            logging.info(f"İlgisiz tweet: {tweet_text}")
            print(f"İlgisiz tweet: {tweet_text}")
    except Exception as e:
        logging.error(f"Tweet analiz hatası: {e}")
        print(f"Tweet analiz hatası: {e}")

# Kendi tweetlerini periyodik olarak kontrol etme
def check_tweets_periodically(interval):  # interval saniye cinsinden (örneğin, 300 saniye = 5 dakika)
    last_tweet_id = None
    while True:
        try:
            # Kendi kullanıcı kimliğinizi (ID) alın
            me = client.get_me()
            my_id = me.data.id

            # Kendi tweetlerinizi çekin (en az 5 tweet döner, en yenisi ilk sırada)
            tweets = client.get_users_tweets(id=my_id, max_results=5)

            if tweets.data:
                latest_tweet = tweets.data[0]
                if last_tweet_id is None or latest_tweet.id > last_tweet_id:
                    last_tweet_id = latest_tweet.id
                    print(f"En son tweet: {latest_tweet.text}")
                    analyze_and_trade(latest_tweet.text)
                else:
                    print("Yeni tweet yok.")
            else:
                print("Tweet bulunamadı.")
        except tweepy.errors.Unauthorized as e:
            logging.error(f"Kimlik doğrulama hatası: {e}")
            print(f"Kimlik doğrulama hatası: {e}")
        except Exception as e:
            logging.error(f"Bir hata oluştu: {e}")
            print(f"Bir hata oluştu: {e}")

        # Belirli bir süre bekle
        time.sleep(interval)

# Ana işlem
if __name__ == "__main__":
    check_tweets_periodically(interval=360)  # Her 6 dakikada bir kontrol et


























# import tweepy
# import logging
# import time
# import requests
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from langchain.chains import LLMChain

# # Logging yapılandırması
# logging.basicConfig(filename="agent.log", level=logging.INFO, 
#                     format="%(asctime)s - %(levelname)s - %(message)s")
# logging.info("Agent başlatıldı")


# api_key = "okiXaU6Ex8Kkb5JEwIK60Zbzb"                                  #X
# api_secret = "3HCmXfe1fqFMAAkjlFRI8fZy8T9jomOaPehzPQkMkXYrrkcQ0Q"      #X
# access_token = "1935011846571839494-13h7cim4olLXQeiuV0P4ADSdEaMF7R"    #X
# access_token_secret = "v28uuvWEhKWVdZMAnpAX9egYXT8NNxGf3TpLxhVTldFgX"  #X
# BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIs12gEAAAAA%2BJ%2B4q3EwCm4CHtz9%2BpoCJntZwU4%3DL6q63cUlax4D5UKuhfSXsUcbjY8LfKHfqlylfKlCdwkeNQfvRI" # developer X
# GOOGLE_API_KEY = "AIzaSyClBs8Q8d7H9-H7rylrL6DFNUpErCW0rOA"  #google gemini
# OKX_API_KEY = "67c4409b-6ebd-4738-bd3c-0c556e55879e"        #okx
# OKX_API_SECRET = "EC877847A62A853490D3A1E51FECB66D"         #okx
# OKX_PASSPHRASE = "101339Hh!"                                #okx

# # Tweepy Client ile V2 API'sine bağlanın
# client = tweepy.Client(
#     bearer_token=BEARER_TOKEN,
#     consumer_key=api_key,
#     consumer_secret=api_secret,
#     access_token=access_token,
#     access_token_secret=access_token_secret
# )

# # LangChain ve Google Gemini ayarları
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=GOOGLE_API_KEY,
#     temperature=0.7
# )

# # LangChain prompt şablonu
# prompt = PromptTemplate(
#     input_variables=["tweet"],
#     template="Bu tweet XRP veya BitCoin ile ilgili mi? Eğer öyleyse, alım mı satım mı yapılmalı? Tweet: {tweet}\nCevap formatı: {'is_relevant': bool, 'action': str}"
# )

# # LLM zinciri oluştur
# chain = LLMChain(llm=llm, prompt=prompt)

# # OKX TR API ile emir verme fonksiyonu (Basitleştirilmiş)
# def place_order(symbol, side, quantity):
#     try:
#         url = "https://www.okx.com/api/v5/trade/order"
#         headers = {
#             "OK-ACCESS-KEY": OKX_API_KEY,
#             "OK-ACCESS-SIGN": OKX_API_SECRET,  # Gerçek uygulamada imza oluşturmanız gerekir
#             "OK-ACCESS-TIMESTAMP": str(int(time.time())),
#             "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE
#         }
#         data = {
#             "instId": symbol,  # Örneğin: "XRP-USDT"
#             "tdMode": "cash",
#             "side": side,  # "buy" veya "sell"
#             "ordType": "market",
#             "sz": str(quantity)  # İşlem miktarı
#         }
#         response = requests.post(url, headers=headers, json=data)
#         response_data = response.json()
#         logging.info(f"OKX TR işlem sonucu: {response_data}")
#         print(f"OKX TR işlem sonucu: {response_data}")
#         return response_data
#     except Exception as e:
#         logging.error(f"OKX TR işlem hatası: {e}")
#         print(f"OKX TR işlem hatası: {e}")
#         return None

# # Tweet analizi ve işlem yapma
# def analyze_and_trade(tweet_text):
#     try:
#         response = chain.run(tweet=tweet_text)
#         # Gemini yanıtını parse et (JSON benzeri format bekleniyor)
#         import json
#         result = json.loads(response)
#         if result.get("is_relevant", False):
#             action = result.get("action", "").lower()
#             if action in ["buy", "sell"]:
#                 place_order("XRP-USDT", action, 0)  
#                 logging.info(f"{action.capitalize()} emri verildi: {tweet_text}")
#                 print(f"{action.capitalize()} emri verildi: {tweet_text}")
#             else:
#                 logging.info(f"Geçersiz işlem: {action} | Tweet: {tweet_text}")
#                 print(f"Geçersiz işlem: {action} | Tweet: {tweet_text}")
#         else:
#             logging.info(f"İlgisiz tweet: {tweet_text}")
#             print(f"İlgisiz tweet: {tweet_text}")
#     except Exception as e:
#         logging.error(f"Tweet analiz hatası: {e}")
#         print(f"Tweet analiz hatası: {e}")

# # Kendi tweetlerini periyodik olarak kontrol etme
# def check_tweets_periodically(interval=300):  # interval saniye cinsinden (örneğin, 300 saniye = 5 dakika)
#     last_tweet_id = None
#     while True:
#         try:
#             # Kendi kullanıcı kimliğinizi (ID) alın
#             me = client.get_me()
#             my_id = me.data.id

#             # Kendi tweetlerinizi çekin (en az 5 tweet döner, en yenisi ilk sırada)
#             tweets = client.get_users_tweets(id=my_id, max_results=5)

#             if tweets.data:
#                 latest_tweet = tweets.data[0]
#                 if last_tweet_id is None or latest_tweet.id > last_tweet_id:
#                     last_tweet_id = latest_tweet.id
#                     print(f"En son tweet: {latest_tweet.text}")
#                     analyze_and_trade(latest_tweet.text)
#                 else:
#                     print("Yeni tweet yok.")
#             else:
#                 print("Tweet bulunamadı.")
#         except tweepy.errors.Unauthorized as e:
#             logging.error(f"Kimlik doğrulama hatası: {e}")
#             print(f"Kimlik doğrulama hatası: {e}")
#         except Exception as e:
#             logging.error(f"Bir hata oluştu: {e}")
#             print(f"Bir hata oluştu: {e}")

#         # Belirli bir süre bekle
#         time.sleep(interval)

# # Ana işlem
# if __name__ == "__main__":
#     check_tweets_periodically(interval=300)  # Her 5 dakikada bir kontrol et