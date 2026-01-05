# Ar-Ge Değeri ve Özgün Katkılar
## TÜBİTAK İP-2: Yapay Zeka, Karakter ve Bot Geliştirme

---

## Özet

Bu proje, oyun yapay zekası alanında **5 temel özgün katkı** sunmaktadır. Klasik oyun AI sistemlerinden farklı olarak, hibrit mimari, makine öğrenmesi entegrasyonu ve akademik temelli tasarım ile Ar-Ge niteliği taşımaktadır.

---

## 1. Hibrit AI Mimarisi

### Problem
Mevcut oyunlarda bot AI sistemleri genellikle **tek bir yaklaşım** kullanır:
- Ya tamamen **rule-based** (öngörülebilir, statik)
- Ya tamamen **ML-based** (black-box, debug edilemez)

### Çözümümüz
```
┌─────────────────────────────────────────────────┐
│           HİBRİT AI MİMARİSİ                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐      ┌─────────────┐          │
│  │ Utility AI  │      │ PPO Agent   │          │
│  │ (Rule-Based)│  +   │ (ML-Based)  │          │
│  └──────┬──────┘      └──────┬──────┘          │
│         │                    │                  │
│         └────────┬───────────┘                  │
│                  ▼                              │
│         ┌─────────────┐                         │
│         │  Decision   │                         │
│         │  Fusion     │                         │
│         └─────────────┘                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Ar-Ge Değeri
| Özellik | Klasik Sistemler | Bizim Sistem |
|---------|------------------|--------------|
| Debug Edilebilirlik | Düşük (ML) veya Yüksek (Rule) | **Yüksek** |
| Adaptasyon | Yok (Rule) veya Yüksek (ML) | **Yüksek** |
| Açıklanabilirlik | Düşük (ML) veya Yüksek (Rule) | **Yüksek** |
| Performans | Değişken | **Optimize** |

### Akademik Referans
> Hong, Y., Yan, T., & Seo, J. (2023). GOBT: A synergistic approach to game AI using goal-oriented and utility-based planning in behavior trees.

---

## 2. Gerçek Zamanlı Python-UE Bridge

### Problem
Oyun motorları (Unreal, Unity) genellikle C++/C# ile sınırlıdır. Modern ML kütüphaneleri (PyTorch, TensorFlow) Python'da geliştirilmiştir.

### Çözümümüz
```
┌─────────────────┐         gRPC          ┌─────────────────┐
│  Unreal Engine  │ ◄──────────────────► │  Python Server  │
│  (C++)          │    TCP:50051          │  (PyTorch)      │
├─────────────────┤                       ├─────────────────┤
│ • Bot Character │                       │ • PPO Agent     │
│ • AI Controller │  Observation (64D)    │ • Training Loop │
│ • Perception    │ ─────────────────────►│ • Reward Calc   │
│                 │                       │                 │
│                 │  Action (0-8)         │ • TensorBoard   │
│                 │ ◄─────────────────────│ • Model Save    │
└─────────────────┘                       └─────────────────┘
```

### Ar-Ge Değeri
- **Model güncelleme** oyun derlemesi gerektirmez
- **A/B testing** farklı modeller kolayca değiştirilebilir
- **Research-grade** ML kütüphaneleri kullanılabilir
- **Distributed training** mümkün

### Teknik Detaylar
| Bileşen | Teknoloji |
|---------|-----------|
| Protokol | gRPC (Protocol Buffers) |
| Port | 50051 (TCP) |
| Observation | 64-dim float array |
| Action | Discrete (0-8) |
| Latency | <10ms (lokal) |

---

## 3. PPO ile Öğrenen Bot

### Problem
Klasik oyun bot'ları **scriptlenmiş** davranışlar sergiler. Oyuncular kısa sürede pattern'leri öğrenir ve oyun sıkıcı hale gelir.

### Çözümümüz
Proximal Policy Optimization (PPO) ile **deneyimden öğrenen** bot sistemi.

### Eğitim Sonuçları
```
Training Results (100K steps):
├── Mean Reward:     191.37 (vs 48.11 rule-based)
├── Win Rate:        42%
├── Survival Rate:   68%
├── Improvement:     3x reward increase
└── Training Time:   ~30 seconds
```

### Reward Fonksiyonu (Özgün Tasarım)
```python
rewards = {
    'kill_enemy':      +10.0,   # Teşvik: Saldırganlık
    'damage_dealt':    +1.0,    # Teşvik: Etkili savaş
    'damage_taken':    -0.5,    # Ceza: Dikkatsizlik
    'death':           -10.0,   # Ceza: Hayatta kalma
    'survival':        +0.1/s,  # Teşvik: Sürdürülebilirlik
    'cover_usage':     +0.5,    # Teşvik: Taktiksel oyun
    'headshot':        +3.0,    # Teşvik: Beceri
}
```

### Akademik Referans
> Chelarescu, P. A. (2022). A deep reinforcement learning agent for general video game AI framework games.
>
> Oh, I., et al. (2022). Creating pro-level AI for a real-time fighting game using deep reinforcement learning.

---

## 4. Dinamik Zorluk Ayarlama (DDA)

### Problem
Sabit zorluk seviyeleri (Easy/Medium/Hard) tüm oyuncular için uygun değildir:
- Yeni oyuncular **frustration** yaşar
- Deneyimli oyuncular **boredom** yaşar

### Çözümümüz
Oyuncu performansını **gerçek zamanlı** izleyerek otomatik zorluk ayarlama.

### Player Performance Tracker
```
Tracked Metrics:
├── accuracy_ratio      (Weight: 0.25)
├── kill_death_ratio    (Weight: 0.30)
├── average_lifespan    (Weight: 0.20)
├── headshot_ratio      (Weight: 0.10)
└── damage_per_minute   (Weight: 0.15)
                        ─────────────
                        Skill Score → Difficulty
