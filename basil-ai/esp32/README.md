# esp32/

Freenove ESP32-WROVER 用ファームウェア。PlatformIO プロジェクトとしてこのディレクトリ直下に展開する予定。

> 憲法: [../CLAUDE.md](../CLAUDE.md)
>
> **ESP32 に判断ロジックは載せない**。センサー値の publish と、Pi から来たコマンドの実行のみ。

---

## プロジェクト方針(フェーズ 2 で実装)

### フレームワーク

- PlatformIO + Arduino framework (ESP32)
- board: `esp-wrover-kit`(Freenove ESP32-WROVER 相当)
- 言語: C++

### 主要ライブラリ(予定)

| 用途 | ライブラリ |
|------|-----------|
| MQTT | `PubSubClient` or `AsyncMqttClient` |
| SHT31(温湿度) | `Adafruit SHT31 Library` |
| BH1750(照度) | `BH1750` (claws) |
| HX711(ロードセル) | `bogde/HX711` |
| I2C | 標準 `Wire` |

### `platformio.ini` の予定

```ini
[env:esp-wrover-kit]
platform = espressif32
board = esp-wrover-kit
framework = arduino
monitor_speed = 115200
lib_deps =
  knolleary/PubSubClient
  adafruit/Adafruit SHT31 Library
  claws/BH1750
  bogde/HX711
build_flags =
  -DCORE_DEBUG_LEVEL=3
```

Wi-Fi / MQTT 資格情報は `platformio.ini` には書かず、
`include/secrets.h`(gitignore 対象)に切り出す。

---

## 責務

### やること

- SHT31 / BH1750 / 静電容量 / HX711 / フロートスイッチの読み取り
- センサー値を JSON で `picopico/basil/sensor/*` に publish
- `picopico/basil/command/pump` 受信 → DRV8833 駆動 → 指定時間で必ず停止
- `picopico/basil/command/led` 受信 → LED ON/OFF
- Wi-Fi / MQTT の自動再接続
- ウォッチドッグタイマーによる自己復旧

### やらないこと

- 「土壌水分 < X% だから給水する」などの**判断**
- Claude API 呼び出し
- 撮影(USB Webカメラは Pi 側)
- どんなしきい値でも、ESP32 単独では給水を起動しない

---

## フェイルセーフ

- ブート直後はポンプ GPIO を LOW にして待機
- MQTT 未接続のときは給水コマンドを一切受けない
- 給水コマンドには必ず `max_seconds` がある。経過したら必ず停止する
- Wi-Fi 断を検知したらポンプを即停止
- ウォッチドッグで N 秒動作が止まったら自己再起動

---

## ディレクトリ(フェーズ 2 で追加)

```
esp32/
├── README.md            # 本ファイル
├── platformio.ini
├── include/
│   └── secrets.h        # gitignore 対象
├── src/
│   └── main.cpp
└── lib/
```
