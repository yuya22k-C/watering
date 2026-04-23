# Safety Guards

basil-ai の Pi 側セーフティガード仕様。実装は `raspi/safety.py`。
Claude API の応答はあくまで「提案」で、最終決定はここで行う。

---

## 原則

1. Claude 応答を**そのまま**ポンプに流さない。必ずガードを通す
2. ガードが拒否した場合は `decisions.clipped=1` + `guard_reason` に理由を残す
3. ガード自身は **絶対に例外で落ちない**。想定外値はフェイルセーフ(給水しない)側に倒す
4. 全ガードは独立(どれかが OK でも、別のガードが NG なら拒否)

---

## ガード一覧と優先順

数値が小さいほど先に判定される(ショートサーキット)。

| # | ガード | 条件 | 挙動 |
|---|-------|------|------|
| 1 | タンク空 | `tank_empty=true` | **即拒否**。通知を送る |
| 2 | センサー欠損 | 直近 N 分で sensor 値が来ていない | 拒否。LINE で警告 |
| 3 | 異常値 | 温度 -10〜50°C 外、湿度 0〜100 外、重量 0〜3000g 外 | 拒否 |
| 4 | クールダウン | 前回給水から `MIN_COOLDOWN_MINUTES` 未満 | 拒否(Claude が water=true でも) |
| 5 | 1 日上限 | 過去 24h の合計 ml > 日次上限 | 拒否 |
| 6 | 1 回上限 | 応答 ml > `MAX_WATER_ML_PER_SHOT` | **クリップ**して実行(拒否ではない) |
| 7 | 重量急減 | 前回観測から -100g 超 | 拒否(漏水・鉢ひっくり返し疑い) |

---

## `.env` で調整可能なパラメータ

| キー | デフォルト | 説明 |
|------|----------|------|
| `MAX_WATER_ML_PER_SHOT` | 40 | 1 回の給水上限(ml)。ここを超えたらクリップ |
| `MIN_COOLDOWN_MINUTES` | 180 | 前回給水からのクールダウン(分) |
| `MAX_WATER_ML_PER_DAY` | 120 | 直近 24h の合計上限(ml)。デフォは 3 回 × 40ml |
| `SENSOR_STALE_MINUTES` | 10 | この分数以上新しいセンサー値が無ければ拒否 |
| `TANK_EMPTY_SHUTDOWN` | 1 | 1 なら tank_empty=true で全拒否。0 でも警告は出す |

---

## Claude API タイムアウト / エラー時のフォールバック

Claude 呼び出しは以下で保護する。

1. HTTP タイムアウト: 20 秒
2. リトライ: 指数バックオフ 2 回(2s, 4s)。3 回目で失敗なら諦める
3. JSON パース失敗: `source=rule_based` にフォールバック

### ルールベース判定(フォールバック本体)

Claude 不在時に Pi 単独で判断する簡易ロジック。

```
def rule_based_decide(latest, recent_24h) -> dict:
    # 1. tank_empty はそもそも safety で弾くが、念のため
    if latest.tank_empty:
        return {"water": False, "ml": 0, "reason": "tank empty"}

    # 2. 土壌水分 >= 45% → やらない
    if latest.soil_pct >= 45:
        return {"water": False, "ml": 0, "reason": "soil moist enough"}

    # 3. 土壌水分 < 30% かつ 重量 24h 減少 → 給水(控えめに)
    if latest.soil_pct < 30 and recent_24h.weight_trend < -10:
        return {"water": True, "ml": 20, "reason": "dry + weight down"}

    # 4. 土壌 30-45% で重量減が顕著 → 小給水
    if recent_24h.weight_trend < -30:
        return {"water": True, "ml": 15, "reason": "weight dropped"}

    # 5. それ以外はやらない
    return {"water": False, "ml": 0, "reason": "no strong signal"}
```

数値は運用してから詰める。フェーズ 5 の長期テストで調整する。

---

## 通知(LINE Messaging API)

以下のイベントで LINE 通知する。通知が失敗しても動作は継続する(通知失敗で例外にしない)。

| イベント | 優先度 |
|---------|-------|
| Pi 起動 / 正常停止 | info |
| 給水実行(ml と理由) | info |
| Claude API 失敗 → ルールベースにフォールバック | warn |
| タンク空検知 | **alert** |
| センサー異常値 | warn |
| 重量急減(漏水疑い) | **alert** |

---

## 手動オーバーライド

開発中・撮影中に人間が介入できるよう、以下を用意する。

- `raspi/tools/manual_water.py --ml 30`
  → `picopico/basil/command/pump` に source=`manual` で送信
  → `watering_history` に記録
- セーフティガードは manual 操作にも適用する(タンク空・異常値では実行しない)
- 対照個体への手動給水を記録する CLI も同ファイルに含める
