# Unreal Engine Entegrasyon Rehberi
## TÜBİTAK İP-2 AI Bot System - Firma İçin

---

## Genel Bakış

Python RL Server hazır ve çalışıyor. Unreal Engine tarafında gRPC client yazılması gerekiyor.

```
Unreal Engine (C++) ◄─── gRPC (TCP:50051) ───► Python RL Server
```

---

## 1. Proto Dosyası

`protos/bot_service.proto` dosyasını kullanın. Bu dosya tüm mesaj formatlarını ve servisleri tanımlar.

### Unreal Engine için gRPC kurulumu:
1. gRPC C++ kütüphanesini projeye ekleyin
2. Proto dosyasını C++ koduna derleyin:
```bash
protoc --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc=grpc_cpp_plugin bot_service.proto
```

---

## 2. Observation Space (64-dim Float Array)

Bot'un gördüğü dünyayı 64 boyutlu normalized float array olarak gönderin.

### Yapı:

```cpp
// Tüm değerler 0.0 - 1.0 arası normalize edilmeli
float observation[64];

// [0-15] Bot Self State
observation[0] = bot->Health / MaxHealth;           // health
observation[1] = bot->Armor / MaxArmor;             // armor
observation[2] = bot->PrimaryAmmo / MaxAmmo;        // ammo_primary
observation[3] = bot->SecondaryAmmo / MaxAmmo;      // ammo_secondary
observation[4] = NormalizePosition(bot->X);          // pos_x (0-1)
observation[5] = NormalizePosition(bot->Y);          // pos_y (0-1)
observation[6] = NormalizePosition(bot->Z);          // pos_z (0-1)
observation[7] = bot->Yaw / 180.0f;                  // rotation_yaw (-1 to 1)
observation[8] = bot->Pitch / 90.0f;                 // rotation_pitch (-1 to 1)
observation[9] = NormalizeVelocity(bot->VelX);       // velocity_x
observation[10] = NormalizeVelocity(bot->VelY);      // velocity_y
observation[11] = NormalizeVelocity(bot->VelZ);      // velocity_z
observation[12] = bot->IsInCover ? 1.0f : 0.0f;      // is_in_cover
observation[13] = bot->IsReloading ? 1.0f : 0.0f;    // is_reloading
observation[14] = bot->IsAiming ? 1.0f : 0.0f;       // is_aiming
observation[15] = NormalizeTime(TimeSinceLastDamage); // time_since_damage

// [16-23] Enemy 1 (En yakın düşman)
observation[16] = NormalizeDistance(enemy1->Distance); // distance (0=yakın, 1=uzak)
observation[17] = GetRelativeAngle(enemy1) / 180.0f;   // angle (-1 to 1)
observation[18] = enemy1->EstimatedHealth;              // health_estimate
observation[19] = enemy1->IsVisible ? 1.0f : 0.0f;      // is_visible
observation[20] = enemy1->IsInCover ? 1.0f : 0.0f;      // is_in_cover
observation[21] = CalculateThreatLevel(enemy1);         // threat_level (0-1)
observation[22] = GetVelocityTowardsMe(enemy1);         // velocity_towards_me (-1 to 1)
observation[23] = enemy1->IsAimingAtMe ? 1.0f : 0.0f;   // is_aiming_at_me

// [24-31] Enemy 2 (Aynı yapı)
// [32-39] Enemy 3 (Aynı yapı)
// Düşman yoksa tüm değerler 0.0 veya default

// [40-55] Environment State
observation[40] = NormalizeDistance(cover1->Distance);  // cover1_distance
observation[41] = GetRelativeAngle(cover1) / 180.0f;    // cover1_angle
// ... cover2, cover3, cover4 (42-47)
observation[48] = NormalizeDistance(objective->Distance); // objective_distance
observation[49] = GetRelativeAngle(objective) / 180.0f;   // objective_angle
observation[50] = objective->Progress;                     // objective_progress (0-1)
observation[51] = NormalizeDistance(dangerZone->Distance); // danger_zone_distance
observation[52] = GetRelativeAngle(dangerZone) / 180.0f;   // danger_zone_angle
observation[53] = NormalizeTime(TimeInCombat);             // time_in_combat
observation[54] = enemiesInRange / 10.0f;                  // enemies_in_range (normalized)
observation[55] = alliesInRange / 10.0f;                   // allies_in_range (normalized)

// [56-63] Team State
observation[56] = teamAverageHealth;                       // team_health_avg
observation[57] = aliveTeammates / totalTeammates;         // team_alive_ratio
observation[58] = NormalizeDistance(nearestAlly->Distance); // nearest_ally_distance
observation[59] = GetRelativeAngle(nearestAlly) / 180.0f;   // nearest_ally_angle
observation[60] = teamObjectiveProgress;                    // team_objective_progress
observation[61] = teamKills / 20.0f;                        // team_kills (normalized)
observation[62] = teamDeaths / 20.0f;                       // team_deaths (normalized)
observation[63] = allyNeedsSupport ? 1.0f : 0.0f;          // support_needed
```

