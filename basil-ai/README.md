# basil-ai

「AIにバジル栽培させてみた」YouTube 企画(チャンネル: ワンルーム農園)の
IoT システム一式。Claude API に水やりの可否・量を判断させ、その過程を撮影する。

> プロジェクト憲法は [CLAUDE.md](./CLAUDE.md) を参照。
> ルール変更はまず CLAUDE.md を更新してから実装する。

---

## アーキテクチャ

```
[ESP32 Freenove] ──MQTT──> [Raspberry Pi 4B] ──HTTPS──> [Claude API]
     │                           │
 センサー読み取り              画像撮影
 ポンプ制御                   ルールベース判定
 判断はしない                 セーフティガード
                              LINE Messaging API 通知
```

- ESP32: センサー + ポンプ(判断ゼロ)
- Raspberry Pi: 画像、Claude 呼び出し、ガード、SQLite、通知
- Claude API: 画像 + 数値 → 給水提案(JSON)

詳細は [docs/architecture.md](./docs/architecture.md)。

---

## ディレクトリ

```
basil-ai/
├── CLAUDE.md            # プロジェクト憲法
├── PROGRESS.md          # フェーズ別チェックリスト
├── README.md            # 本ファイル
├── .env.example
├── .gitignore
├── docs/                # 設計ドキュメント
├── esp32/               # PlatformIO プロジェクト(センサー + ポンプ)
├── raspi/               # Pi 側 Python (ゲートウェイ + AI 連携)
└── shared/              # 両層で共有する定数(MQTT トピック等)
```

---

## クイックスタート(Pi 側)

```bash
cd raspi
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic python-dotenv opencv-python paho-mqtt
cp ../.env.example ../.env   # 値を埋める
python main.py
```

ESP32 側は `esp32/README.md` を参照。

---

## 現在地

**フェーズ 0: 設計整理中**

詳細は [PROGRESS.md](./PROGRESS.md) を参照。

---

## 重要な禁止事項(詳細は CLAUDE.md §4)

- LINE Notify は使わない(2025-03 終了)。LINE Messaging API を使う
- 抵抗式土壌水分センサーは使わない。静電容量式のみ
- ESP32-CAM は使わない。USB Webカメラを使う
- ESP32 に判断ロジックを載せない
- クラウド MQTT は使わない。Pi 上の Mosquitto のみ
