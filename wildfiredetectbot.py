import ee
import datetime
import requests
import os

ee.Initialize(project='fire-detection-project-503313')

TOKEN = '8769666205:AAEcsdRqhR5TBYqFNl7pL3BUUie_FxVoQXU'
CHAT_ID = os.environ.get('7304456993')

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def check_fires():
    end_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    firms = ee.ImageCollection('FIRMS') \
      .filterDate(start_date, end_date) \
      .select('T21')
      
    landCover = ee.Image('MODIS/006/MCD12Q1/20200101').select('LC_Type1')
    forestMask = landCover.gte(1).And(landCover.lte(5))
    
    count = firms.size().getInfo()
    
    if count > 0:
        first_fire = firms.first()
        try:
            centroid = first_fire.geometry().centroid().coordinates().getInfo()
            lon = centroid[0]
            lat = centroid[1]
        except:
            lon, lat = 0.0, 0.0
            
        maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
        alert_msg = (
            f"🌲🔥 *အရေးပေါ် တောမီးလောင်ကျွမ်းမှု သတိပေးချက်* \n\n"
            f"📍 *လတ္တီကျု:* {lat}\n"
            f"📍 *လောင်ဂျီကျု:* {lon}\n"
            f"🔢 *တွေ့ရှိရသည့် Hotspots:* {count} ခု\n\n"
            f"🗺️ [Google Maps တွင် ကြည့်ရန်]({maps_link})"
        )
        send_telegram_alert(alert_msg)
    else:
        no_fire_msg = (
            f"🛡️ *တောမီးစောင့်ကြည့်ရေး အခြေအနေ* \n\n"
            f"✅ လွန်ခဲ့သော ၂၄ နာရီအတွင်း အရေးပေါ် တောမီးလောင်ကျွမ်းမှု မရှိပါ။ (တစ်နာရီတစ်ကြိမ် အလိုအလျောက် စစ်ဆေးနေသည်)"
        )
        send_telegram_alert(no_fire_msg)

if __name__ == '__main__':
    check_fires()
