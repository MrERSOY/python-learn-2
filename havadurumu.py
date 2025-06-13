import requests


def get_sehir_koordinatlari(sehir_adi):
    """
    Bir şehir adını coğrafi koordinatlara (enlem ve boylam) çevirir.
    Open-Meteo, hava durumu için koordinatları tercih eder.
    """
    # Geocoding API'si bir şehrin koordinatlarını bulmamızı sağlar.
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={sehir_adi}&count=1&language=tr&format=json"
    try:
        response = requests.get(geocoding_url)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            location = data['results'][0]
            return location['latitude'], location['longitude'], location.get('admin1', '')
        else:
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Şehir koordinatları alınırken hata oluştu: {e}")
        return None, None, None


def get_weather_data(latitude, longitude):
    """
    Verilen koordinatlar için Open-Meteo API'sinden anlık hava durumu verilerini çeker.
    """
    # API'nin adresi. Hangi verileri istediğimizi (sıcaklık, nem vs.) URL'de belirtiyoruz.
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code"

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Hava durumu verisi alınırken hata oluştu: {e}")
        return None


def hava_durumunu_goster(data, city, bolge):
    """
    Alınan hava durumu verisini kullanıcıya okunaklı bir şekilde gösterir.
    """
    if data:
        current_weather = data['current']
        sicaklik = current_weather['temperature_2m']
        hissedilen_sicaklik = current_weather['apparent_temperature']
        nem = current_weather['relative_humidity_2m']

        # Open-Meteo, hava durumunu WMO kodları ile verir. Bunu metne çevirmemiz gerekir.
        weather_code = current_weather['weather_code']
        aciklama = wmo_code_to_text(weather_code)

        print("\n--- Hava Durumu Bilgisi (Open-Meteo) ---")
        print(f"Şehir: {city.capitalize()}, {bolge}")
        print(f"Sıcaklık: {sicaklik}°C")
        print(f"Hissedilen Sıcaklık: {hissedilen_sicaklik}°C")
        print(f"Durum: {aciklama}")
        print(f"Nem: %{nem}")
        print("-----------------------------------------")


def wmo_code_to_text(code):
    """ WMO hava durumu kodlarını okunabilir metne çevirir. """
    codes = {
        0: "☀️ Açık", 1: "🌤️ Genellikle açık", 2: "⛅ Parçalı bulutlu", 3: "☁️ Çok bulutlu",
        45: "🌫️ Sis", 48: "🌫️ Kırağılı sis",
        51: "🌧️ Hafif çiseleme", 53: "🌧️ Orta şiddette çiseleme", 55: "🌧️ Yoğun çiseleme",
        61: "🌦️ Hafif yağmurlu", 63: "🌧️ Orta şiddette yağmur", 65: "🌧️ Yoğun yağmur",
        71: "🌨️ Hafif kar yağışlı", 73: "🌨️ Orta şiddette kar yağışlı", 75: "❄️ Yoğun kar yağışlı",
        80: "🌦️ Hafif sağanak yağmur", 81: "🌧️ Orta şiddette sağanak yağmur", 82: "⛈️ Şiddetli sağanak yağmur",
        95: "⛈️ Gök gürültülü fırtına"
    }
    return codes.get(code, "Bilinmeyen hava durumu")


# --- ANA PROGRAM BLOGU ---
if __name__ == "__main__":
    sehir_adi = input(
        "Hava durumunu öğrenmek istediğiniz şehri yazın: ").strip()

    if sehir_adi:
        lat, lon, bolge = get_sehir_koordinatlari(sehir_adi)
        if lat and lon:
            weather_data = get_weather_data(lat, lon)
            hava_durumunu_goster(weather_data, sehir_adi, bolge)
        else:
            print(f"'{sehir_adi}' şehri için konum bilgisi bulunamadı.")
    else:
        print("Lütfen bir şehir adı giriniz.")

    # --- YENİ EKLENEN SATIR ---
    # Bu satır, programın kullanıcı Enter'a basana kadar beklemesini sağlar.
    input("\nKapatmak için Enter tuşuna basın...")
