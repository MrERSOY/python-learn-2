import tkinter as tk
from tkinter import ttk
from deep_translator import GoogleTranslator
import requests
import threading
try:
    import pyttsx3
    TTS_ENABLED = True
except ImportError:
    TTS_ENABLED = False

# --- Dil Listesi ---
LANGUAGES = {
    'Türkçe': 'tr', 'İngilizce': 'en', 'Almanca': 'de', 'Fransızca': 'fr',
    'İspanyolca': 'es', 'Rusça': 'ru', 'Arapça': 'ar', 'Japonca': 'ja', 'İtalyanca': 'it'
}
LANGUAGE_NAMES = list(LANGUAGES.keys())

# --- Global Değişkenler ---
ceviri_zamanlayici = None
tts_engine = None

# --- Fonksiyonlar ---


def init_tts():
    """Text-to-Speech motorunu başlatır."""
    global tts_engine
    if TTS_ENABLED and tts_engine is None:
        try:
            tts_engine = pyttsx3.init()
        except Exception as e:
            print(f"TTS başlatılamadı: {e}")
            return False
    return TTS_ENABLED


def speak_text_thread():
    """Giriş metnini ayrı bir thread'de seslendirir."""
    global tts_engine
    if not init_tts():
        update_status("Metin okuma özelliği (pyttsx3) kurulu değil.")
        return

    # HATA DÜZELTMESİ: Motor meşgulse yeni bir okuma başlatmayı engelle
    if tts_engine.isBusy():
        update_status("Zaten bir metin okunuyor...")
        return

    text_to_speak = giris_kutusu.get("1.0", tk.END).strip()
    if text_to_speak:
        try:
            update_status("Okunuyor...")
            tts_engine.say(text_to_speak)
            tts_engine.runAndWait()
            update_status("Okuma tamamlandı.")
        except Exception as e:
            update_status(f"Okuma hatası: {e}")


def speak_text():
    threading.Thread(target=speak_text_thread).start()


def copy_to_clipboard(box):
    """Belirtilen metin kutusunun içeriğini panoya kopyalar."""
    text = box.get("1.0", tk.END).strip()
    if text:
        pencere.clipboard_clear()
        pencere.clipboard_append(text)
        update_status("Metin panoya kopyalandı!")


def clear_input():
    giris_kutusu.delete("1.0", tk.END)


def sozluk_bilgisini_al(kelime):
    """Ücretsiz bir API üzerinden bir İngilizce kelimenin sözlük bilgisini alır."""
    def worker():
        try:
            update_status(f"'{kelime}' aranıyor...")
            response = requests.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{kelime}")
            response.raise_for_status()
            data = response.json()[0]

            sozluk_kutusu.config(state=tk.NORMAL)
            sozluk_kutusu.delete("1.0", tk.END)

            sozluk_kutusu.insert(tk.END, f"{data.get('word', kelime)}", "word")
            if data.get('phonetic'):
                sozluk_kutusu.insert(
                    tk.END, f"  {data.get('phonetic')}\n\n", "phonetic")
            else:
                sozluk_kutusu.insert(tk.END, "\n\n")

            for anlam in data.get('meanings', []):
                kelime_turu = anlam.get('partOfSpeech', 'Bilinmiyor')
                sozluk_kutusu.insert(
                    tk.END, f"{kelime_turu.capitalize()}\n", "part_of_speech")

                for i, tanim in enumerate(anlam.get('definitions', []), 1):
                    sozluk_kutusu.insert(
                        tk.END, f"  {i}. {tanim.get('definition')}\n", "definition")

                synonyms = anlam.get('synonyms', [])
                if synonyms:
                    sozluk_kutusu.insert(
                        tk.END, f"  Eşanlamlılar: ", "synonym_header")
                    sozluk_kutusu.insert(
                        tk.END, f"{', '.join(synonyms[:5])}\n", "synonym")

                sozluk_kutusu.insert(tk.END, "\n")

            sozluk_kutusu.config(state=tk.DISABLED)
            update_status(f"'{kelime}' kelimesi bulundu.")

        except requests.exceptions.HTTPError:
            sozluk_kutusu.config(state=tk.NORMAL)
            sozluk_kutusu.delete("1.0", tk.END)
            sozluk_kutusu.insert(
                "1.0", f"'{kelime}' kelimesi sözlükte bulunamadı.")
            update_status("Kelime bulunamadı.")
        except Exception as e:
            sozluk_kutusu.config(state=tk.NORMAL)
            sozluk_kutusu.delete("1.0", tk.END)
            sozluk_kutusu.insert(
                "1.0", f"Sözlük verisi alınırken bir hata oluştu.")
            update_status("Sözlük hatası.")

    threading.Thread(target=worker).start()


