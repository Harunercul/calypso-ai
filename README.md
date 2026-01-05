# CALYPSO AI Bot System - TÜBİTAK İP-2

## Proje Bilgileri

| Bilgi | Değer |
|-------|-------|
| **Proje Adı** | Yapay Zeka Destekli Çok Oyunculu Coop TPS Oyunu - Bot Geliştirme |
| **İş Paketi** | İP-2: Yapay Zeka, Karakter ve Bot Geliştirme |
| **Oyun** | CALYPSO (FPS/TPS) |
| **Destek** | TÜBİTAK 1501 - Sanayi Ar-Ge Projeleri |
| **Geliştirici** | Harun Ercul (AI/Python), MB Oyun (Unreal Engine) |

---

## Dokümantasyon

| # | Dosya | Açıklama |
|---|-------|----------|
| 1 | [Akademik Literatür](docs/01_AKADEMIK_LITERATUR.md) | Projede kullanılan 18 akademik makalenin öncelik sıralaması, DOI linkleri ve kullanım alanları |
| 2 | [Ar-Ge Özgün Katkılar](docs/02_ARGE_OZGUN_KATKILAR.md) | TÜBİTAK için projenin özgün değeri, teknik yenilikler ve Ar-Ge katkıları |
| 3 | [Hakem Demo Senaryoları](docs/03_HAKEM_DEMO_SENARYOLARI.md) | TÜBİTAK hakemi için 3 demo senaryosu: Temel Savaş, Adaptif Zorluk, RL vs Rule-Based |
| 4 | [Unreal Entegrasyon Rehberi](docs/04_UNREAL_ENTEGRASYON_REHBERI.md) | UE5 tarafı için gRPC client kurulumu, C++ kod örnekleri ve Blueprint entegrasyonu |
| 5 | [AI Eğitim Gereksinimleri](docs/05_AI_EGITIM_GEREKSINIMLERI.md) | AI modelini eğitmek için firmadan istenen oyun verileri checklist'i |
| 6 | [Gelecek LLM Fikirleri](docs/06_GELECEK_LLM_FIKIRLERI.md) | İleride eklenebilecek LLM entegrasyonu fikirleri: NPC diyalog, taktik analiz, adaptif hikaye |

---

## Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    UNREAL ENGINE 5                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Bot         │  │ Behavior    │  │ Utility AI  │         │
│  │ Character   │──│ Tree        │──│ Component   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                                                   │
│         │ Observation (64-dim) / Action                     │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────┐           │
│  │           gRPC Client (C++)                  │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │ TCP/IP (port 50051)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PYTHON RL SERVER (Bu Repo)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ gRPC        │  │ PPO Agent   │  │ Reward      │         │
│  │ Service     │──│ (SB3)       │──│ Calculator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Difficulty  │  │ Training    │  │ TensorBoard │         │
│  │ Manager     │  │ Loop        │  │ Logging     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## Kullanılan Teknolojiler

| Kategori | Teknoloji | Versiyon |
|----------|-----------|----------|
| ML Framework | PyTorch | 2.0+ |
| RL Library | Stable-Baselines3 | 2.0+ |
| Communication | gRPC | 1.50+ |
| Monitoring | TensorBoard | 2.0+ |
| Testing | Pytest | 7.0+ |
| Python | Python | 3.10+ |

---

## Akademik Literatür Referansları

### Kritik Makaleler (Direkt Kullanıyoruz)

#### 1. PPO Agent Implementasyonu
> **Chelarescu, P. A. (2022).** A deep reinforcement learning agent for general video game AI framework games. *IEEE ICAICA*.
> DOI: https://doi.org/10.1109/ICAICA54878.2022.9844524
>
> **Kullanım:** PPO algoritması implementasyonu ve hyperparameter seçimi

#### 2. Self-Play Training
> **Oh, I., Rho, S., Moon, S., Son, S., Lee, H., & Chung, J. (2022).** Creating pro-level AI for a real-time fighting game using deep reinforcement learning. *IEEE Transactions on Games*.
> DOI: https://doi.org/10.1109/TG.2021.3049539
>
> **Kullanım:** Self-play curriculum learning, %62 win-rate against pros

