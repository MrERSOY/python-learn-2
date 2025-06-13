import tkinter as tk
from tkinter import simpledialog
import os

# --- Sabitler ---
GECMIS_DOSYASI = "hesap_gecmisi.txt"

# --- Global Değişkenler ---
toplam_yuzde = 0
yuzde_gecmisi = []

# --- Dosya İşlemleri Fonksiyonları ---


def dosyayi_kaydet(dosya_adi, veri_listesi):
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            for item in veri_listesi:
                f.write(str(item) + "\n")
    except IOError as e:
        print(f"HATA: {dosya_adi} dosyasına yazılamadı. {e}")


def gecmisi_yukle():
    if not os.path.exists(GECMIS_DOSYASI):
        return
    try:
        with open(GECMIS_DOSYASI, "r", encoding="utf-8") as f:
            for satir in f:
                gecmis_listbox.insert(tk.END, satir.strip())
    except IOError as e:
        print(f"HATA: Geçmiş dosyası okunamadı. {e}")

# --- Hesaplama ve Arayüz Fonksiyonları ---


def fontlari_yeniden_boyutlandir(event=None):
    """Pencere yeniden boyutlandırıldığında fontları orantılı olarak ayarlar."""
    pencere_yuksekligi = pencere.winfo_height()

    # Pencere yüksekliğine göre orantılı font boyutları hesapla (minimum boyutlar belirlendi)
    ekran_font_boyutu = max(12, int(pencere_yuksekligi / 18))
    buton_font_boyutu = max(8, int(pencere_yuksekligi / 32))
    panel_baslik_font = max(9, int(pencere_yuksekligi / 45))
    panel_icerik_font = max(8, int(pencere_yuksekligi / 50))
    # DEĞİŞİKLİK: Yüzdelik butonları için daha büyük font oranı
    yuzde_buton_fontu = max(9, int(pencere_yuksekligi / 42))

    # Widget'ların fontlarını güncelle
    ekran.config(font=('Segoe UI', ekran_font_boyutu))
    for widget in buton_cercevesi.winfo_children():
        widget.config(font=('Segoe UI Semibold', buton_font_boyutu))

    on_top_checkbutton.config(font=('Segoe UI', panel_icerik_font))
    yuzde_cercevesi.config(font=('Segoe UI', panel_baslik_font))
    toplam_yuzde_etiketi.config(font=('Segoe UI', panel_baslik_font, 'bold'))

    # DEĞİŞİKLİK: Yüzde ve aksiyon butonları için özel font boyutu kullan
    for widget in yuzde_buton_cercevesi.winfo_children():
        widget.config(font=('Segoe UI', yuzde_buton_fontu))
    for widget in aksiyon_buton_cercevesi.winfo_children():
        widget.config(font=('Segoe UI', yuzde_buton_fontu))

    yuzde_sonuc_etiketi.config(font=('Segoe UI', panel_baslik_font))
    gecmis_cercevesi.config(font=('Segoe UI', panel_baslik_font))
    gecmis_listbox.config(font=('Segoe UI', panel_icerik_font))


def toggle_always_on_top():
    pencere.attributes("-topmost", always_on_top_var.get())


def yuzdeyi_hesapla(*args):
    mevcut_metin = ekran_degiskeni.get()
    try:
        sayi = float(mevcut_metin)
        yuzde_sonuc = sayi * (toplam_yuzde / 100.0)
        yuzde_sonuc_etiketi.config(text=f"Sonuç: {yuzde_sonuc:.2f}")
    except (ValueError, TypeError):
        yuzde_sonuc_etiketi.config(text="Sonuç: -")


def yuzde_ekle(oran):
    global toplam_yuzde
    toplam_yuzde += oran
    yuzde_gecmisi.append(oran)
    toplam_yuzde_etiketi.config(text=f"Toplam Yüzde: %{toplam_yuzde}")
    yuzdeyi_hesapla()


def yuzde_sifirla():
    global toplam_yuzde
    toplam_yuzde = 0
    yuzde_gecmisi.clear()
    toplam_yuzde_etiketi.config(text=f"Toplam Yüzde: %{toplam_yuzde}")
    yuzdeyi_hesapla()


def yuzde_geri_al():
    global toplam_yuzde
    if yuzde_gecmisi:
        son_eklenen = yuzde_gecmisi.pop()
        toplam_yuzde -= son_eklenen
        toplam_yuzde_etiketi.config(text=f"Toplam Yüzde: %{toplam_yuzde}")
        yuzdeyi_hesapla()


