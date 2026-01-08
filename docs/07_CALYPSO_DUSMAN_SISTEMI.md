# CALYPSO Düşman Sistemi
## TÜBİTAK İP-2 - AI Bot Konfigürasyonu

---

## Genel Bakış

CALYPSO oyunundaki düşman sistemi **Tier** bazlı organize edilmiştir. Her tier farklı zorluk ve davranış kalıpları içerir.

```
TIER HİYERARŞİSİ
────────────────────────────────────────────────────────
Tier 1          → Düşük Güvenlik (Kolay)
Tier 2          → Orta Seviye (Normal)
Tier 2 Marksman → Nişancı (Zor)
Tier 2 Robotic  → Örümcek Mayın (Özel)
Tier 2 Special  → Kalkanlı Birimler (Çok Zor)
Tier 5          → Boss - Juggernaut (Ekstrem)
────────────────────────────────────────────────────────
```

---

## Tier 1 - Düşük Güvenlik

**Kimler:** Güvenlik Görevlileri, Basit Mürettebat

### Varyantlar

| Varyant | Spawn | Silah | Hasar | Şarjör | Reload |
|---------|-------|-------|-------|--------|--------|
| HG (Tabanca) | %70 | Pistol | 4 | 7 | 2s |
| SMG | %30 | Hafif Makinalı | 2 | 15 | 3s |

### Temel İstatistikler
- **HP:** 100
- **Zırh:** %10 veya yok
- **İsabet:** %15 (çok düşük - genellikle ıskalarlar)
- **Hız:** Orta-Hızlı

### Kısıtlamalar
- Consumable kullanamazlar
- İyileşemezler (Heal yok)
- Yardım çağıramazlar

### Davranış Döngüsü

```
[Tespit] → [Şaşkınlık 1.5s] → [Panik Ateşi 2s] → [Sipere Kaçış]
                                                        ↓
[Etkisiz Ateş 2s] ← [Uzun Nişan 5s] ← [Pasif Bekleme 7s]
        ↓
[Savunmasız Reload 3s] → [Döngü Tekrar]
```

### Alan Bazlı Davranışlar

| Alan | Davranış | Süre |
|------|----------|------|
| Dar | Blind fire, sonra panik kaçış | 10s |
| Orta | Masa/koltuk altına saklan | 2m yaklaşınca kaç |
| Geniş | Uzak siper ara, yoksa çömel | 5s bekle, rastgele ateş |

### Spawn Ayarları
- **Tetikleyici:** Alarm
- **Aralık:** Her 30 saniye
- **Grup:** 3-5 kişi
- **Lokasyonlar:** Mutfak kapıları, mürettebat yatakhaneleri, yakın koridorlar

---

## Tier 2 - Orta Seviye Düşmanlar

**Kimler:** Geminin Silahlı Güvenlik Ekibi, Paralı Askerler

### Varyantlar

| Varyant | Spawn | Silah | Hasar | Ritim | Reload |
|---------|-------|-------|-------|-------|--------|
| AR (Burst) | %60 | Tüfek | 6x3=18 | 3 mermi → 1.2s ara | 4s |
| SG (Shotgun) | %40 | Pompalı | 15 | Her 2s bir atış | 8s |

### Bomba Paketi (Ek)
- **Spawn:** +%40 şans (tüm varyantlar)
- **Görsel:** Göğüste parlak torbalar
- **Paket HP:** 50
- **Patlama:** 200 hasar, 500 UU alan
- **Hazırlık:** 2s bağırma + 20s cooldown
- **Uyarı:** 1.5s önce kırmızı halka

### Temel İstatistikler
- **HP:** 150
- **Zırh:** %25 hasar azaltma
- **İsabet:** %40
- **Hız:** Orta
- **Kısıtlama:** Kendini iyileştiremez

### Davranış Mekanikleri

| Mekanik | Birim | Açıklama |
|---------|-------|----------|
| Baskılama | AR | Oyuncu siperdeyken sürekli burst |
| Kuşatma | SG | 3.5s sprintlerle yan sızma |
| Bomba | Hepsi | 2s hazırlık, 20s cooldown |
| Savunma | Hepsi | 0.5s duraksama, sprint kaçış |

