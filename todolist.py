gorevler = []

print("Basit görev listesi uygulamasına hoş geldiniz!")
while True:
    print("\nLütfen yapmak istediğiniz işlemi seçin:")
    print("1. Görev Ekle")
    print("2. Görevleri Listele")
    print("3. Görev Sil")
    print("4. Çıkış")

    secim = input("Seçiminiz (1-4): ")

    if secim == "1":
        yeni_gorev = input("Eklenecek görevi girin: ")
        gorevler.append(yeni_gorev)
        print(f"'{yeni_gorev}' görevi eklendi.")
    elif secim == "2":
        print("Yapılacak Görevler:")
        if not gorevler:
            print("Görev listesi boş.")
        else:
            for index, gorev in enumerate(gorevler, start=1):
                print(f"{index}. {gorev}")
    elif secim == "3":
        print("Silmek istediğiniz görevi seçin:")
        if not gorevler:
            print("Silinecek görev yok.")
        else:
            for index, gorev in enumerate(gorevler, start=1):
                print(f"{index}. {gorev}")
            try:
                silinecek_no = int(
                    input("Silinecek görevin numarasını girin: "))
                if 1 <= silinecek_no <= len(gorevler):
                    silinen_gorev = gorevler.pop(silinecek_no - 1)
                    print(f"'{silinen_gorev}' görevi silindi.")
                else:
                    print("Geçersiz görev numarası.")
            except ValueError:
                print("Lütfen geçerli bir sayı girin.")
    elif secim == "4":
        print("Çıkış yapılıyor. Hoşça kal!")
        break
    else:
        print("Geçersiz seçim. Lütfen 1-4 arasında bir sayı girin.")
