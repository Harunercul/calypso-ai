# CALYPSO AI Eğitim Sonuçları
## TÜBİTAK İP-2 - Mock Data ile PPO Eğitimi

---

## Veri Kaynağı

Bu eğitim, firma tarafından sağlanan resmi oyun tasarım dokümanlarına dayanmaktadır:

```
game_docx/
├── CP-Tier 1 - düşük güvenlik.pdf    → Tier 1 düşman davranışları
├── CP-Tier 2 - Orta Seviye.pdf       → Tier 2 taktiksel davranışlar
├── CP-Tier 2 - Robotic.pdf           → Örümcek mayın mekanikleri
├── CP-Tier 2 - Special.pdf           → Kalkan sistemleri
└── CP-Tier 5 - Bosslar.pdf           → Juggernaut boss pattern'leri
```

Bu dokümanlardan elde edilen veriler:
- `configs/difficulty_config.yaml` → Düşman istatistikleri, silah verileri
- `calypso_mock_env.py` → Davranış döngüleri, spawn kuralları
- `calypso_observation.py` → Tier/silah/kalkan observation'ları

---

## Eğitim Özeti

| Parametre | Değer |
|-----------|-------|
| **Algoritma** | PPO (Proximal Policy Optimization) |
| **Framework** | Stable-Baselines3 2.0+ |
| **Observation Space** | 96 boyut |
| **Action Space** | 16 discrete aksiyon |
| **Environment** | CalypsoMockEnv |
| **Tarih** | Ocak 2026 |

---

## Model Karşılaştırması

### Tier 1 vs Tier 2 Performans

| Metrik | Tier 1 Model | Tier 2 Model |
|--------|--------------|--------------|
| **Ortalama Reward** | 82.41 | 57.22 |
| **Ortalama Kill** | 4.00 | 6.20 |
| **Hayatta Kalma** | %100 | %50 |
| **Verilen Hasar** | 0.57 | 0.26 |
| **Alınan Hasar** | 0.09 | 0.78 |
| **Episode Süresi** | 245 step | 467 step |

### Aksiyon Kullanım Dağılımı

#### Tier 1 Model (Kolay Düşmanlar)
```
FLANK              : ████████████████████████████████████ 75.4%
COORDINATE_ATTACK  : ████████ 17.0%
ATTACK             : ███ 7.5%
TAKE_COVER         : ▏ 0.1%
```

#### Tier 2 Model (Orta-Zor Düşmanlar)
```
COORDINATE_ATTACK  : ███████████████████████████████████ 75.9%
TARGET_WEAK_POINT  : ██████ 15.3%
ATTACK             : ██ 6.9%
COUNTER_SHIELD     : ▏ 1.7%
```

**Analiz:**
- Tier 1'de model FLANK aksiyonunu öğrenmiş (kolay düşmanları yandan vur)
- Tier 2'de model TARGET_WEAK_POINT ve COUNTER_SHIELD kullanmayı öğrenmiş (kalkanlı düşmanlarla başa çık)

---

## Eğitim Hyperparameters

```python
PPO_CONFIG = {
    'learning_rate': 3e-4,
    'n_steps': 2048,
    'batch_size': 64,
    'n_epochs': 10,
    'gamma': 0.99,
    'gae_lambda': 0.95,
    'clip_range': 0.2,
    'ent_coef': 0.01,
    'vf_coef': 0.5,
    'max_grad_norm': 0.5
}
```

---

## Observation Space (96-dim)

```
CALYPSO Observation Vector
├── [0-19]   Bot Self State (20)
│   ├── health, armor, ammo_primary, ammo_secondary
│   ├── pos_x, pos_y, pos_z
│   ├── rotation_yaw, rotation_pitch
│   ├── velocity_x, velocity_y, velocity_z
│   ├── is_in_cover, is_reloading, is_aiming
│   ├── time_since_damage
│   └── current_tier, alarm_level, area_type, combat_phase  ← CALYPSO Özel
│
├── [20-55]  Enemy States (3 x 12 = 36)
│   └── Per enemy:
│       ├── distance, angle, health_estimate, is_visible
│       ├── is_in_cover, threat_level, velocity_towards_me
│       ├── is_aiming_at_me
│       └── tier, has_shield, shield_hp, weapon_type  ← CALYPSO Özel
│
├── [56-75]  Environment State (20)
│   ├── cover1-4_distance, cover1-4_angle
│   ├── objective_distance, objective_angle, objective_progress
│   ├── danger_zone_distance, danger_zone_angle
│   ├── time_in_combat, enemies_in_range, allies_in_range
│   └── spider_mine_nearby, boss_phase, shield_enemies_count,
│       flank_route_available  ← CALYPSO Özel
│
├── [76-83]  Team State (8)
│   └── team_health_avg, team_alive_ratio, nearest_ally_distance,
│       nearest_ally_angle, team_objective_progress, team_kills,
│       team_deaths, support_needed
│
└── [84-95]  Tactical Info (12)  ← CALYPSO Özel
    └── suppression_threat, flank_threat, sniper_threat,
        explosive_threat, shield_wall_active, retreat_path_clear,
        group_coordination, time_since_alarm, reinforcement_eta,
        enemy_reload_window, boss_stun_window, player_skill_estimate
```

---

## Action Space (16 Aksiyon)

