import random


print("--- Sayı Tahmin Oyununa Hoş Geldiniz! ---")
print("1 ile 100 arasında bir sayı tuttum. Bakalım bulabilecek misin?")

rastgele_sayi = random.randint(1, 100)


tahmin_sayisi = 0

while True:
    kullanici_tahmini = input("Tahmininiz: ")

    try:
        kullanici_tahmini = int(kullanici_tahmini)

        tahmin_sayisi = tahmin_sayisi + 1
    except ValueError:
        print("Lütfen sadece sayı giriniz!")
        continue

    if kullanici_tahmini < rastgele_sayi:
        print("Daha YÜKSEK bir sayı söylemelisin.")
    elif kullanici_tahmini > rastgele_sayi:
        print("Daha DÜŞÜK bir sayı söylemelisin.")
    else:
        print(f"🎉 Tebrikler! {rastgele_sayi} sayısını doğru tahmin ettin.")
        print(f"Toplam {tahmin_sayisi} denemede buldun.")
        break