### Dengeleme
- **İlk tepki gecikmesi:** 1.3s
- **İlk atışlar:** Bilerek ıskalanır
- **Genel isabet:** %40

### 9 Kişilik Grup Taktikleri

**Kompozisyon:** 2 Kalkan + 4 AR + 3 SG

#### Dar Alanlar (Koridorlar)
| Birim | Kalkanlı | Kalkansız |
|-------|----------|-----------|
| Kalkan | Yavaş ilerle, mermi em | 6s geri çekil |
| SG | Peek-fire, geri çekil | 3m sprint siper |
| AR | Sürekli baskılama | Çapraz ateş (ikili) |

#### Geniş Alanlar
| Birim | Kalkanlı | Kalkansız |
|-------|----------|-----------|
| Kalkan | Merkez ilerle (yem) | Defansif bekle |
| SG | Gizli flank | Bitirici atış |
| AR | Kalkanı koru, SG'ye cover | Yaylım ateş |

#### Giriş Sırası
1. **Kalkanlar** - Kapıda bekle, koruma sağla
2. **AR'lar** - Hızla yüksek/uzak sipere
3. **SG'ler** - Kalkana yakın, flank rotası

#### Geri Çekilme
- **Tetik:** Ön kalkanlar yok edildiğinde
- **Tepki:** Tüm birimler geri ateşle çekilir
- **Son birim:** Panele koş, 3s yardım çağır

---

## Tier 2 - Marksman (Nişancı)

### İstatistikler
- **HP:** 40-50
- **Zırh:** Yok
- **İsabet:** %70

### Silah
- **Tip:** DMR
- **Hasar:** 15
- **RPM:** 10
- **Şarjör:** 4
- **Reload:** 10s

### Spawn
- **Başlangıç:** Tier 2 tetiklendikten 1 dk sonra
- **Aralık:** Her 90 saniyede 1-2 adet
- **Lokasyonlar:** Üst güverte, dans salonu balkonu, koridor sonu

### Alan Bazlı
| Alan | Davranış |
|------|----------|
| Dar | Koridor ucunda pozisyon |
| Orta | Kolon/masa arkası |
| Geniş | Yüksek platform, yarı-sniper |

---

## Tier 2 - Robotic (Örümcek Mayın)

### İstatistikler
- **Vücut HP:** 250
- **Bacak HP:** 50 (her biri, 4 adet)
- **Toplam HP:** 450
- **Zırh:** Yok
- **Hız:** Orta-Yavaş
- **Hasar:** %60 oyuncu HP (patlayıcı)

### Hareket
- Yer, duvar, tavanda hareket edebilir
- 3-4 bacak sağlam → Normal yürüyüş
- 2 bacak kırık → Yere düşer, sürünür
- Fizik itme → O yöne gider, yüzeyde patlar

### Patlama Mekaniği
- **Tetik mesafesi:** 2m
- **Geri sayım:** 2.5s
- **İptal:** Bacaklar kırılır + menzil dışı
- **Uyarı:** Bip sesi, kırmızı ışık

### Spawn Çizelgesi
```
0-45s   → Bekleme
45s     → 1. spawn
50s     → 2. spawn
50-95s  → 45s geri sayım
95s     → 3. spawn
100s    → 4. spawn
```
- **Aralık:** 45s
- **Spawn gap:** 5s
- **Haritada max:** 3 adet
- **Lokasyonlar:** Koridor kapıları, asansörler, depolar, havalandırma

---

## Tier 2 - Special

### Plasma Kalkanlı Muhafız

**İstatistikler:**
- **HP:** 150 / Zırh HP: 100
- **Kalkan HP:** 500 (enerji)
- **Zırh:** %25
- **Silah:** Enerji tabancası (düşük hasar)

