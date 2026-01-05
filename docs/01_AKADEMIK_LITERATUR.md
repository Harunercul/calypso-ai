# Akademik Literatür ve Referanslar
## TÜBİTAK İP-2: Yapay Zeka, Karakter ve Bot Geliştirme

---

## Özet

Bu projede **18 hakemli makale** referans alınmıştır. Makaleler 6 kategoride sınıflandırılmış olup, projedeki kullanım önceliklerine göre aşağıda listelenmiştir.

---

## 🔴 KRİTİK - Doğrudan Kullandığımız Makaleler

Bu makaleler sistemimizin temelini oluşturuyor. Hakem bunları mutlaka soracak.

### 1. PPO Agent Implementasyonu

> **Chelarescu, P. A. (2022).** A deep reinforcement learning agent for general video game AI framework games. *2022 IEEE Conference on Games (CoG)*, 1–4.
>
> DOI: https://doi.org/10.1109/CoG51982.2022.9844524

**Projede Kullanımı:**
- PPO algoritması hyperparameter seçimi
- Observation space tasarımı (64-dim vector)
- Training loop yapısı
- Stable-Baselines3 entegrasyonu

**Kodda Nerede:** `python_rl_server/agents/ppo_agent.py`

---

### 2. Self-Play Training & Pro-Level AI

> **Oh, I., Rho, S., Moon, S., Son, S., Lee, H., & Chung, J. (2022).** Creating pro-level AI for a real-time fighting game using deep reinforcement learning. *IEEE Transactions on Games*, 14(2), 212–220.
>
> DOI: https://doi.org/10.1109/TG.2021.3049539

**Projede Kullanımı:**
- Curriculum learning stratejisi
- Self-play eğitim yaklaşımı
- %62 win-rate hedefi referansı
- Profesyonel seviye bot tasarımı

**Kodda Nerede:** `configs/training_config.yaml` (curriculum stages)

---

### 3. Utility AI + Behavior Tree Hibrit Sistemi

> **Hong, Y., Yan, T., & Seo, J. (2023).** GOBT: A synergistic approach to game AI using goal-oriented and utility-based planning in behavior trees. *Journal of Multimedia Information System*, 10(4), 321–332.
>
> DOI: https://doi.org/10.33851/JMIS.2023.10.4.321

**Projede Kullanımı:**
- Utility scoring mekanizması
- Consideration-based karar verme
- 8 aksiyon tipi tasarımı (Attack, Cover, Flee, vs.)
- Response curve'ler

**Kodda Nerede:** `python_rl_server/agents/rule_based.py`

---

### 4. Adaptif Zorluk Sistemi (DDA)

> **Pfau, J., Smeddinck, J. D., & Malaka, R. (2020).** Enemy within: Long-term motivation effects of deep player behavior models for dynamic difficulty adjustment. *2020 CHI Conference on Human Factors in Computing Systems*, 1–10.
>
> DOI: https://doi.org/10.1145/3313831.3376423

**Projede Kullanımı:**
- Player performance tracking metrikleri
- Skill score hesaplama formülü
- Smooth difficulty transitions
- Motivation-based DDA

**Kodda Nerede:**
- `python_rl_server/difficulty/manager.py`
- `python_rl_server/difficulty/player_tracker.py`

---

### 5. FPS Bot RL Sistematik Derlemesi

> **Almeida, P., Carvalho, V., & Simões, A. (2023).** Reinforcement learning applied to AI bots in first-person shooters: A systematic review. *Algorithms*, 16(7), Article 323.
>
> DOI: https://doi.org/10.3390/a16070323

**Projede Kullanımı:**
- FPS oyunları için RL best practices
- Multi-agent training mimarisi
- State/action space tasarım prensipleri
- Reward shaping stratejileri

**Kodda Nerede:** `python_rl_server/training/rewards.py`

---

## 🟡 ÖNEMLİ - Destekleyici Referanslar

Bu makaleler tasarım kararlarımızı destekliyor.

### 6. Behavior Tree Evolution (Unreal Engine 4!)

> **Partlan, N., Soto, L., Howe, J., et al. (2022).** EvolvingBehavior: Towards co-creative evolution of behavior trees for game NPCs. *Proceedings of FDG '22*, 1–13.
>
> DOI: https://doi.org/10.1145/3555858.3555896

**Neden Önemli:** UE4'te genetik programlama ile BT - Firma için referans

---

### 7. Utility Function Learning

> **Chen, T., Richoux, F., Torres, J. M., & Inoue, K. (2021).** Interpretable utility-based models applied to the FightingICE platform. *2021 IEEE Conference on Games (CoG)*, 1–8.
>
> DOI: https://doi.org/10.1109/CoG52621.2021.9619121

**Neden Önemli:** İnsan verisinden utility öğrenme - %64-83 doğruluk

---