def ceviriyi_gerceklestir():
    giris_metni = giris_kutusu.get("1.0", tk.END).strip()
    kaynak_dil_adi = kaynak_dil_combobox.get()
    hedef_dil_adi = hedef_dil_combobox.get()

    kaynak_kodu = LANGUAGES.get(kaynak_dil_adi)
    if ' ' not in giris_metni and giris_metni and kaynak_kodu == 'en':
        sozluk_bilgisini_al(giris_metni)
    else:
        sozluk_kutusu.config(state=tk.NORMAL)
        sozluk_kutusu.delete("1.0", tk.END)
        sozluk_kutusu.config(state=tk.DISABLED)

    if not giris_metni:
        sonuc_kutusu.delete("1.0", tk.END)
        update_status("Hazır.")
        return

    if not kaynak_dil_adi or not hedef_dil_adi or kaynak_dil_adi == hedef_dil_adi:
        sonuc_kutusu.delete("1.0", tk.END)
        sonuc_kutusu.insert("1.0", giris_metni)
        return

    try:
        sonuc_kutusu.delete("1.0", tk.END)
        sonuc_kutusu.insert("1.0", "Çevriliyor...")
        update_status("Çevriliyor...")
        pencere.update_idletasks()

        hedef_kodu = LANGUAGES[hedef_dil_adi]
        ceviri = GoogleTranslator(
            source=kaynak_kodu, target=hedef_kodu).translate(giris_metni)

        sonuc_kutusu.delete("1.0", tk.END)
        sonuc_kutusu.insert("1.0", ceviri)
        update_status("Çeviri tamamlandı.")
    except Exception as e:
        sonuc_kutusu.delete("1.0", tk.END)
        sonuc_kutusu.insert("1.0", f"Çeviri hatası oluştu.")
        update_status("Çeviri hatası.")


def zamanlayiciyi_baslat(event=None):
    global ceviri_zamanlayici
    if ceviri_zamanlayici:
        pencere.after_cancel(ceviri_zamanlayici)
    ceviri_zamanlayici = pencere.after(500, ceviriyi_gerceklestir)


def dilleri_degistir():
    kaynak_dil, hedef_dil = kaynak_dil_combobox.get(), hedef_dil_combobox.get()
    sonuc_metni = sonuc_kutusu.get("1.0", tk.END).strip()

    kaynak_dil_combobox.set(hedef_dil)
    hedef_dil_combobox.set(kaynak_dil)

    if "Çevriliyor..." not in sonuc_metni:
        giris_kutusu.delete("1.0", tk.END)
        giris_kutusu.insert("1.0", sonuc_metni)

    zamanlayiciyi_baslat()


def update_status(message):
    status_bar.config(text=message)


# --- ANA PENCERE VE YAPI ---
pencere = tk.Tk()
pencere.title("Dil Asistanı (Çeviri & Sözlük)")
pencere.geometry("900x700")
pencere.minsize(700, 500)
pencere.configure(bg='#2d2d2d')

style = ttk.Style()
style.theme_use('clam')
style.configure('TCombobox', fieldbackground='#3c3c3c', background='#3c3c3c',
                foreground='white', bordercolor='#505050', arrowcolor='white')
style.map('TCombobox', fieldbackground=[('readonly', '#3c3c3c')])
style.configure('TPanedwindow', background='#2d2d2d')

# --- ARAYÜZ ELEMANLARI ---
# Üst Çerçeve: Dil Seçimi
ust_cerceve = tk.Frame(pencere, bg='#2d2d2d', pady=10)
ust_cerceve.pack(fill=tk.X)
ust_cerceve.grid_columnconfigure((0, 2), weight=1)
kaynak_dil_combobox = ttk.Combobox(
    ust_cerceve, values=LANGUAGE_NAMES, state='readonly', font=('Segoe UI', 12))
kaynak_dil_combobox.set('İngilizce')
kaynak_dil_combobox.grid(row=0, column=0, padx=20, pady=5)
kaynak_dil_combobox.bind("<<ComboboxSelected>>", zamanlayiciyi_baslat)
degistir_butonu = tk.Button(ust_cerceve, text="↔", font=('Segoe UI', 14, 'bold'),
                            command=dilleri_degistir, bg='#505050', fg='white', bd=0, activebackground='#686868')
degistir_butonu.grid(row=0, column=1, padx=10)
hedef_dil_combobox = ttk.Combobox(
    ust_cerceve, values=LANGUAGE_NAMES, state='readonly', font=('Segoe UI', 12))
