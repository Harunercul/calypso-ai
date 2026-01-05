# Hakem Demo Rehberi
## TÜBİTAK İP-2: Yapay Zeka Bot Sistemi

---

## Demo Özeti

Hakeme **3 ana senaryo** gösterilecek:

| Senaryo | Süre | Gösterilecek Sistem |
|---------|------|---------------------|
| 1. Temel Savaş | 5-7 dk | Utility AI + Karar Verme |
| 2. Adaptif Zorluk | 7-10 dk | DDA + Player Tracking |
| 3. RL Karşılaştırma | 10-12 dk | PPO vs Rule-Based |

**Toplam Demo Süresi:** ~25-30 dakika

---

## Senaryo 1: Temel Savaş Davranışları (5-7 dk)

### Amaç
Utility AI tabanlı karar verme sistemini göstermek.

### Gösterilecekler

1. **Bot Spawn**
   - Bot sahneye gelir
   - Devriye modunda başlar (PATROL action)

2. **Düşman Algılama**
   - Oyuncu yaklaştığında bot fark eder
   - Utility skorları değişir (Attack ↑, Patrol ↓)

3. **Karar Verme Süreci**
   ```
   Utility Skorları (Canlı):
   ├── ATTACK:      0.85 ████████░░
   ├── TAKE_COVER:  0.45 ████░░░░░░
   ├── FLEE:        0.15 █░░░░░░░░░
   ├── PATROL:      0.10 █░░░░░░░░░
   └── Seçilen: ATTACK
   ```

4. **Savaş Davranışları**
   - Saldırı → Hasar alma → Siper alma
   - Can düşünce FLEE
   - Mermi bitince RELOAD

### Terminal Komutu (Demo için)
```bash
python scripts/quick_test.py
```

### Hakeme Söylenecek
> "Bot, 8 farklı aksiyonun utility skorlarını hesaplayarak en uygun davranışı seçiyor. Bu sistem Hong et al. (2023)'in GOBT framework'ünden esinlenmiştir."

---

## Senaryo 2: Adaptif Zorluk Sistemi (7-10 dk)

### Amaç
Dynamic Difficulty Adjustment (DDA) sistemini göstermek.

### Gösterilecekler

1. **Oyuncu Performans Metrikleri**
   ```
   Player Performance:
   ├── Accuracy:     65%
   ├── K/D Ratio:    2.3
   ├── Avg Lifespan: 45s
   ├── Headshot %:   12%
   └── Skill Score:  0.72
   ```

2. **Zorluk Geçişi**
   ```
   Difficulty: ████████░░ 0.72

   Level 5: Koruma
   ├── HP:        150
   ├── Accuracy:  80%
   ├── Reaction:  0.3s
   └── Aggression: 70%
   ```

3. **7 Zorluk Seviyesi**
   | Level | İsim | HP | Accuracy |
   |-------|------|-----|----------|
   | 1 | Yolcu | 50 | 20% |
   | 2 | Mürettebat | 75 | 40% |
   | 3 | Gemi Muhafızı | 100 | 60% |
   | 4 | Gemi Polisi | 120 | 70% |
   | 5 | Koruma | 150 | 80% |
   | 6 | Sahil Güvenlik | 175 | 85% |
   | 7 | Özel Kuvvetler | 200 | 95% |

### Python Demo Kodu
```python
from python_rl_server.difficulty import DifficultyManager, PlayerPerformanceTracker

# Manager oluştur
dm = DifficultyManager()
dm.register_player("demo_player")

# Performans simüle et
tracker = dm.get_tracker("demo_player")
tracker.record_kill()
tracker.record_kill()
tracker.record_shot(hit=True)
tracker.record_shot(hit=True)
tracker.record_shot(hit=False)

# Zorluk güncelle
dm.update_difficulty("demo_player")
print(dm.get_difficulty_info("demo_player"))
```

### Hakeme Söylenecek
> "Sistem, oyuncunun accuracy, K/D ratio ve hayatta kalma süresini izliyor. Pfau et al. (2020)'un çalışmasındaki gibi yumuşak geçişlerle zorluk ayarlanıyor. Oyuncu fark etmeden optimal zorluk sağlanıyor."

---

## Senaryo 3: RL vs Rule-Based Karşılaştırma (10-12 dk)

### Amaç
Makine öğrenmesi (PPO) ile kural tabanlı sistemin farkını göstermek.

### Gösterilecekler

1. **Yan Yana Karşılaştırma**
   ```
   ┌─────────────────┬─────────────────┐
   │   PPO Agent     │  Rule-Based     │
   ├─────────────────┼─────────────────┤
   │ Mean Reward:    │ Mean Reward:    │
   │    191.37       │    48.11        │
   │                 │                 │
   │ Win Rate:       │ Win Rate:       │
   │    42%          │    44%          │
   │                 │                 │
   │ Survival:       │ Survival:       │
   │    68%          │    64%          │
   └─────────────────┴─────────────────┘
   ```