### 8. VizDoom FPS Benchmark

> **Khan, A., Shah, A. A., Khan, L., et al. (2024).** Using VizDoom research platform scenarios for benchmarking reinforcement learning algorithms in first-person shooter games. *IEEE Access*, 12, 15105–15132.
>
> DOI: https://doi.org/10.1109/ACCESS.2024.3358203

**Neden Önemli:** FPS oyunlarında RL kıyaslama yöntemleri

---

### 9. NPC Karar Verme Taksonomisi

> **Uludağlı, M. Ç., & Oğuz, K. (2023).** Non-player character decision-making in computer games. *Artificial Intelligence Review*, 56(12), 14159–14191.
>
> DOI: https://doi.org/10.1007/s10462-023-10491-7

**Neden Önemli:** FSM, BT, Rule-based, ML karşılaştırması - Sistemimizi konumlandırma

---

### 10. Multi-Agent Utility Theory

> **Rădulescu, R., Mannion, P., Roijers, D. M., & Nowé, A. (2020).** Multi-objective multi-agent decision making: A utility-based analysis and survey. *Autonomous Agents and Multi-Agent Systems*, 34(1), 1–52.
>
> DOI: https://doi.org/10.1007/s10458-019-09433-x

**Neden Önemli:** Çok ajanlı sistemlerde utility fonksiyonları

---

## 🟢 TEORİK ARKA PLAN

Bu makaleler akademik derinlik sağlıyor.

### Davranış Ağaçları

| # | Makale | Katkı |
|---|--------|-------|
| 11 | Agis et al. (2020) | Event-driven BT, NPC koordinasyonu |
| 12 | Fronek et al. (2020) | Prosedürel BT üretimi |
| 13 | Iovino et al. (2022) | BT survey - oyundan robotiğe |

### Dinamik Zorluk

| # | Makale | Katkı |
|---|--------|-------|
| 14 | Moschovitis & Denisova (2023) | Biyometrik DDA (kalp atışı) |
| 15 | Huber et al. (2021) | DRL + PCG kombinasyonu |

### Inverse Kinematics (Animasyon)

| # | Makale | Katkı |
|---|--------|-------|
| 16 | Voleti et al. (2022) | SMPL-IK - öğrenilmiş IK |
| 17 | Agrawal et al. (2023) | SKEL-IK - poz koruma |
| 18 | Li et al. (2021) | HybrIK - hibrit analitik-neural |

---

## Hakeme Ne Diyeceksin?

### Kısa Versiyon:

> "Sistemimizi geliştirirken **Chelarescu (2022)**'nin PPO yaklaşımını, **Hong et al. (2023)**'in GOBT hibrit mimarisini ve **Pfau et al. (2020)**'un DDA modellerini temel aldık. FPS domain'i için **Almeida et al. (2023)**'ün sistematik derlemesindeki best practice'leri uyguladık."

### Detaylı Versiyon:

> "Projemizde 18 hakemli makaleyi inceledik. PPO implementasyonumuz Chelarescu (2022)'nin GVGAI çalışmasından esinlenmiştir. Utility AI sistemimiz Hong et al. (2023)'in GOBT framework'ünü referans alır. Adaptif zorluk sistemimiz Pfau et al. (2020)'un derin oyuncu davranış modellerini kullanır. Rule-based agent'ımız Chen et al. (2021)'in yorumlanabilir utility modellerinden faydalanmıştır."

---

## Kod-Makale Eşleştirmesi

| Kod Dosyası | Referans Makale |
|-------------|-----------------|
| `ppo_agent.py` | Chelarescu (2022), Oh et al. (2022) |
| `rule_based.py` | Hong et al. (2023), Chen et al. (2021) |
| `rewards.py` | Almeida et al. (2023) |
| `manager.py` | Pfau et al. (2020) |
| `player_tracker.py` | Pfau et al. (2020), Moschovitis (2023) |
| `mock_env.py` | Khan et al. (2024) - VizDoom benchmark |
| `callbacks.py` | Oh et al. (2022) - curriculum learning |

---

## PDF Makaleler

Tüm makaleler hocanın reposunda mevcut:
```
https://github.com/ttbilgin/mbgames_project/tree/main/Work_Package_2/BilimselMakaleler
```

### Okunması Gereken Öncelik Sırası:

1. ⭐ `Creating_Pro-Level_AI_...` (Oh et al. 2022)
2. ⭐ `A_Deep_Reinforcement_Learning_Agent_...` (Chelarescu 2022)
3. ⭐ `jmis-10-4-321.pdf` (Hong et al. 2023 - GOBT)
4. ⭐ `3313831.3376423.pdf` (Pfau et al. 2020 - DDA)
5. `algorithms-16-00323.pdf` (Almeida 2023 - FPS RL Review)

---

*TÜBİTAK İP-2 Projesi - Ocak 2025*