hedef_dil_combobox.set('Türkçe')
hedef_dil_combobox.grid(row=0, column=2, padx=20, pady=5)
hedef_dil_combobox.bind("<<ComboboxSelected>>", zamanlayiciyi_baslat)

# Ana Çerçeve: Metin Kutuları
ana_cerceve = ttk.PanedWindow(pencere, orient=tk.HORIZONTAL)
ana_cerceve.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

# Sol Panel (Giriş)
sol_panel = tk.Frame(ana_cerceve, bg='#3c3c3c')
giris_ust_bar = tk.Frame(sol_panel, bg='#3c3c3c')
giris_ust_bar.pack(fill=tk.X, padx=5, pady=2)
speak_button = tk.Button(giris_ust_bar, text="🔊", font=(
    'Segoe UI', 12), command=speak_text, bd=0, bg='#3c3c3c', fg='#a0a0a0', activebackground='#505050')
speak_button.pack(side=tk.LEFT)
copy_input_button = tk.Button(giris_ust_bar, text="📋", font=('Segoe UI', 12), command=lambda: copy_to_clipboard(
    giris_kutusu), bd=0, bg='#3c3c3c', fg='#a0a0a0', activebackground='#505050')
copy_input_button.pack(side=tk.RIGHT)
clear_button = tk.Button(giris_ust_bar, text="❌", font=(
    'Segoe UI', 12), command=clear_input, bd=0, bg='#3c3c3c', fg='#a0a0a0', activebackground='#505050')
clear_button.pack(side=tk.RIGHT)
giris_kutusu = tk.Text(sol_panel, font=('Segoe UI', 14), bg='#3c3c3c',
                       fg='white', insertbackground='white', bd=0, relief='flat', padx=10, pady=10)
giris_kutusu.pack(fill=tk.BOTH, expand=True)
ana_cerceve.add(sol_panel, weight=1)

# Sağ Panel (Sonuç)
sag_panel = tk.Frame(ana_cerceve, bg='#3c3c3c')
sonuc_ust_bar = tk.Frame(sag_panel, bg='#3c3c3c')
sonuc_ust_bar.pack(fill=tk.X, padx=5, pady=2)
copy_output_button = tk.Button(sonuc_ust_bar, text="📋", font=('Segoe UI', 12), command=lambda: copy_to_clipboard(
    sonuc_kutusu), bd=0, bg='#3c3c3c', fg='#a0a0a0', activebackground='#505050')
copy_output_button.pack(side=tk.RIGHT)
sonuc_kutusu = tk.Text(sag_panel, font=(
    'Segoe UI', 14), bg='#3c3c3c', fg='white', bd=0, relief='flat', padx=10, pady=10)
sonuc_kutusu.pack(fill=tk.BOTH, expand=True)
ana_cerceve.add(sag_panel, weight=1)

giris_kutusu.bind("<KeyRelease>", zamanlayiciyi_baslat)

# Sözlük Çerçevesi
sozluk_cercevesi = tk.LabelFrame(pencere, text="Sözlük Bilgisi", font=(
    'Segoe UI', 12), bg='#2d2d2d', fg='white', padx=10, pady=5, bd=1, relief='solid')
sozluk_cercevesi.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 5))
sozluk_kutusu = tk.Text(sozluk_cercevesi, font=('Segoe UI', 11), bg='#3c3c3c',
                        fg='white', bd=0, relief='flat', padx=10, pady=10, wrap=tk.WORD, state=tk.DISABLED)
sozluk_kutusu.pack(fill=tk.BOTH, expand=True)

# Durum Çubuğu
status_bar = tk.Label(pencere, text="Hazır.", bd=1, relief=tk.SUNKEN,
                      anchor=tk.W, bg='#2d2d2d', fg='white', font=('Segoe UI', 10))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Sözlük kutusu için stil etiketleri
sozluk_kutusu.tag_configure("word", font=(
    'Segoe UI', 16, 'bold'), foreground="white")
sozluk_kutusu.tag_configure("phonetic", font=(
    'Segoe UI', 12, 'italic'), foreground="#a0a0a0")
sozluk_kutusu.tag_configure("part_of_speech", font=(
    'Segoe UI', 13, 'bold'), foreground="#64b5f6")  # Mavi renk
sozluk_kutusu.tag_configure("definition", font=('Segoe UI', 11), lmargin1=10)
sozluk_kutusu.tag_configure("synonym_header", font=(
    'Segoe UI', 11, 'bold'), lmargin1=10)
sozluk_kutusu.tag_configure("synonym", font=(
    'Segoe UI', 11, 'italic'), foreground="#a0a0a0", lmargin1=10)


# --- UYGULAMAYI BAŞLATMA ---
pencere.mainloop()
