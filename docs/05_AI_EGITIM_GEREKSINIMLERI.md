# AI Model Eğitim Gereksinimleri
## CALYPSO Bot Sistemi - Oyun Verisi Checklist

---

## Amaç

Bu doküman, AI bot modelinin **gerçek oyun verilerine göre yeniden eğitilmesi** için gerekli bilgileri içermektedir. Mock environment ile temel sistem çalışıyor; gerçek Unreal Engine entegrasyonu için aşağıdaki verilere ihtiyacımız var.

**Not:** Bu bilgiler toplandıktan sonra:
1. Observation space güncellenir (64-dim → oyuna özgü)
2. Action space güncellenir (9 aksiyon → oyundaki aksiyonlar)
3. Reward fonksiyonu kalibre edilir
4. Model yeniden eğitilir

---

## 1. Bot Aksiyonları (Zorunlu)

Bot'un oyunda yapabileceği tüm aksiyonları listeleyin:

- [ ] Ateş etme (primary/secondary silah?)
- [ ] Nişan alma (ADS - Aim Down Sight?)
- [ ] Siper alma (cover sistemi var mı?)
- [ ] Reload
- [ ] Koşma / Yürüme / Eğilme
- [ ] Zıplama
- [ ] Yakın dövüş (melee?)
- [ ] El bombası / Throwable?
- [ ] Özel yetenek / Skill?
- [ ] İtem kullanma (medkit vs.?)
- [ ] Etkileşim (kapı açma vs.?)
- [ ] Diğer: _______________

---

## 2. Oyun Mekanikleri (Zorunlu)

### Silahlar
| Silah Tipi | Hasar | Menzil | Fire Rate | Magazin |
|------------|-------|--------|-----------|---------|
| Örnek: AR  | 25    | 50m    | 600 RPM   | 30      |
|            |       |        |           |         |
|            |       |        |           |         |

### Karakterler
| Değer | Miktar |
|-------|--------|
| Oyuncu HP | ? |
| Bot HP | ? |
| Armor | ? |
| Hareket hızı (yürüme) | ? |
| Hareket hızı (koşma) | ? |
| Headshot multiplier | ? |

---

## 3. Algılama Sistemi (Zorunlu)

- [ ] Görüş menzili: ___ metre
- [ ] Görüş açısı: ___ derece
- [ ] Ses algılama var mı? Menzil: ___
- [ ] Aynı anda max kaç düşman takip edilebilir?
- [ ] Cover arkasındaki düşman görünür mü?

---

## 4. Harita / Çevre

- [ ] Cover noktaları önceden tanımlı mı?
- [ ] Patrol rotaları var mı?
- [ ] Objective/görev sistemi var mı?
- [ ] Harita boyutu yaklaşık: ___ x ___ metre

---

## 5. Takım Mekaniği

- [ ] Takım bazlı oyun mu?
- [ ] Takım arkadaşı sayısı: ___
- [ ] Takım iletişimi var mı?

---

## 6. Ödül/Skor Sistemi

| Olay | Puan |
|------|------|
| Kill | ? |
| Assist | ? |
| Headshot | ? |
| Ölüm | ? |
| Objective | ? |

---

## 7. Mevcut Veriler (Varsa)

- [ ] Oyuncu replay kayıtları var mı?
- [ ] Mevcut bot logları var mı?
- [ ] Maç istatistikleri var mı?

---

## 8. Teknik

- [ ] Unreal Engine versiyonu: ___
- [ ] Mevcut AI sistemi var mı? (Behavior Tree vs.)
- [ ] gRPC deneyimi olan developer var mı?

---

## Sonraki Adımlar

Bu checklist tamamlandıktan sonra:

1. **Observation Space Güncelleme**
   - `python_rl_server/environments/observation.py` dosyası güncellenir
   - Gerçek oyun verilerine göre 64-dim vektör yeniden tasarlanır

2. **Action Space Güncelleme**
   - `python_rl_server/agents/` altındaki agent'lar güncellenir
   - Oyundaki aksiyonlara göre discrete/continuous action tanımlanır

3. **Reward Kalibrasyonu**
   - `python_rl_server/training/rewards.py` kalibre edilir
   - Gerçek oyun skorlarına göre reward fonksiyonu ayarlanır

4. **Yeniden Eğitim**
   - Minimum 500K step eğitim yapılır
   - A/B test ile performans doğrulanır

---

*TÜBİTAK İP-2 Projesi - AI Eğitim Gereksinimleri*