def butona_tikla(karakter):
    mevcut_metin = ekran.get()
    if str(karakter) in "+-*/" and mevcut_metin and mevcut_metin[-1] in "+-*/":
        return
    if str(karakter) == '.':
        son_op_idx = max(mevcut_metin.rfind(op) for op in "+-*/")
        if '.' in mevcut_metin[son_op_idx+1:]:
            return
    ekran.delete(0, tk.END)
    ekran.insert(0, mevcut_metin + str(karakter))


def hesapla():
    ifade = ekran.get()
    if not ifade:
        return
    try:
        sonuc = eval(ifade)
        ekran.delete(0, tk.END)
        ekran.insert(0, str(sonuc))
        gecmis_yazisi = f"{ifade} = {sonuc}"
        gecmis_listbox.insert(0, gecmis_yazisi)
        dosyayi_kaydet(GECMIS_DOSYASI, gecmis_listbox.get(0, tk.END))
    except ZeroDivisionError:
        ekran.delete(0, tk.END)
        ekran.insert(0, "Sıfıra Bölünemez")
    except Exception:
        ekran.delete(0, tk.END)
        ekran.insert(0, "Hatalı İfade")


def temizle():
    ekran.delete(0, tk.END)


def geri_al():
    ekran.delete(0, tk.END)
    ekran.insert(0, ekran.get()[:-1])


def klavye_girisi(event):
    key = event.keysym
    char = event.char
    if char.isdigit() or char in ['+', '-', '*', '/', '.']:
        butona_tikla(char)
    elif key in ['Return', 'KP_Enter']:
        hesapla()
    elif key == 'Escape':
        temizle()
    elif key == 'BackSpace':
        geri_al()


# --- ANA PENCERE VE YAPI ---
pencere = tk.Tk()
pencere.title("Hesap Makinesi")
pencere.minsize(550, 450)  # Minimum boyut belirledik
pencere.configure(bg='#3c3c3c')

# Ana pencerenin satır ve sütunlarını orantılı büyümeye ayarlıyoruz
pencere.grid_rowconfigure(0, weight=1)
pencere.grid_columnconfigure(0, weight=1)
pencere.grid_columnconfigure(1, weight=2)

always_on_top_var = tk.BooleanVar()

hesap_makinesi_cercevesi = tk.Frame(pencere, padx=10, pady=10, bg='#3c3c3c')
# "nsew" ile hücreyi doldur
hesap_makinesi_cercevesi.grid(row=0, column=0, sticky="nsew")

yan_panel_cercevesi = tk.Frame(pencere, padx=10, pady=10, bg='#2a2a2a')
# "nsew" ile hücreyi doldur
yan_panel_cercevesi.grid(row=0, column=1, sticky="nsew")

# --- HESAP MAKİNESİ WIDGET'LARI ---
hesap_makinesi_cercevesi.grid_rowconfigure(0, weight=1)
hesap_makinesi_cercevesi.grid_rowconfigure(1, weight=4)
hesap_makinesi_cercevesi.grid_columnconfigure(0, weight=1)

ekran_degiskeni = tk.StringVar()
ekran_degiskeni.trace_add("write", yuzdeyi_hesapla)
ekran = tk.Entry(hesap_makinesi_cercevesi, textvariable=ekran_degiskeni,
                 bd=0, relief="flat", justify="right", bg='#3c3c3c', fg='white')
ekran.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)

buton_cercevesi = tk.Frame(hesap_makinesi_cercevesi, bg='#3c3c3c')
buton_cercevesi.grid(row=1, column=0, sticky="nsew")

butonlar = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('C', 4, 2), ('+', 4, 3),
    ('←', 5, 0), ('=', 5, 1)
]

for i in range(6):
    buton_cercevesi.grid_rowconfigure(i, weight=1)
for i in range(4):
    buton_cercevesi.grid_columnconfigure(i, weight=1)

for (metin, satir, sutun) in butonlar:
    if metin.isdigit() or metin == '.':
        renk_bg, renk_active, renk_fg = '#505050', '#686868', 'white'
    elif metin in '/*-+':
        renk_bg, renk_active, renk_fg = '#ff9500', '#fbac47', 'white'
    else:
        renk_bg, renk_active, renk_fg = '#d4d4d2', '#e8e8e7', 'black'

    def cmd(m=metin): return butona_tikla(m)
    if metin == '=':
        cmd = hesapla
        renk_bg, renk_active = '#ff9500', '#fbac47'
    elif metin == 'C':
        cmd = temizle
    elif metin == '←':
        cmd = geri_al

    b = tk.Button(buton_cercevesi, text=metin, bg=renk_bg, fg=renk_fg,
                  activebackground=renk_active, activeforeground=renk_fg, bd=0, command=cmd)
    colspan = 3 if metin == '=' else 1
    b.grid(row=satir, column=sutun, columnspan=colspan,
           sticky="nsew", padx=1, pady=1)

