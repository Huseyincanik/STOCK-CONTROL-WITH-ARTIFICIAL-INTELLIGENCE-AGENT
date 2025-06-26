# STOCK-CONTROL-WITH-ARTIFICIAL-INTELLIGENCE-AGENT
**Crypto Agent & Trader**

Bu proje, sosyal medya akışlarını ve geleceğe yönelik fiyat tahminlerini kullanarak otomatik XRP-TRY alım/satım işlemleri gerçekleştiren bir kripto ajanıdır. Google Gemini (Gemini 2.0) ve LangChain entegrasyonu ile gerçek zamanlı tweet analizi, OKX TR API üzerinden emir gönderme ve WhatsApp bildirimleri gibi kapsamlı özellikler sunar.

---

## 📂 Proje Yapısı

```
├── Agent_Control.py          # Tweet analiz ve anlık trade ajanı
├── Trade_at_model.py        # Günlük bazlı tahminlere göre trade scripti
├── XRP_Predict_for_run.ipynb     # Fiyat tahmin modeli not defteri
├── Additional_signal.ipynb       # Ek sinyal üretme not defteri
├── requirements.txt         # Gerekli Python kütüphaneleri
├── future_predictions.csv   # Model çıktısı (günlük fiyat tahmini)
├── agent.log                # Agent log dosyası
├── okx_trader.log           # Trade_at_model log dosyası
└── info_secret.json         # API anahtarları ve kimlik bilgileri
```

---

## 🔑 Özellikler

### 1. Gerçek Zamanlı Tweet Analizi & Trade (Agent\_Control.py)

* **Tweepy V2** kullanarak kendi Twitter hesabınızdan yeni tweetleri periyodik (6 dakikalık) aralıklarla kontrol eder.
* **Google Gemini (Gemini 2.0)** ile her tweeti analiz ederek:

  * XRP veya Bitcoin ile ilgili olup olmadığını belirler.
  * Tweet metnindeki olumlu/olumsuz sinyale göre alım (`buy`) veya satım (`sell`) kararı verir.
* **OKX TR API** üzerinden piyasa emri (`market order`) gönderir; HMAC SHA256 imzası ile güvenlik protokolü uygular.
* **WhatsApp Bildirimi**: Her başarılı işlem için belirtilen numaraya `pywhatkit` ile mesaj gönderir.
* **Logging**: `agent.log` dosyasında bilgi ve uyarılar detaylı biçimde kaydedilir.

### 2. Günlük Tahmine Dayalı Trade (Trade\_at\_model.py)

* `future_predictions.csv` dosyasındaki **bugün** ve **dün** tarihli fiyat tahminlerini karşılaştırır.
* Fiyat yükselişi bekleniyorsa **alım** (buy), düşüş bekleniyorsa **satım** (sell) emri gönderir.
* Emir sonrası WhatsApp ile alım/satım mesajı gönderir.
* **Zamanlama**: `schedule` kütüphanesi ile her gün `22:40`'ta otomatik çalışır.
* **Logging**: `okx_trader.log` dosyasında günlük işlem kayıtları tutulur.

### 3. Fiyat Tahmin Modelleri (Jupyter Notebooks)

* **XRP\_Predict\_for\_run.ipynb**: Zaman serisi modelleri (örneğin LSTM, ARIMA vb.) ile geleceğe yönelik XRP-TRY fiyat tahminleri üretir.
* **Additional\_signal.ipynb**: Teknik analiz (RSI, MACD vb.) ve ek makine öğrenimi sinyallerini hesaplar.
* Model çıktısı `future_predictions.csv` biçiminde kaydedilir.

---

## 🛠️ Gereksinimler

* Python 3.9+
* Aşağıdaki kütüphaneler (requirements.txt içerisinde listelenmiştir):

  * tweepy
  * langchain-google-genai
  * langchain-core
  * requests
  * pandas
  * schedule
  * pywhatkit
  * hmac, hashlib, base64, json, datetime
  * jupyterlab (notebooks için)

---

## 🚀 Kurulum & Çalıştırma

1. **Depoyu klonlayın**

```bash
git clone https://github.com/kullaniciadi/crypto-agent-trader.git
cd crypto-agent-trader
```