| ID | Aksiyon | Açıklama | Kategori |
|----|---------|----------|----------|
| 0 | IDLE | Bekle | Temel |
| 1 | ATTACK | Standart saldırı | Temel |
| 2 | TAKE_COVER | Sipere gir | Temel |
| 3 | FLEE | Kaç | Temel |
| 4 | RELOAD | Mermi doldur | Temel |
| 5 | PATROL | Devriye gez | Hareket |
| 6 | INVESTIGATE | Araştır | Hareket |
| 7 | ADVANCE | Agresif ilerle | Hareket |
| 8 | FLANK | Yan manevra | Taktik |
| 9 | SUPPORT | Takım desteği | Taktik |
| 10 | SUPPRESS | Baskılama ateşi | Taktik |
| 11 | PEEK_FIRE | Siperden peek-fire | Taktik |
| 12 | TARGET_WEAK_POINT | Zayıf nokta hedefle | CALYPSO Özel |
| 13 | EVADE_EXPLOSIVE | Patlayıcıdan kaçın | CALYPSO Özel |
| 14 | COUNTER_SHIELD | Kalkan karşı manevrası | CALYPSO Özel |
| 15 | COORDINATE_ATTACK | Koordineli saldırı | CALYPSO Özel |

---

## Training Logs

### Tier 1 Training (50K steps)

```
============================================================
CALYPSO AI Bot Training
============================================================
Tier: 1
Alarm Level: 1
Area Type: MEDIUM
Total Timesteps: 50,000
Num Environments: 4
============================================================

Eval num_timesteps=40000, episode_reward=112.08 +/- 71.19
Episode length: 326.00 +/- 560.52
New best mean reward!

Training complete!
Mean Reward: 79.01 +/- 17.29
```

### Tier 2 Training (100K steps)

```
============================================================
CALYPSO AI Bot Training
============================================================
Tier: 2
Alarm Level: 2
Area Type: MEDIUM
Total Timesteps: 100,000
Num Environments: 4
============================================================

Eval num_timesteps=40000, episode_reward=33.13 +/- 7.57
Eval num_timesteps=80000, episode_reward=42.50 +/- 16.88
New best mean reward!

Training complete!
Mean Reward: 57.22 +/- 18.59
```

---

## Tier Bazlı Düşman Davranışları

### Tier 1 - Düşük Güvenlik
```
[Tespit] → [Şaşkınlık 1.5s] → [Panik Ateşi 2s] → [Sipere Kaçış]
                                                        ↓
[Etkisiz Ateş 2s] ← [Uzun Nişan 5s] ← [Pasif Bekleme 7s]
```

- HP: 100, Accuracy: %15
- Silahlar: Tabanca (%70), SMG (%30)
- İyileşemez, yardım çağıramaz

### Tier 2 - Orta Seviye
```
Kompozisyon: 2 Kalkan + 4 AR + 3 SG (9 kişilik grup)

AR (Assault Rifle):
  - Baskılama ateşi
  - Oyuncuyu siperde tutma

SG (Shotgun):
  - Kuşatma manevrası
  - 3.5s sprintlerle flank
```

- HP: 150, Accuracy: %40
- Bomba paketi: %40 şans
- Taktiksel koordinasyon

### Tier 2 Special - Kalkanlı
```
Plasma Kalkan:
  - 500 HP (6s sonra yenilenir)
  - Zayıf nokta: Battery (125 HP)

Iron-Clad Vanguard:
  - 2000 HP (yenilenmez)
  - Kalkan kırılınca shotgun çeker
```

---

## Gerçek Veri ile Beklenen İyileştirmeler

| Metrik | Mock Data | Gerçek Veri (Hedef) |
|--------|-----------|---------------------|
| **Observation** | 96-dim simüle | UE5'ten gerçek sensör |
| **Reward** | Basit hesaplama | Oyun mekaniğine özel |
| **Episode Süresi** | 245-467 step | Oyun tempo'suna uygun |
| **Aksiyon Çeşitliliği** | 4-5 dominant | 10+ aktif kullanım |
| **Transfer Öğrenme** | - | Mock → Gerçek fine-tune |

### Transfer Learning Planı

```
┌─────────────────────────────────────────────────────────┐
│  1. Mock Data Pre-training (Tamamlandı)                 │
│     └─> Temel davranışları öğren                        │
│                                                         │
│  2. Gerçek Veri Fine-tuning (Bekliyor)                  │
│     └─> UE5'ten gelen observation ile ince ayar         │
│                                                         │
│  3. Self-Play Training (Planlandı)                      │
│     └─> Bot vs Bot ile ileri seviye taktikler           │
│                                                         │
│  4. Human Feedback (Planlandı)                          │
│     └─> Oyuncu geri bildirimine göre DDA ayarı          │
└─────────────────────────────────────────────────────────┘
```

---

## Model Dosyaları

```
models/
├── calypso_tier1_*/
│   ├── best/
│   │   └── best_model.zip      ← En iyi Tier 1 model
│   ├── checkpoints/
│   │   └── calypso_ppo_*.zip   ← Checkpoint'ler
│   ├── logs/
│   │   └── PPO_1/              ← TensorBoard logs
│   └── final_model.zip
│
└── calypso_tier2_*/
    ├── best/
    │   └── best_model.zip      ← En iyi Tier 2 model
    └── ...
```

---

## Kullanım

### Eğitim

```bash
# Tier 1 eğitimi
python python_rl_server/train_calypso.py train --tier 1 --timesteps 100000

# Tier 2 eğitimi
python python_rl_server/train_calypso.py train --tier 2 --alarm 2 --timesteps 200000

# Curriculum learning (Tier 1 → 2 → Boss)
python python_rl_server/train_calypso.py curriculum --timesteps 300000
```

### Değerlendirme

```bash
# Model değerlendirme
python python_rl_server/train_calypso.py eval models/calypso_tier1/best/best_model --episodes 20

# Render ile izleme
python python_rl_server/train_calypso.py eval models/calypso_tier2/best/best_model --render
```

### TensorBoard

```bash
tensorboard --logdir models/calypso_tier1_*/logs
```

---

*CALYPSO - TÜBİTAK İP-2 Projesi*
*Ocak 2026*