---

## 3. Action Space (Server'dan Dönen)

Server integer (0-8) döndürür. Bu aksiyonu uygulayın:

```cpp
enum class EBotAction : uint8
{
    IDLE = 0,        // Bekle
    ATTACK = 1,      // Saldır (mevcut hedefe ateş et)
    TAKE_COVER = 2,  // En yakın sipere git
    FLEE = 3,        // Düşmandan uzaklaş
    RELOAD = 4,      // Mermi doldur
    PATROL = 5,      // Devriye noktasına git
    INVESTIGATE = 6, // Son bilinen düşman pozisyonuna git
    SUPPORT = 7,     // Takım arkadaşına yardıma git
    FLANK = 8        // Yan atak pozisyonuna git
};

void ABotAIController::ExecuteAction(int32 ActionType)
{
    switch (ActionType)
    {
        case 0: // IDLE
            StopMovement();
            break;
        case 1: // ATTACK
            if (CurrentTarget)
            {
                SetFocus(CurrentTarget);
                FireWeapon();
            }
            break;
        case 2: // TAKE_COVER
            MoveToNearestCover();
            break;
        case 3: // FLEE
            MoveAwayFromThreat();
            break;
        case 4: // RELOAD
            ReloadWeapon();
            break;
        case 5: // PATROL
            MoveToNextPatrolPoint();
            break;
        case 6: // INVESTIGATE
            MoveToLastKnownEnemyLocation();
            break;
        case 7: // SUPPORT
            MoveToAllyInNeed();
            break;
        case 8: // FLANK
            MoveToFlankPosition();
            break;
    }
}
```

---

## 4. gRPC Client Örneği (C++)

```cpp
#include "bot_service.grpc.pb.h"
#include <grpcpp/grpcpp.h>

class BotAIClient
{
public:
    BotAIClient(std::shared_ptr<grpc::Channel> channel)
        : stub_(calypso::ai::BotAIService::NewStub(channel)) {}

    int GetAction(const std::vector<float>& observation)
    {
        calypso::ai::GameState request;
        request.set_bot_id("bot_1");
        request.set_timestamp(FDateTime::Now().ToUnixTimestamp());

        // Self state
        auto* self_state = request.mutable_self_state();
        self_state->set_health(observation[0]);
        self_state->set_armor(observation[1]);
        // ... diğer alanlar

        calypso::ai::BotAction response;
        grpc::ClientContext context;

        grpc::Status status = stub_->GetAction(&context, request, &response);

        if (status.ok())
        {
            return response.action_type();
        }

        return 0; // Default: IDLE
    }

private:
    std::unique_ptr<calypso::ai::BotAIService::Stub> stub_;
};

// Kullanım
auto channel = grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials());
BotAIClient client(channel);

// Her tick'te
std::vector<float> observation = BuildObservation(bot);
int action = client.GetAction(observation);
ExecuteAction(action);
```

---

## 5. Unreal Engine Build.cs

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "AIModule",
    "NavigationSystem",
    "GameplayTasks",
    // gRPC için
    "Networking",
    "Sockets"
});
```

---

## 6. Python Server Başlatma

Firma tarafında test için:

```bash
cd /path/to/arge_oyun
python scripts/start_server.py --model ./models/ppo_20260102_225153/ppo_final.zip --port 50051
```

Rule-based test için (model olmadan):
```bash
python scripts/start_server.py --rule-based --port 50051
```

---

## 7. Test Akışı

1. Python server'ı başlat
2. Unreal Engine'de bot spawn et
3. Bot her tick'te:
   - Observation oluştur (64-dim)
   - gRPC ile server'a gönder
   - Action al (0-8)
   - Action'ı uygula
4. Opsiyonel: Reward gönder (training mode için)

---

## 8. Zorluk Seviyeleri

Server'dan `DifficultyService.GetCurrentDifficulty()` ile mevcut zorluk alınabilir:

| Level | İsim | HP | Accuracy | Reaction |
|-------|------|-----|----------|----------|
| 1 | Yolcu | 50 | 20% | 1.0s |
| 2 | Mürettebat | 75 | 40% | 0.7s |
| 3 | Gemi Muhafızı | 100 | 60% | 0.5s |
| 4 | Gemi Polisi | 120 | 70% | 0.4s |
| 5 | Koruma | 150 | 80% | 0.3s |
| 6 | Sahil Güvenlik | 175 | 85% | 0.25s |
| 7 | Özel Kuvvetler | 200 | 95% | 0.15s |

---

## İletişim

Python RL Server sorularınız için: Harun Ercul

Server port: **50051** (TCP)

---

*Bu doküman TÜBİTAK İP-2 kapsamında hazırlanmıştır.*
