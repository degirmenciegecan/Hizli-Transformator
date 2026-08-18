import sys
import math

try:
    import requests
except ImportError as e:
    print("\n" + "="*60)
    print(" GEREKLI KUTUPHANELER EKSIK!")
    print("="*60)
    print(f"Hata detayi: {e}")
    print("\nLutfen baslat menusunden 'cmd' yazip Komut Istemini acin ve")
    print("asagidaki komutu yazip ENTER'a basin:")
    print("\npip install requests\n")
    print("Kurulum bittikten sonra bu programi tekrar acabilirsiniz.")
    input("\nCikmak icin ENTER'a basin...")
    sys.exit(1)

def get_metal_prices():
    """
    Yahoo Finance API kullanarak güncel LME (London Metal Exchange) bakır ve alüminyum 
    vadeli işlem (futures) fiyatlarını çeker.
    (Bakır: HG=F (USD/lb), Alüminyum: ALI=F (USD/Ton) cinsindendir. USD/kg'a çevrilir)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    prices = {"copper_usd_kg": 0.0, "aluminum_usd_kg": 0.0}
    
    print("\n" + "-"*50)
    print(" 📡 CANLI PİYASA VERİ KAYNAKLARI (YAHOO FINANCE)")
    print("-"*50)
    
    try:
        # Bakır Fiyatı (Copper - HG=F)
        url_cu = "https://query1.finance.yahoo.com/v8/finance/chart/HG=F"
        print(f"🔗 Bakır (Copper Futures) Kaynağı:\n   {url_cu}")
        response_cu = requests.get(url_cu, headers=headers, timeout=10)
        response_cu.raise_for_status()
        data_cu = response_cu.json()
        
        price_lb = data_cu['chart']['result'][0]['meta']['regularMarketPrice']
        prices["copper_usd_kg"] = price_lb / 0.453592  # 1 lb = 0.453592 kg
            
    except Exception as e:
        print(f"[Hata] Bakır fiyatı çekilirken bir sorun oluştu: {e}")
        prices["copper_usd_kg"] = 9.50
        
    try:
        # Alüminyum Fiyatı (Aluminum - ALI=F)
        url_al = "https://query1.finance.yahoo.com/v8/finance/chart/ALI=F"
        print(f"🔗 Alüminyum (Aluminum Futures) Kaynağı:\n   {url_al}")
        response_al = requests.get(url_al, headers=headers, timeout=10)
        response_al.raise_for_status()
        data_al = response_al.json()
        
        price_ton = data_al['chart']['result'][0]['meta']['regularMarketPrice']
        prices["aluminum_usd_kg"] = price_ton / 1000.0  # Fiyat USD/Ton cinsinden ise
            
    except Exception as e:
        print(f"[Hata] Alüminyum fiyatı çekilirken bir sorun oluştu: {e}")
        prices["aluminum_usd_kg"] = 2.50
        
    print("-" * 50)
    return prices

def transformer_analysis(S, V1, V2, uk, P0, Pk):
    """
    Transformatör elektriksel karakter analizini gerçekleştirir.
    S: Görünür Güç (VA)
    V1: Primer Gerilim (V)
    V2: Sekonder Gerilim (V)
    uk: Bağıl Kısa Devre Empedansı (%)
    P0: Boşta Çalışma Kaybı (W)
    Pk: Kısa Devre Kaybı (W)
    """
    print("\n" + "="*50)
    print(" 🛠️  TRANSFORMATÖR ELEKTRİKSEL KARAKTER ANALİZİ")
    print("="*50)
    
    try:
        # 1. Primer ve Sekonder Anma Akımları
        I1 = S / V1
        I2 = S / V2
        
        # 2. Sarım Oranı (a)
        a = V1 / V2
        
        # 3. Kısa Devre Test Gerilimi (Vk)
        Vk = V1 * (uk / 100.0)
        
        # 4. Eşdeğer Kısa Devre Empedansı (Zk)
        # Zk = Vk / I1 (Primer tarafına indirgenmiş)
        Zk = Vk / I1
        
        # 5. Eşdeğer Sargı Direnci (Rk)
        Rk = Pk / (I1**2)
        
        # 6. Eşdeğer Kaçak Reaktans (Xk) ve Endüktans (Lk) - 50 Hz için
        # Gerçekte Xk değeri her zaman pozitif olmalıdır. Olası ölçüm veri hatalarına karşı kontrol:
        if Zk**2 >= Rk**2:
            Xk = math.sqrt(Zk**2 - Rk**2)
        else:
            Xk = 0.0
            print("[Uyarı] Verilen kayıp değerlerine göre Rk > Zk çıkıyor. Girdi değerlerini kontrol edin.")
            
        f = 50.0 # Türkiye Şebeke Frekansı (Hz)
        Lk = Xk / (2 * math.pi * f)
        
        # 7. Tam Yük Verimi (İdeal Şebeke cosφ = 1)
        # Verim = P_çıkış / P_giriş = S / (S + P0 + Pk)
        efficiency = (S / (S + P0 + Pk)) * 100.0
        
        # Sonuçları Yazdır
        print(f"🔹 Primer Anma Akımı (I1)     : {I1:.2f} A")
        print(f"🔹 Sekonder Anma Akımı (I2)   : {I2:.2f} A")
        print(f"🔹 Sarım Oranı (a)            : {a:.4f}")
        print(f"🔹 Kısa Devre Gerilimi (Vk)   : {Vk:.2f} V")
        print(f"🔹 Eşdeğer Empedans (Zk)      : {Zk:.4f} Ω")
        print(f"🔹 Eşdeğer Direnç (Rk)        : {Rk:.4f} Ω")
        print(f"🔹 Eşdeğer Reaktans (Xk)      : {Xk:.4f} Ω")
        print(f"🔹 Eşdeğer Endüktans (Lk)     : {Lk*1000:.2f} mH")
        print(f"🔹 Tam Yük Verimi (cosφ=1)    : %{efficiency:.2f}")
        
    except Exception as e:
        print(f"[Hata] Elektriksel hesaplamalar sırasında bir hata oluştu: {e}")

def thermal_cooling_analysis(P0, Pk, oil_volume, expansion_coeff, delta_T):
    """
    Termodinamik ve soğutma (dalgalı duvar) analizini gerçekleştirir.
    """
    print("\n" + "="*50)
    print(" 🌡️  TERMODİNAMİK VE MEKANİK SOĞUTMA MODÜLÜ")
    print("="*50)
    
    try:
        # 1. Toplam Isı Kaybı
        total_heat_loss = P0 + Pk
        
        # 2. Gerekli Soğutma Yüzey Alanı (Dalgalı Duvar)
        # Standart yağlı trafolar için yüzey ısı yayılım katsayısı (h) ~ 11 W/(m^2*K) kabul edilir.
        h_dissipation = 11.0 
        required_cooling_area = total_heat_loss / (h_dissipation * delta_T)
        
        # 3. Yağ Genleşme Hesabı (Litre)
        oil_expansion_vol = oil_volume * expansion_coeff * delta_T
        
        print(f"🔹 Toplam Isı Kaybı (P0+Pk)      : {total_heat_loss:.2f} W")
        print(f"🔹 Maksimum Sıcaklık Artışı (ΔT) : {delta_T:.2f} °C")
        print(f"🔹 Minimum Soğutma Alanı İhtiyacı: {required_cooling_area:.2f} m²")
        print(f"   (Varsayılan ısı yayılım katsayısı h={h_dissipation} W/m²K baz alınmıştır)")
        print(f"🔹 Nominal Yağ Hacmi             : {oil_volume:.2f} Litre")
        print(f"🔹 Maks. Yağ Genleşme Hacmi      : {oil_expansion_vol:.2f} Litre")
        print(f"   (Kazan esneme payı bu hacmi tolere etmelidir)")
        
    except Exception as e:
        print(f"[Hata] Termodinamik hesaplamalar sırasında bir hata oluştu: {e}")

def cost_analysis(S):
    """
    Web-Scraping ile alınan fiyatlara göre trafo sargı maliyeti analizi yapar.
    """
    print("\n" + "="*50)
    print(" 💰  TRANSFORMATÖR MALİYET ANALİZİ (GÜNCEL KUR İLE)")
    print("="*50)
    
    print("Güncel piyasa verileri çekiliyor... Lütfen bekleyin.")
    prices = get_metal_prices()
    
    cu_price = prices["copper_usd_kg"]
    al_price = prices["aluminum_usd_kg"]
    
    print(f"📈 Güncel Bakır Fiyatı     : ~{cu_price:.2f} USD/kg")
    print(f"📈 Güncel Alüminyum Fiyatı : ~{al_price:.2f} USD/kg")
    print("-" * 50)
    
    # KVA gücüne göre yaklaşık sargı ağırlığı tahmini
    # (Trafonun kVA gücü arttıkça orantılı olarak iletken ihtiyacı artar)
    # Örnek statik yaklaşım: S_kVA başına yaklaşık 1.2 kg bakır veya 0.8 kg alüminyum 
    S_kVA = S / 1000.0
    cu_weight = S_kVA * 1.2
    al_weight = S_kVA * 0.8
    
    total_cu_cost = cu_weight * cu_price
    total_al_cost = al_weight * al_price
    
    print(f"🛠️ {S_kVA:.1f} kVA Trafo için Tahmini İletken Ağırlıkları:")
    print(f"   Bakır Sargı Kullanılırsa   : {cu_weight:.1f} kg")
    print(f"   Alüminyum Sargı Kullanılırsa : {al_weight:.1f} kg")
    print("-" * 50)
    
    print(f"💵 Bakır Sargı Toplam Maliyeti     : {total_cu_cost:.2f} USD")
    print(f"💵 Alüminyum Sargı Toplam Maliyeti : {total_al_cost:.2f} USD")
    print("="*50 + "\n")

def draw_transformer():
    """
    Terminal ekranına ASCII formatında 3-Faz Güç Transformatörü çizer.
    """
    print(r"""
          =======================================
          |       TRANSFORMATÖR ŞEMASI          |
          =======================================
               ___         ___         ___
              /   \       /   \       /   \
             |     |     |     |     |     |
             |     |     |     |     |     |
             |     |     |     |     |     |
    ~~~~~~~~~|     |~~~~~|     |~~~~~|     |~~~~~~~~~
   {  V1     |     |     |     |     |     |    V2  }
   {  (H.V)  |     |     |     |     |     |   (L.V)}
    ~~~~~~~~~|     |~~~~~|     |~~~~~|     |~~~~~~~~~
             |     |     |     |     |     |
             |     |     |     |     |     |
             |     |     |     |     |     |
              \___/       \___/       \___/
          =======================================
          ||  3-FAZ YAĞLI TİP GÜÇ TRANSFORMATÖRÜ ||
          =======================================
    """)

def get_float_input(prompt):
    """
    Kullanıcıdan güvenli bir şekilde ondalıklı sayı alır. Hatalı girişte programı sonlandırmak yerine tekrar sorar.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  -> [Hata] Geçersiz giriş! Lütfen sadece sayısal bir değer giriniz (Örn: 50.5).")
        except KeyboardInterrupt:
            import sys
            print("\n[Bilgi] İşlem iptal edildi.")
            sys.exit(1)