2. **Training Grafikleri (TensorBoard)**
   - Episode reward artışı
   - Loss değerleri
   - 100K step eğitim süreci

### Terminal Komutu
```bash
# Karşılaştırma çalıştır
python scripts/evaluate.py --compare --model ./models/ppo_*/ppo_final.zip --episodes 50

# TensorBoard (eğitim grafikleri)
tensorboard --logdir ./logs
```

### Sonuç Tablosu
| Metrik | PPO | Rule-Based | Kazanan |
|--------|-----|------------|---------|
| Mean Reward | 191.37 | 48.11 | **PPO (+143)** |
| Win Rate | 42% | 44% | Rule-Based |
| Survival | 68% | 64% | **PPO** |
| Tutarlılık | ±143 | ±20 | Rule-Based |

### Hakeme Söylenecek
> "PPO agent'ımız 100.000 adım eğitimle rule-based sisteme göre 3 kat daha fazla reward elde etti. Chelarescu (2022)'nin GVGAI çalışmasındaki hyperparametreleri kullandık. Daha uzun eğitimle win rate'in de artmasını bekliyoruz."

---

## Demo Hazırlık Checklist

### Önceki Gün
- [ ] Python environment çalışıyor mu? (`python scripts/quick_test.py`)
- [ ] Model eğitilmiş mi? (`./models/ppo_*/`)
- [ ] TensorBoard logları var mı? (`./logs/`)

### Demo Günü
- [ ] Terminal açık, doğru dizinde
- [ ] Virtual environment aktif
- [ ] Evaluation script hazır

### Yedek Plan
- [ ] Önceden kaydedilmiş terminal çıktıları
- [ ] Ekran görüntüleri / video

---

## Demo Komutları (Sırasıyla)

```bash
# 1. Environment aktif et
cd /Users/harun.ercul/Desktop/arge_oyun
source venv/bin/activate

# 2. Senaryo 1: Quick test (Utility AI)
python scripts/quick_test.py

# 3. Senaryo 2: DDA demo (Python'da)
python -c "
from python_rl_server.difficulty import DifficultyManager
dm = DifficultyManager()
dm.register_player('hakem_demo')
tracker = dm.get_tracker('hakem_demo')
for _ in range(5): tracker.record_kill()
for _ in range(2): tracker.record_death()
dm.update_difficulty('hakem_demo')
info = dm.get_difficulty_info('hakem_demo')
print(f'Skill Score: {tracker.calculate_skill_score():.2f}')
print(f'Difficulty Level: {info[\"difficulty_level\"]} - {info[\"difficulty_name\"]}')
print(f'Bot Accuracy: {info[\"bot_params\"][\"accuracy\"]*100:.0f}%')
"

# 4. Senaryo 3: PPO vs Rule-Based
python scripts/evaluate.py --compare --model ./models/ppo_*/ppo_final.zip --episodes 20

# 5. TensorBoard (ayrı terminal)
tensorboard --logdir ./logs
```

---

## Sık Sorulan Sorular (Hakemden Gelebilecek)

### S: Neden PPO algoritması seçtiniz?
> A: Chelarescu (2022) ve Almeida et al. (2023) FPS oyunlarında PPO'nun en stabil sonuçları verdiğini göstermiştir. Ayrıca Stable-Baselines3 ile production-ready implementasyonu mevcuttur.

### S: Rule-based neden hala kullanılıyor?
> A: Hong et al. (2023)'in GOBT çalışmasında gösterildiği gibi, hibrit sistemler en iyi sonuçları verir. Rule-based sistem interpretable ve debug edilebilir; RL sistem ise adaptif ve öğrenebilir.

### S: DDA sistemi oyuncu deneyimini nasıl etkiliyor?
> A: Pfau et al. (2020) göstermiştir ki, fark edilmeyen zorluk ayarlaması motivasyonu artırır. Sistemimiz skill score'a göre yumuşak geçişler yaparak "frustration" ve "boredom" arasında denge kurar.

### S: Gerçek oyunla nasıl entegre olacak?
> A: gRPC protokolü ile. Proto dosyası hazır, firma C++ client yazacak. Python server 50051 portunda çalışacak.

---

## Dosya Konumları

```
docs/
├── LITERATUR_VE_REFERANSLAR.md   # Makale referansları
├── HAKEM_DEMO_REHBERI.md         # Bu dosya
├── FIRMA_ICIN_ENTEGRASYON.md     # UE entegrasyonu
└── FIRMA_SORULARI.md             # Firmaya sorular

scripts/
├── quick_test.py                  # Senaryo 1 için
├── evaluate.py                    # Senaryo 3 için
└── train_agent.py                 # Eğitim için
```

---

*TÜBİTAK İP-2 Projesi - Hakem Demosu Rehberi*
