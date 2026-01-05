# Gelecek Çalışma: LLM Tabanlı Oyun AI Sistemi
## TÜBİTAK İP-2 - İleri Seviye Ar-Ge Önerisi

---

## Özet

Bu doküman, mevcut RL tabanlı bot sistemine **Büyük Dil Modeli (LLM)** entegrasyonunun potansiyel faydalarını ve uygulama senaryolarını açıklamaktadır. Bu özellik, projenin gelecek fazlarında değerlendirilebilecek bir Ar-Ge yönelimi olarak sunulmaktadır.

---

## Neden LLM?

### Mevcut Sistemin Güçlü Yanları
- ✅ PPO ile hızlı karar verme (<10ms)
- ✅ Utility AI ile açıklanabilir davranış
- ✅ DDA ile adaptif zorluk

### LLM ile Kazanılacaklar
- 🆕 **Stratejik düşünme** - Uzun vadeli plan yapabilme
- 🆕 **Doğal dil anlama** - Oyuncu komutlarını anlama
- 🆕 **Açıklanabilirlik** - "Neden bu kararı aldın?" sorusuna cevap
- 🆕 **Kişilik çeşitliliği** - Her bot farklı karakter

---

## Potansiyel Kullanım Senaryoları

### Senaryo 1: Taktik Danışman

**Konsept:** LLM, karmaşık durumlarda bot'a üst düzey taktik önerir.

```
┌─────────────────────────────────────────────────────────┐
│                    KARAR AKIŞI                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Normal Durum:                                          │
│  Observation → PPO/Utility AI → Action (hızlı)          │
│                                                         │
│  Karmaşık Durum:                                        │
│  Observation → LLM Analiz → Strateji → PPO → Action     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Örnek Senaryo:**
```
Durum:
- 3 düşman farklı açılarda
- Can %25
- Mermi %10
- Arkada siper var ama uzak

LLM Analizi:
"Mevcut durumda doğrudan savaş intihar olur. Öncelik sırası:
1. Duman bombası at (varsa)
2. Sipere doğru geri çekil
3. Reload yap
4. Tek tek angaje ol

Önerilen ilk aksiyon: FLEE (sipere doğru)"
```

---

### Senaryo 2: Dinamik Bot Kişilikleri

**Konsept:** Her bot'a LLM ile benzersiz kişilik atanır.

```
┌─────────────────────────────────────────────────────────┐
│                  BOT KİŞİLİKLERİ                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔴 "Yırtıcı" - Agresif Saldırgan                      │
│     "Düşman gördüğümde düşünmem, saldırırım."          │
│     Attack: 0.95, Cover: 0.20, Flee: 0.05              │
│                                                         │
│  🔵 "Hayalet" - Sessiz Taktikçi                        │
│     "Görünmeden vur, iz bırakmadan git."               │
│     Attack: 0.60, Cover: 0.70, Flank: 0.90             │
│                                                         │
│  🟢 "Kalkan" - Savunmacı Destek                        │
│     "Takımı korurum, gerekirse kendimi feda ederim."   │
│     Support: 0.90, Cover: 0.80, Attack: 0.40           │
│                                                         │
│  🟡 "Tilki" - Fırsatçı                                 │
│     "Zayıf anı bekle, tek vuruşta bitir."              │
│     Investigate: 0.80, Flank: 0.85, Flee: 0.60         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**LLM Prompt Örneği:**
```
Sen bir FPS oyununda "Hayalet" kod adlı keskin nişancısın.
Karakterin: Sessiz, sabırlı, tek atışta öldüren.

Mevcut duruma göre öncelik sıranı (0-1 arası) belirle:
- Attack: ?
- Cover: ?
- Flee: ?
- Flank: ?
- Support: ?
```

---

### Senaryo 3: Oyuncu Davranış Analizi

**Konsept:** LLM, oyuncu pattern'lerini analiz ederek bot stratejisi önerir.

```
┌─────────────────────────────────────────────────────────┐
│              OYUNCU ANALİZ SİSTEMİ                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Toplanan Veri (son 5 dakika):                         │
│  ├── Oyuncu hep sağ flank kullanıyor                   │
│  ├── Sniper rifle tercih ediyor                        │
│  ├── Uzak mesafede kalıyor                             │
│  ├── Sabırlı, beklemeyi seviyor                        │
│  └── Cover değiştirme sıklığı: düşük                   │
│                                                         │
│  LLM Analizi:                                          │
│  "Bu oyuncu keskin nişancı tarzı oynuyor.              │
│   Karşı strateji:                                       │
│   1. Yakın mesafeye zorla (SMG/Shotgun avantajı)       │
│   2. Sol flank'tan yaklaş (beklemiyor)                 │
│   3. Duman kullan (görüşünü kapat)                     │
│   4. Birden fazla bot ile angaje ol (odağını böl)"     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Senaryo 4: Doğal Dil Komut Sistemi (Co-op)

**Konsept:** Oyuncu, bot takım arkadaşlarına sesli/yazılı komut verir.

```
┌─────────────────────────────────────────────────────────┐
│              DOĞAL DİL KOMUTLARI                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Oyuncu: "Beni cover'la, ben kapıyı açacağım"          │
│           ↓                                             │
│  LLM Parse:                                            │
│  {                                                      │
│    "action": "SUPPORT",                                │
│    "type": "cover_fire",                               │
│    "target": "player",                                 │
│    "duration": "until_door_open",                      │
│    "position": "maintain_current"                      │
│  }                                                      │
│           ↓                                             │
│  Bot: Pozisyonunu korur, oyuncuya ateş desteği verir   │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Oyuncu: "Sol tarafı temizle, ben sağdan geliyorum"    │
│           ↓                                             │
│  LLM Parse:                                            │
│  {                                                      │
│    "action": "CLEAR_AREA",                             │
│    "area": "left_flank",                               │
│    "coordination": "pincer_movement",                  │
│    "player_position": "right_flank"                    │
│  }                                                      │
│           ↓                                             │
│  Bot: Sol tarafa hareket, düşmanları angaje eder       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Senaryo 5: Açıklanabilir AI (XAI)