def main():
    print("="*60)
    print("🚀 ANTI-GRAVITY YAZILIM - TRAFO AR-GE HESAPLAMA ARACI 🚀")
    print("="*60)
    print("Lütfen trafo etiket değerlerini giriniz.\n")
    
    try:
        S = get_float_input("Görünür Güç S (VA): ")
        V1 = get_float_input("Primer Gerilimi V1 (V): ")
        V2 = get_float_input("Sekonder Gerilimi V2 (V): ")
        uk = get_float_input("Bağıl Kısa Devre Empedansı uk (%): ")
        P0 = get_float_input("Boşta Çalışma Kaybı P0 (W): ")
        Pk = get_float_input("Kısa Devre Kaybı Pk (W): ")
        
        print("\n--- Termodinamik Veriler ---")
        oil_volume = get_float_input("Trafo Yağ Hacmi (Litre) (Örn: 200): ")
        expansion_coeff = get_float_input("Yağ Genleşme Katsayısı (1/°C) (Örn: 0.00075): ")
        delta_T = get_float_input("Maksimum Sıcaklık Artışı ΔT (°C) (Örn: 60): ")
        
        while True:
            print("\n" + "="*50)
            print(" 📋 GİRİLEN DEĞERLER ÖZETİ")
            print("="*50)
            print(f"[1] Görünür Güç (S)        : {S} VA")
            print(f"[2] Primer Gerilimi (V1)   : {V1} V")
            print(f"[3] Sekonder Gerilimi (V2) : {V2} V")
            print(f"[4] Empedans (uk)          : % {uk}")
            print(f"[5] Boşta Kayıp (P0)       : {P0} W")
            print(f"[6] Kısa Devre Kaybı (Pk)  : {Pk} W")
            print(f"[7] Yağ Hacmi              : {oil_volume} Litre")
            print(f"[8] Genleşme Katsayısı     : {expansion_coeff} 1/°C")
            print(f"[9] Sıcaklık Artışı (ΔT)   : {delta_T} °C")
            print("="*50)
            
            choice = input("Değiştirmek istediğiniz verinin numarasını girin (1-9) veya onaylayıp hesaplamaya geçmek için 'E' tuşlayın: ").strip().lower()
            
            if choice == 'e':
                break
            elif choice == '1':
                S = get_float_input("Yeni Görünür Güç S (VA): ")
            elif choice == '2':
                V1 = get_float_input("Yeni Primer Gerilimi V1 (V): ")
            elif choice == '3':
                V2 = get_float_input("Yeni Sekonder Gerilimi V2 (V): ")
            elif choice == '4':
                uk = get_float_input("Yeni Bağıl Kısa Devre Empedansı uk (%): ")
            elif choice == '5':
                P0 = get_float_input("Yeni Boşta Çalışma Kaybı P0 (W): ")
            elif choice == '6':
                Pk = get_float_input("Yeni Kısa Devre Kaybı Pk (W): ")
            elif choice == '7':
                oil_volume = get_float_input("Yeni Trafo Yağ Hacmi (Litre): ")
            elif choice == '8':
                expansion_coeff = get_float_input("Yeni Yağ Genleşme Katsayısı (1/°C): ")
            elif choice == '9':
                delta_T = get_float_input("Yeni Maksimum Sıcaklık Artışı ΔT (°C): ")
            else:
                print("  -> Lütfen geçerli bir numara (1-9) veya 'E' giriniz.")
        
        # 1. Aşama: Elektriksel Karakter Analizi
        transformer_analysis(S, V1, V2, uk, P0, Pk)
        
        # 2. Aşama: Termodinamik ve Soğutma Modülü
        thermal_cooling_analysis(P0, Pk, oil_volume, expansion_coeff, delta_T)
        
        # 3. Aşama: Web Scraping ile Maliyet Analizi
        cost_analysis(S)
        
        # 4. Aşama: Şematik Çizim
        draw_transformer()
        
        print("\nİşlem tamamlandı.")
        input("Çıkmak için ENTER'a basın...")
        
    except KeyboardInterrupt:
        print("\n[Bilgi] İşlem kullanıcı tarafından iptal edildi. Program sonlandırılıyor.")
        input("\nÇıkmak için ENTER'a basın...")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n[Beklenmeyen Hata] {e}")
        input("\nÇıkmak için ENTER'a basın...")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