#### 3. Utility AI + Behavior Tree Hibrit Mimarisi
> **Hong, Y., Yan, T., & Seo, J. (2023).** GOBT: A synergistic approach to game AI using goal-oriented and utility-based planning in behavior trees. *Journal of Multimedia Information System*.
> DOI: https://doi.org/10.33851/JMIS.2023.10.4.321
>
> **Kullanım:** Utility scoring + BT decision making kombinasyonu

#### 4. Adaptif Zorluk Sistemi (DDA)
> **Pfau, J., Smeddinck, J. D., & Malaka, R. (2020).** Enemy within: Long-term motivation effects of deep player behavior models for dynamic difficulty adjustment. *ACM CHI*.
> DOI: https://doi.org/10.1145/3313831.3376423
>
> **Kullanım:** Player behavior modeling, smooth difficulty transitions

#### 5. FPS Bot RL Systematic Review
> **Almeida, P., Carvalho, V., & Simões, A. (2023).** Reinforcement learning applied to AI bots in first-person shooters: A systematic review. *Algorithms*.
> DOI: https://doi.org/10.3390/a16070323
>
> **Kullanım:** FPS için RL best practices, multi-agent training

### Önemli Referanslar

| Makale | Yazar | Yıl | Kullanım Alanı |
|--------|-------|-----|----------------|
| EvolvingBehavior (UE4) | Partlan et al. | 2022 | BT evolution in Unreal |
| Utility-based FightingICE | Chen et al. | 2021 | Utility function design |
| VizDoom RL Benchmark | Khan et al. | 2024 | FPS RL benchmarking |
| NPC Decision Taxonomy | Uludağlı & Oğuz | 2023 | System comparison |

### Destekleyici Referanslar

- **DDA + PCG + RL:** Huber et al. (2021) - Advanced difficulty adjustment
- **HybrIK:** Li et al. (2021) - Hybrid IK for animations
- **Event-driven BT:** Agis et al. (2020) - Multi-agent coordination
- **BT Survey:** Iovino et al. (2022) - Comprehensive BT overview

---

## Proje Yapısı

```
arge_oyun/
├── README.md                    # Bu dosya
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
│
├── python_rl_server/           # Ana Python paketi
│   ├── __init__.py
│   ├── server/                 # gRPC server implementasyonu
│   │   ├── __init__.py
│   │   ├── grpc_server.py      # Ana server
│   │   └── service_impl.py     # Service implementations
│   │
│   ├── agents/                 # RL Agents
│   │   ├── __init__.py
│   │   ├── ppo_agent.py        # PPO implementasyonu
│   │   ├── base_agent.py       # Abstract base class
│   │   └── rule_based.py       # Karşılaştırma için rule-based
│   │
│   ├── environments/           # Gym environments
│   │   ├── __init__.py
│   │   ├── mock_env.py         # Test için mock environment
│   │   ├── ue_bridge_env.py    # Unreal Engine bridge
│   │   └── observation.py      # Observation space tanımları
│   │
│   ├── training/               # Training scripts
│   │   ├── __init__.py
│   │   ├── train.py            # Ana training script
│   │   ├── callbacks.py        # Custom callbacks
│   │   └── rewards.py          # Reward functions
│   │
│   ├── difficulty/             # Adaptif zorluk sistemi
│   │   ├── __init__.py
│   │   ├── manager.py          # Difficulty manager
│   │   └── player_tracker.py   # Player performance tracking
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration loader
│   │   └── logger.py           # Logging utilities
│   │
│   └── tests/                  # Unit tests
│       ├── __init__.py
│       ├── test_agent.py
│       ├── test_env.py
│       └── test_server.py
│
├── protos/                     # gRPC Proto definitions
│   └── bot_service.proto       # Service tanımları
│
├── configs/                    # Configuration files
│   ├── training_config.yaml    # Training hyperparameters
│   ├── server_config.yaml      # Server settings
│   └── difficulty_config.yaml  # Difficulty levels
│
├── models/                     # Trained models (gitignore)
│   └── .gitkeep
│
├── docs/                       # Documentation
│   ├── API.md                  # API documentation
│   ├── TRAINING.md             # Training guide
│   └── DEPLOYMENT.md           # Deployment guide
│
└── scripts/                    # Utility scripts
    ├── start_server.py         # Server başlatma
    ├── train_agent.py          # Training başlatma
    └── evaluate.py             # Model evaluation
```