2. **Sanal ortam oluşturun** (opsiyonel ama önerilir)

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\\Scripts\\activate  # Windows
```

3. **Gereksinimleri yükleyin**

```bash
pip install -r requirements.txt
```

4. **Konfigürasyon dosyasını oluşturun**

* `info_secret.json` dosyasını proje köküne yerleştirin ve aşağıdaki şablonu doldurun:

  ```json
  {
    "api_key": "TWITTER_API_KEY",
    "api_secret": "TWITTER_API_SECRET",
    "access_token": "TWITTER_ACCESS_TOKEN",
    "access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
    "BEARER_TOKEN": "TWITTER_BEARER_TOKEN",
    "GOOGLE_API_KEY": "GOOGLE_GEMINI_API_KEY",
    "OKX_API_KEY": "OKX_API_KEY",
    "OKX_API_SECRET": "OKX_API_SECRET",
    "OKX_PASSPHRASE": "OKX_PASSPHRASE"
  }
  ```

5. **Notebook'ları çalıştırın**

* Fiyat tahmin modeli:

  ```bash
  jupyter lab XRP_Predict_for_run.ipynb
  ```
* Ek sinyaller:

  ```bash
  jupyter lab Additional_signal.ipynb
  ```
* Model çıktısını `future_predictions.csv` olarak kaydedin.

6. **Ajanı başlatın**

```bash
python Agent_Control.py
```

* Bu script, tweetleri izleyip işlem ve bildirim gönderimini sürekli yapar.

7. **Günlük trade scripti**

```bash
python Trade_at_model.py
```

* Otomatik zamanlama `schedule` ile ayarlanmıştır, elle de tetikleyebilirsiniz.

---

## ⚙️ Yapılandırma & Özelleştirme

* `interval` parametresini `Agent_Control.py` içinde değiştirilerek tweet kontrol sıklığı ayarlanabilir (varsayılan: 360 saniye).
* `schedule.every().day.at("baslatilacak_saat")` satırı ile günlük trade zamanlaması güncellenebilir.
* Tahmin modellerinin parametreleri ve sinyal eşikleri `XRP_Predict_for_run.ipynb` ve `Additional_signal.ipynb` içinde özelleştirilebilir.
* `QUANTITY` değişkeni ile işlem adeti ayarlanabilir.

---









# STOCK-CONTROL-WITH-ARTIFICIAL-INTELLIGENCE-AGENT
**Crypto Agent & Trader**

This project is a crypto agent that performs automatic XRP-TRY buy/sell transactions using social media feeds and future price predictions. It offers comprehensive features such as real-time tweet analysis with Google Gemini (Gemini 2.0) and LangChain integration, order submission via OKX TR API, and WhatsApp notifications.

---

## 📂 Project Structure

```
├── Agent_Control.py # Tweet analysis and instant trade agent
├── Trade_at_model.py # Trading script based on daily predictions
├── XRP_Predict_for_run.ipynb # Price prediction model notebook
├── Additional_signal.ipynb # Additional signal generation notebook
├── requirements.txt # Required Python libraries
├── future_predictions.csv # Model output (daily price prediction)
├── agent.log # Agent log file
├── okx_trader.log # Trade_at_model log file
└── info_secret.json # API keys and identity information
```

---

## 🔑 Features

### 1. Real-Time Tweet Analysis & Trade (Agent\_Control.py)

* Checks new tweets from your own Twitter account periodically (6 minutes) using **Tweepy V2**.

* Analyzes each tweet with **Google Gemini (Gemini 2.0)** and:

* Determines whether it is related to XRP or Bitcoin.

* Makes a buy or sell decision based on the positive/negative signal in the tweet text.

* Sends market order via **OKX TR API**; applies security protocol with HMAC SHA256 signature.

* **WhatsApp Notification**: Sends a message to the specified number with `pywhatkit` for each successful transaction.

* **Logging**: Information and alerts are recorded in detail in the `agent.log` file.

### 2. Daily Prediction Based Trade (Trade\_at\_model.py)

* Compares the price predictions of **today** and **yesterday** in the `future_predictions.csv` file.

* Sends a **buy** order if the price is expected to increase, and a **sell** order if the price is expected to decrease.

* Sends a buy/sell message via WhatsApp after the order.

* **Timing**: Runs automatically at `22:40` every day with the `schedule` library.

* **Logging**: Daily transaction records are kept in the `okx_trader.log` file.

### 3. Price Prediction Models (Jupyter Notebooks)

* **XRP\_Predict\_for\_run.ipynb**: Produces future XRP-TRY price predictions with time series models (e.g. LSTM, ARIMA, etc.).
* **Additional\_signal.ipynb**: Calculates technical analysis (RSI, MACD etc.) and additional machine learning signals.
* Model output is saved in `future_predictions.csv` format.

---

## 🛠️ Requirements

* Python 3.9+
* The following libraries (listed in requirements.txt):

* tweepy
* langchain-google-genai
* langchain-core
* requests
* pandas
* schedule
* pywhatkit
* hmac, hashlib, base64, json, datetime
* jupyterlab (for notebooks)

---

## 🚀 Installation & Operation

1. **Clone the repository**

```bash
git clone https://github.com/kullaniciadi/crypto-agent-trader.git
cd crypto-agent-trader
```

2. **Create a virtual environment** (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\\Scripts\\activate # Windows
```

3. **Install requirements**

```bash
pip install -r requirements.txt
```

4. **Create the configuration file**

* Place the `info_secret.json` file in the project root and fill in the following template:

```json
{
"api_key": "TWITTER_API_KEY",
"api_secret": "TWITTER_API_SECRET",
"access_token": "TWITTER_ACCESS_TOKEN",
"access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
"BEARER_TOKEN": "TWITTER_BEARER_TOKEN",
"GOOGLE_API_KEY": "GOOGLE_GEMINI_API_KEY",
"OKX_API_KEY": "OKX_API_KEY",
"OKX_API_SECRET": "OKX_API_SECRET",
"OKX_PASSPHRASE": "OKX_PASSPHRASE"
}
```

5. **Run the notebooks**

* Price prediction model:

```bash
jupyter lab XRP_Predict_for_run.ipynb
```
* Additional signals:

```bash
jupyter lab Additional_signal.ipynb
```
* Save the model output as `future_predictions.csv`.

6. **Start the agent**

```bash
python Agent_Control.py
```

* This script continuously monitors tweets and sends actions and notifications.

7. **Daily trade script**

```bash
python Trade_at_model.py
```

* Automatic schedule is set with `schedule`, you can also trigger it manually.

---

## ⚙️ Configuration & Customization

* Tweet check frequency can be set by changing `interval` parameter in `Agent_Control.py` (default: 360 seconds).

* Daily trade schedule can be updated with `schedule.every().day.at("start_hour")` line.

* Parameters of forecast models and signal thresholds can be customized in `XRP_Predict_for_run.ipynb` and `Additional_signal.ipynb`.

* Trade quantity can be set with `QUANTITY` variable.

---