**Konsept:** Bot neden bu kararı aldığını açıklayabilir.

```
┌─────────────────────────────────────────────────────────┐
│              AÇIKLANABİLİR KARAR                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [DEBUG MODE]                                          │
│                                                         │
│  Bot Aksiyonu: FLEE                                    │
│                                                         │
│  LLM Açıklaması:                                       │
│  "Kaçmayı seçtim çünkü:                                │
│   1. Canım kritik seviyede (%15)                       │
│   2. Önümde 2 düşman var                               │
│   3. Mermim bitmek üzere (%5)                          │
│   4. Arkamda güvenli bir siper var                     │
│   5. Takım arkadaşım yaklaşıyor, destek gelebilir      │
│                                                         │
│   Bu durumda savaşmak %90 ölüm demek.                  │
│   Geri çekilip toparlanmak daha mantıklı."             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Teknik Mimari Önerisi

```
┌─────────────────────────────────────────────────────────┐
│                  LLM ENTEGRasyonlu MİMARİ               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐                                       │
│  │   Unreal    │                                       │
│  │   Engine    │                                       │
│  └──────┬──────┘                                       │
│         │ gRPC                                         │
│         ▼                                              │
│  ┌─────────────────────────────────────────────┐       │
│  │           Python AI Server                   │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │       │
│  │  │   PPO   │  │ Utility │  │   LLM   │     │       │
│  │  │  Agent  │  │   AI    │  │ Advisor │     │       │
│  │  └────┬────┘  └────┬────┘  └────┬────┘     │       │
│  │       │            │            │           │       │
│  │       └────────────┴────────────┘           │       │
│  │                    │                         │       │
│  │                    ▼                         │       │
│  │           ┌─────────────┐                   │       │
│  │           │  Decision   │                   │       │
│  │           │   Fusion    │                   │       │
│  │           └─────────────┘                   │       │
│  └─────────────────────────────────────────────┘       │
│                       │                                 │
│                       ▼ API Call                       │
│              ┌─────────────────┐                       │
│              │  Claude API /   │                       │
│              │  Local LLM      │                       │
│              └─────────────────┘                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Maliyet ve Performans Analizi

### API Maliyeti (Claude Haiku)

| Kullanım | Token/İstek | İstek/dk | Aylık Maliyet |
|----------|-------------|----------|---------------|
| Taktik (nadir) | ~200 | 1 | ~$5 |
| Kişilik (başlangıç) | ~100 | 0.1 | ~$1 |
| Analiz (periyodik) | ~500 | 0.5 | ~$10 |
| Komut (co-op) | ~150 | 5 | ~$30 |

**Toplam:** ~$50/ay (yoğun kullanımda)

### Lokal LLM Alternatifi

| Model | VRAM | Latency | Kalite |
|-------|------|---------|--------|
| Llama 3.1 8B | 8GB | ~200ms | İyi |
| Mistral 7B | 6GB | ~150ms | İyi |
| Phi-3 Mini | 4GB | ~100ms | Orta |

---

## Uygulama Yol Haritası

### Faz 1: Proof of Concept (2 hafta)
- [ ] Basit taktik danışman prototipi
- [ ] Claude API entegrasyonu
- [ ] A/B test: LLM vs Pure RL

### Faz 2: Kişilik Sistemi (3 hafta)
- [ ] 5 farklı bot kişiliği
- [ ] Kişilik → Utility ağırlık dönüşümü
- [ ] Oyun içi test

### Faz 3: Oyuncu Analizi (4 hafta)
- [ ] Oyuncu veri toplama
- [ ] Pattern recognition
- [ ] Karşı strateji önerisi

### Faz 4: Doğal Dil (6 hafta)
- [ ] Komut parsing sistemi
- [ ] Intent recognition
- [ ] Co-op entegrasyonu

---

## Akademik Değer

Bu entegrasyon, aşağıdaki araştırma alanlarına katkı sağlar:

1. **Hybrid AI Systems** - RL + LLM kombinasyonu
2. **Explainable AI (XAI)** - Oyun AI'da açıklanabilirlik
3. **Human-AI Collaboration** - Doğal dil ile bot kontrolü
4. **Adaptive NPCs** - LLM tabanlı kişilik modelleme

### Potansiyel Yayın Konuları
- "LLM-Augmented Game AI: A Hybrid Approach"
- "Natural Language Commands for NPC Control in FPS Games"
- "Explainable Decision Making in Game Bots using LLMs"

---

## Sonuç

LLM entegrasyonu, mevcut sistemin üzerine eklenebilecek güçlü bir Ar-Ge yönelimi sunmaktadır. Özellikle:

- **Akademik değer** artışı
- **Oyuncu deneyimi** iyileştirmesi
- **Benzersiz özellik** olarak pazarlama avantajı
- **TÜBİTAK** için güçlü Ar-Ge niteliği

Bu özellik, projenin **gelecek fazlarında** veya **devam projelerinde** değerlendirilebilir.

---

*Not: Bu doküman bir fikir ve yol haritası niteliğindedir. Uygulama kararı proje yönetimine aittir.*

---

*TÜBİTAK İP-2 - Gelecek Çalışmalar*