---

## Hızlı Başlangıç

### 1. Kurulum

```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies kur
pip install -r requirements.txt

# Proto dosyalarını derle
python -m grpc_tools.protoc -I./protos --python_out=./python_rl_server/server --grpc_python_out=./python_rl_server/server ./protos/bot_service.proto
```

### 2. Mock Environment ile Test

```bash
# Mock environment'ta training
python scripts/train_agent.py --env mock --episodes 1000

# TensorBoard ile izle
tensorboard --logdir ./logs
```

### 3. Server Başlatma

```bash
# gRPC server'ı başlat
python scripts/start_server.py --port 50051 --model ./models/ppo_latest.zip
```

### 4. Unreal Engine Entegrasyonu

Unreal Engine tarafında gRPC client kurulduktan sonra:

```bash
# Production mode'da server
python scripts/start_server.py --port 50051 --mode inference --model ./models/ppo_best.zip
```

---

## Zorluk Seviyeleri

| Seviye | Türkçe Adı | HP | Accuracy | Reaction | Aggression |
|--------|------------|-----|----------|----------|------------|
| 1 | Yolcu | 50 | 20% | 1.0s | 10% |
| 2 | Mürettebat | 75 | 40% | 0.7s | 30% |
| 3 | Gemi Muhafızı | 100 | 60% | 0.5s | 50% |
| 4 | Gemi Polisi | 120 | 70% | 0.4s | 60% |
| 5 | Koruma | 150 | 80% | 0.3s | 70% |
| 6 | Sahil Güvenlik | 175 | 85% | 0.25s | 80% |
| 7 | Özel Kuvvetler | 200 | 95% | 0.15s | 90% |

---

## Reward Fonksiyonu

```python
rewards = {
    'kill_enemy': +10.0,        # Düşman öldürme
    'damage_dealt': +1.0,       # Hasar verme (per 10 HP)
    'damage_taken': -0.5,       # Hasar alma (per 10 HP)
    'death': -10.0,             # Ölme
    'survival_bonus': +0.1,     # Hayatta kalma (per second)
    'objective_progress': +5.0, # Hedef ilerleme
    'team_support': +2.0,       # Takım desteği
    'cover_usage': +0.5,        # Siper kullanımı
}
```

---

## AWS Deployment

### Önerilen Instance Tipleri

| Kullanım | Instance | Spec | Maliyet |
|----------|----------|------|---------|
| Development | t3.large | 2 vCPU, 8GB | ~$0.08/saat |
| Training (CPU) | c5.2xlarge | 8 vCPU, 16GB | ~$0.34/saat |
| Training (GPU) | g4dn.xlarge | T4 GPU, 16GB | ~$0.52/saat |
| Production | t3.medium | 2 vCPU, 4GB | ~$0.04/saat |

### Deployment Adımları

1. Windows Server 2019/2022 AMI seç
2. Python 3.10+ kur
3. CUDA + cuDNN kur (GPU için)
4. Repo'yu clone et
5. Dependencies kur
6. Server'ı systemd/NSSM ile servis olarak çalıştır

---

## Demo Senaryoları (Hakem İçin)

### Senaryo 1: Temel Savaş Davranışları (5-7 dk)
- Bot spawn ve algılama
- Utility AI karar verme
- Siper alma ve kaçış

### Senaryo 2: Adaptif Zorluk (7-10 dk)
- Oyuncu performans metrikleri
- Dinamik zorluk ayarlama
- Yumuşak geçişler

### Senaryo 3: RL vs Rule-Based Karşılaştırma (10-12 dk)
- Yan yana bot davranışları
- Training grafikleri (TensorBoard)
- Performans metrikleri

---

## Lisans

TÜBİTAK 1501 Sanayi Ar-Ge Projeleri Destekleme Programı kapsamında geliştirilmiştir.
Tüm hakları MB Oyun Yazılım ve Pazarlama A.Ş.'ye aittir.

---

## İletişim

| Rol | İsim |
|-----|------|
| AI Geliştirici | Harun Ercul |
| Bilimsel Danışman | Prof. Dr. Turgay Bilgin |
| Proje Yürütücüsü | Erdoğan Atmaca |

---

*Son Güncelleme: Ocak 2025*
