# MQTT Topics

basil-ai の MQTT トピック設計と JSON payload スキーマ。
ブローカーは Pi 上の Mosquitto(ローカル完結、クラウド不使用)。

トピック定数は `shared/mqtt_topics.py` に集約し、Python 側はそこから import する。
ESP32 側(C++)は同じ文字列を直書きする(共有ヘッダ化は過剰)。

---

## トピック一覧

| 方向 | トピック | QoS | Retained | 概要 |
|------|---------|-----|----------|------|
| ESP32 → Pi | `picopico/basil/sensor/env` | 1 | no | 温湿度・照度 |
| ESP32 → Pi | `picopico/basil/sensor/soil` | 1 | no | 静電容量式土壌水分 |
| ESP32 → Pi | `picopico/basil/sensor/weight` | 1 | no | 鉢重量(HX711) |
| ESP32 → Pi | `picopico/basil/sensor/tank` | 1 | yes | フロートスイッチ状態 |
| ESP32 → Pi | `picopico/basil/status` | 1 | yes | ESP32 側のハートビート |
| Pi → ESP32 | `picopico/basil/command/pump` | 1 | no | 給水指示(ml 指定) |
| Pi → ESP32 | `picopico/basil/command/led` | 1 | yes | LED ON/OFF |
| Pi → (ログ) | `picopico/basil/ai/report` | 1 | yes | Claude 判断結果の記録(LWT 兼用) |

`picopico/basil/sensor/+` や `picopico/basil/command/+` で一括 subscribe できる設計。

---

## Payload スキーマ

すべて JSON、UTF-8。タイムスタンプは ISO8601(`Z`)。

### `picopico/basil/sensor/env`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "temperature_c": 24.3,
  "humidity_pct": 48.1,
  "lux": 1820
}
```

### `picopico/basil/sensor/soil`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "raw_adc": 1832,
  "moisture_pct": 42.5
}
```

`moisture_pct` は ESP32 で一次キャリブレーションした値。
Pi 側でも `raw_adc` を保存しておき、ドリフト検知に使う。

### `picopico/basil/sensor/weight`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "grams": 1432.7,
  "tare_ok": true
}
```

### `picopico/basil/sensor/tank`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "empty": false
}
```

`empty=true` のときは Pi 側で**どんな判断でも給水を拒否**する(safety.md §タンク空)。

### `picopico/basil/status`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "boot_count": 42,
  "rssi_dbm": -58,
  "free_heap": 180000,
  "fw_version": "0.1.0"
}
```

---

### `picopico/basil/command/pump`

Pi → ESP32 の給水指示。

```json
{
  "ts": "2026-04-23T12:00:10Z",
  "request_id": "req-2026-04-23T12-00-10Z-abc123",
  "ml": 25,
  "max_seconds": 12,
  "source": "claude_guarded"
}
```

- `ml`: Pi のセーフティガード通過後の最終値。ESP32 は無条件に実行する
- `max_seconds`: フェイルセーフ上限(時間切れでポンプ OFF)
- `source`: `claude_guarded` / `rule_based` / `manual` のいずれか。監査用

### `picopico/basil/command/led`

```json
{
  "ts": "2026-04-23T12:00:00Z",
  "on": true,
  "brightness": 100
}
```

Retained。ESP32 再接続時に即反映する。

---

### `picopico/basil/ai/report`

Claude の判断ログ。Pi 内部で購読するデバッグ用 + 将来的に外部ダッシュボード用。

```json
{
  "ts": "2026-04-23T12:00:05Z",
  "request_id": "req-2026-04-23T12-00-05Z-abc123",
  "claude_suggestion": {
    "water": true,
    "ml": 30,
    "reason": "葉が下垂、土壌表層乾燥、重量減"
  },
  "final_decision": {
    "water": true,
    "ml": 25,
    "clipped": true,
    "reason_if_clipped": "MAX_WATER_ML_PER_SHOT=40 以下だが cooldown 条件は通過。ml を 30→25 にクリップ"
  }
}
```

---

## Last Will (LWT)

- Pi 側クライアントは接続時に `picopico/basil/ai/report` に
  `{"status":"offline","ts":"..."}` を LWT として登録する
- ESP32 側は `picopico/basil/status` に同種の LWT を登録する

---

## 認証

ローカル MQTT だが、同一 LAN に他端末が入る可能性があるため、
`MQTT_USERNAME` / `MQTT_PASSWORD` 必須運用とする(`.env` で設定)。