**Kalkan Mekaniği:**
| Durum | Detay | Sonuç |
|-------|-------|-------|
| Zayıf Nokta (Battery) | 125 HP, rastgele konum | Kalıcı kapanır |
| Saf Hasarla Kırılma | 500 HP hasar | 6s sonra yenilenir |
| NPC Ölümü | Doğrudan öldürme | Kalkan otomatik kapanır |

**Spawn:**
- Alarm 1: 60s'de 1
- Alarm 2: 60s'de 2
- Alarm 3: 60s'de 3

---

### Iron-Clad Vanguard

**İstatistikler:**
- **HP:** 150 / Zırh: 150
- **Kalkan HP:** 2000 (metal, YENİLENMEZ)
- **Zırh:** %25

**Zayıf Nokta:**
- **İsim:** Bolt (ana menteşe)
- **HP:** 125
- **Hasar çarpanı:** 2x

**Dönüşüm (The Shedding):**
- Kalkan kırılınca sarsılma YOK
- Sırttan shotgun çeker
- Tier 2 SG davranışına geçer
- Hızlanır (kalkan ağırlığı gitti)

---

### Sniper (Keskin Nişancı)

**İstatistikler:**
- **HP:** 40
- **Zırh:** Yok
- **Hasar:** Yüksek (tek atışta ciddi)

**Spawn:**
- Marksman yerine veya ek olarak
- Her 90s'de 1 adet
- **KOŞUL:** Geniş alan veya uzun görüş hattı
- Dar alanda SPAWN OLMAZ

---

## Tier 5 - Boss (The Juggernaut)

### İstatistikler
- **HP:** 1000
- **Zırh:** %50 (normal), %90 (savunma modu)
- **Özel:** Normal'de zırh hasar YEMEZ, sadece sersemlediğinde
- **Hız:** Orta-Yavaş / Savunmada Yavaş
- **Silah:** Kinetik çekiç

### Görünüm
- Tamamen kurşun geçirmez siyah zırh
- Kocaman kinetik çekiç
- Zayıf noktalar: Kırmızı LED çizgiler

### Yetenekler

| Yetenek | Açıklama |
|---------|----------|
| **Kinetik Çekiç** | 3 vuruş: 1-2 zayıf, 3. büyük + stun |
| **Fırlatma Hücumu** | Zıpla, alan hasarı, duvara çarparsa 3s sersem |
| **Savunma Modu** | %90 hasar azaltma, yavaş hareket |

### Zayıf Noktalar
- **Konum:** Zırhtaki kırmızı LED çizgiler
- **Hasar alır:** SADECE sersemlediğinde
- **Strateji:** Şok dalgasından kaçın, LED'lere nişan al

### Saldırı Patternleri

```
HAMMER COMBO:
Omuzdan savur → Yere vur → [Oyuncu alandaysa] → 2. vuruş (takip eder)
* Vuruşlar arası idle YOK

SAVUNMA MODU:
Çekici yere koy → Yüzü kapa → Yavaş yer değiştir

LEAP ATTACK:
Hızlı zıpla → İniş hasarı → [Duvara çarparsa] → 3 adım geri, sersem

YÜRÜME:
Çekici önde tut → LED'leri gizle → Yavaş ilerle
```

---

## AI Sistemi Entegrasyonu

### Tek Model Yaklaşımı

```
┌─────────────────────────────────────────┐
│           PPO MODELİ (Tek)              │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ Tier 1 │  │ Tier 2 │  │Special │
│ Config │  │ Config │  │ Config │
└────────┘  └────────┘  └────────┘
```

### Boss Ayrı Sistem

```
Juggernaut → Pattern-based State Machine (RL değil)
             ↓
        [IDLE] ←→ [HAMMER] ←→ [LEAP] ←→ [DEFENSE]
                              ↓
                         [STUNNED]
```

---

## Konfigürasyon Dosyası

Tüm bu veriler `configs/difficulty_config.yaml` dosyasında tanımlıdır.

```yaml
# Örnek kullanım
tier_1:
  variants:
    hg_pistol:
      stats:
        health: 100
        accuracy: 0.15
```

---

*CALYPSO - TÜBİTAK İP-2 Projesi*
*Ocak 2026*
