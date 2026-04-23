# raspi/

basil-ai の Raspberry Pi 4B 側 Python アプリ。
Mosquitto にぶら下がり、USB Webカメラで撮影し、Claude API に判断を仰ぎ、
セーフティガードを通した最終決定を ESP32 に指示する。

> 憲法: [../CLAUDE.md](../CLAUDE.md)
> プロンプト: [../docs/claude-api-prompt.md](../docs/claude-api-prompt.md)
> ガード仕様: [../docs/safety-guards.md](../docs/safety-guards.md)

---

## セットアップ

```bash
cd raspi
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic python-dotenv opencv-python paho-mqtt
cp ../.env.example ../.env   # 値を埋める
python main.py
```

Mosquitto は別途インストール・起動しておく:

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

---

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `main.py` | エントリーポイント。スケジューラとイベントループ |
| `mqtt_handler.py` | Mosquitto 接続、subscribe/publish |
| `claude_client.py` | Anthropic SDK で画像 + 数値 → JSON |
| `camera.py` | USB Webカメラで静止画取得 |
| `safety.py` | セーフティガード(最終決定権) |
| `db.py` | SQLite 4 テーブル |

各ファイルは現状スケルトン(関数シグネチャ + docstring + TODO)のみ。
フェーズ 3〜4 で中身を実装する。

---

## 依存パッケージ

`requirements.txt` はフェーズ 3 で生成する。現時点の予定:

```
anthropic
python-dotenv
opencv-python
paho-mqtt
```

Python 3.11+ を想定。