# --- YAN PANEL WIDGET'LARI ---
yan_panel_cercevesi.grid_rowconfigure(0, weight=0)
yan_panel_cercevesi.grid_rowconfigure(1, weight=1)
yan_panel_cercevesi.grid_rowconfigure(2, weight=2)
yan_panel_cercevesi.grid_columnconfigure(0, weight=1)

on_top_checkbutton = tk.Checkbutton(
    yan_panel_cercevesi, text="Hep Üstte Tut", variable=always_on_top_var,
    command=toggle_always_on_top, bg='#2a2a2a', fg='white',
    selectcolor='#505050', activebackground='#2a2a2a', activeforeground='white'
)
on_top_checkbutton.grid(row=0, column=0, sticky='w', pady=(0, 5))

yuzde_cercevesi = tk.LabelFrame(
    yan_panel_cercevesi, text="Yüzde Toplama", padx=5, pady=5, bg='#2a2a2a', fg='white', bd=1)
yuzde_cercevesi.grid(row=1, column=0, sticky='nsew', pady=5)

toplam_yuzde_etiketi = tk.Label(
    yuzde_cercevesi, text="Toplam Yüzde: %0", bg='#2a2a2a', fg='white')
toplam_yuzde_etiketi.pack(pady=(0, 5))

yuzde_buton_cercevesi = tk.Frame(yuzde_cercevesi, bg='#2a2a2a')
yuzde_buton_cercevesi.pack(pady=5)
oran_butonlari = [5, 10, 20, 25, 50, 75]

for i, oran in enumerate(oran_butonlari):
    # DEĞİŞİKLİK: Yüzde butonlarının genişliği artırıldı.
    btn = tk.Button(yuzde_buton_cercevesi, text=f"%{oran}", width=6, command=lambda o=oran: yuzde_ekle(
        o), bd=0, bg='#505050', fg='white', activebackground='#686868')
    btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)

aksiyon_buton_cercevesi = tk.Frame(yuzde_cercevesi, bg='#2a2a2a')
aksiyon_buton_cercevesi.pack(pady=(5, 0))
geri_al_butonu = tk.Button(aksiyon_buton_cercevesi, text="Geri Al", command=yuzde_geri_al,
                           bd=0, bg='#505050', fg='white', activebackground='#686868')
geri_al_butonu.pack(side=tk.LEFT, padx=5)
sifirla_butonu = tk.Button(aksiyon_buton_cercevesi, text="Sıfırla", command=yuzde_sifirla,
                           bd=0, bg='#505050', fg='white', activebackground='#686868')
sifirla_butonu.pack(side=tk.LEFT, padx=5)

yuzde_sonuc_etiketi = tk.Label(
    yuzde_cercevesi, text="Sonuç: -", bg='#2a2a2a', fg='white')
yuzde_sonuc_etiketi.pack(pady=5)

gecmis_cercevesi = tk.LabelFrame(
    yan_panel_cercevesi, text="İşlem Geçmişi", padx=5, pady=5, bg='#2a2a2a', fg='white', bd=1)
gecmis_cercevesi.grid(row=2, column=0, sticky='nsew', pady=5)
gecmis_cercevesi.grid_rowconfigure(0, weight=1)
gecmis_cercevesi.grid_columnconfigure(0, weight=1)
scrollbar = tk.Scrollbar(gecmis_cercevesi, bd=0)
scrollbar.grid(row=0, column=1, sticky='ns')
gecmis_listbox = tk.Listbox(gecmis_cercevesi, yscrollcommand=scrollbar.set,
                            bg='#3c3c3c', fg='white', bd=0, highlightthickness=0, selectbackground='#505050')
gecmis_listbox.grid(row=0, column=0, sticky='nsew')
scrollbar.config(command=gecmis_listbox.yview)

# --- UYGULAMAYI BAŞLATMA ---
pencere.bind("<Configure>", fontlari_yeniden_boyutlandir)
pencere.bind("<Key>", klavye_girisi)
gecmisi_yukle()
pencere.mainloop()