```

### 7 Kademeli Zorluk Sistemi
| Level | İsim | HP | Accuracy | Reaction | Aggression |
|-------|------|-----|----------|----------|------------|
| 1 | Yolcu | 50 | 20% | 1.0s | 10% |
| 2 | Mürettebat | 75 | 40% | 0.7s | 30% |
| 3 | Gemi Muhafızı | 100 | 60% | 0.5s | 50% |
| 4 | Gemi Polisi | 120 | 70% | 0.4s | 60% |
| 5 | Koruma | 150 | 80% | 0.3s | 70% |
| 6 | Sahil Güvenlik | 175 | 85% | 0.25s | 80% |
| 7 | Özel Kuvvetler | 200 | 95% | 0.15s | 90% |

### Yumuşak Geçiş Algoritması
```python
# Exponential Moving Average ile smooth transition
new_difficulty = current + adjustment_rate × (target - current)
# adjustment_rate = 0.1 (yavaş, fark edilmez geçiş)
```

### Akademik Referans
> Pfau, J., Smeddinck, J. D., & Malaka, R. (2020). Enemy within: Long-term motivation effects of deep player behavior models for dynamic difficulty adjustment.

---

## 5. Akademik Temelli Tasarım

### Problem
Oyun AI geliştirmede genellikle **trial-error** ve **sezgisel** yaklaşımlar kullanılır. Bu, tekrarlanabilirlik ve bilimsel geçerlilik açısından sorunludur.

### Çözümümüz
**18 hakemli makale** incelenerek, kanıtlanmış yöntemler uygulanmıştır.

### Referans Dağılımı
```
Makale Kategorileri:
├── Utility AI & Karar Verme       (3 makale)
├── Davranış Ağaçları              (3 makale)
├── Güçlendirmeli Öğrenme          (3 makale)
├── Dinamik Zorluk Ayarlama        (3 makale)
├── Ters Kinematik                 (3 makale)
└── NPC AI Sistemleri              (3 makale)
                                   ──────────
                                   18 makale
```

### Kod-Makale Eşleştirmesi
| Kod Modülü | Referans Makaleler |
|------------|-------------------|
| `ppo_agent.py` | Chelarescu (2022), Oh et al. (2022) |
| `rule_based.py` | Hong et al. (2023), Chen et al. (2021) |
| `rewards.py` | Almeida et al. (2023) |
| `difficulty/manager.py` | Pfau et al. (2020) |
| `player_tracker.py` | Pfau et al. (2020), Moschovitis (2023) |

---

## Teknolojik Belirsizlikler (Ar-Ge Kriterleri)

TÜBİTAK Ar-Ge projesi için ele alınan belirsizlikler:

### 1. Utility AI Skorlama
**Belirsizlik:** Çoklu faktörlerin optimal ağırlıklandırılması
**Çözüm:** Consideration-based sistem ve response curve'ler
**Sonuç:** 8 aksiyon için dinamik skor hesaplama

### 2. RL Eğitim Stabilitesi
**Belirsizlik:** Reward fonksiyonu tasarımı ve hyperparameter seçimi
**Çözüm:** Chelarescu (2022) referanslı PPO konfigürasyonu
**Sonuç:** 100K step'te stabil eğitim, 3x reward artışı

### 3. Gerçek Zamanlı Inference
**Belirsizlik:** Python-UE haberleşme latency'si
**Çözüm:** gRPC ile optimize edilmiş protokol
**Sonuç:** <10ms lokal latency

### 4. Adaptif Zorluk Dengesi
**Belirsizlik:** Oyuncu deneyimini bozmadan zorluk geçişleri
**Çözüm:** EMA (Exponential Moving Average) ile yumuşak geçiş
**Sonuç:** Fark edilmez zorluk ayarlama

---

## Gelecek Çalışmalar

### Kısa Vadeli
- [ ] Daha uzun eğitim (500K-1M steps)
- [ ] Self-play training
- [ ] Multi-agent koordinasyon

### Orta Vadeli
- [ ] Curriculum learning entegrasyonu
- [ ] Imitation learning (oyuncu verilerinden)
- [ ] Transfer learning (farklı haritalar arası)

### Uzun Vadeli (LLM Entegrasyonu)
- [ ] LLM tabanlı taktik planlama
- [ ] Doğal dil komut sistemi
- [ ] Dinamik NPC diyalogları
- [ ] Oyuncu davranış analizi

---

## Karşılaştırmalı Analiz

| Özellik | Tipik Oyun AI | Akademik Prototip | **Bizim Sistem** |
|---------|---------------|-------------------|------------------|
| AI Tipi | Rule-based | ML-only | **Hibrit** |
| Öğrenme | Yok | Offline | **Online + Offline** |
| Zorluk | Manuel | Sabit | **Adaptif** |
| Framework | Oyun motoru | Python | **Bridge** |
| Referans | Yok | Var | **18 makale** |
| Debug | Zor | Çok zor | **Kolay** |
| Deployment | Kolay | Zor | **Orta** |

---

## Sonuç

Bu proje, oyun yapay zekası alanında **akademik literatür ile endüstriyel uygulama** arasında köprü kurmaktadır. Hibrit mimari, gerçek zamanlı ML inference ve adaptif zorluk sistemi ile Ar-Ge niteliği taşıyan özgün bir çalışmadır.

---

*TÜBİTAK 1501 - Sanayi Ar-Ge Projeleri Destekleme Programı*
*İş Paketi 2: Yapay Zeka, Karakter ve Bot Geliştirme*
