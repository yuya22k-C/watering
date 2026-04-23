# DB Schema

basil-ai の SQLite スキーマ。4 テーブル構成。
実装は `raspi/db.py` が担当する。

- DB ファイル: `basil.db`(`.env` の `DB_PATH` で上書き可能)
- タイムスタンプは ISO8601 UTC 文字列で統一(`YYYY-MM-DDTHH:MM:SSZ`)
- 複合クエリしやすいよう、時刻列にインデックスを貼る

---

## 1. `sensors` — センサー値の生ログ

```sql
CREATE TABLE IF NOT EXISTS sensors (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT    NOT NULL,                 -- ISO8601 UTC
    individual    TEXT    NOT NULL,                 -- 'ai' or 'control'
    kind          TEXT    NOT NULL,                 -- 'env' | 'soil' | 'weight' | 'tank'
    temperature_c REAL,
    humidity_pct  REAL,
    lux           REAL,
    soil_raw_adc  INTEGER,
    soil_pct      REAL,
    weight_g      REAL,
    tank_empty    INTEGER,                          -- 0/1
    raw_json      TEXT    NOT NULL                  -- 元 payload の生 JSON
);

CREATE INDEX IF NOT EXISTS idx_sensors_ts         ON sensors(ts);
CREATE INDEX IF NOT EXISTS idx_sensors_individual ON sensors(individual, ts);
CREATE INDEX IF NOT EXISTS idx_sensors_kind       ON sensors(kind, ts);
```

`kind` ごとに埋まる列が違う(sparse)。`raw_json` に常に生値を入れておくことで、
スキーマ追加に強くする。

---

## 2. `decisions` — 判断ログ(Claude とガード両方)

```sql
CREATE TABLE IF NOT EXISTS decisions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    request_id      TEXT    NOT NULL UNIQUE,
    source          TEXT    NOT NULL,               -- 'claude_guarded' | 'rule_based' | 'manual'
    claude_water    INTEGER,                        -- 0/1 NULL=claude 呼ばず
    claude_ml       INTEGER,
    claude_reason   TEXT,
    final_water     INTEGER NOT NULL,               -- 0/1 最終決定
    final_ml        INTEGER NOT NULL,               -- 実際に送る ml
    clipped         INTEGER NOT NULL DEFAULT 0,     -- 0/1
    guard_reason    TEXT,                           -- クリップ/拒否理由
    image_path      TEXT,                           -- captures/*.jpg
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_decisions_ts ON decisions(ts);
```

- `source='rule_based'` のときは `claude_*` はすべて NULL
- `clipped=1` のときは `guard_reason` が必ず埋まる

---

## 3. `api_logs` — Claude API 呼び出しの入出力

動画素材兼デバッグ用。**入出力の全文を保存する**。

```sql
CREATE TABLE IF NOT EXISTS api_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,
    request_id      TEXT    NOT NULL,
    model           TEXT    NOT NULL,               -- claude-opus-4-7 等
    latency_ms      INTEGER,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    cache_read      INTEGER,
    cache_creation  INTEGER,
    image_path      TEXT,
    prompt_text     TEXT    NOT NULL,               -- system + user メッセージ
    response_text   TEXT,                           -- Claude の生テキスト
    parsed_json     TEXT,                           -- パース成功時の JSON
    error           TEXT                            -- 失敗時のエラー文
);

CREATE INDEX IF NOT EXISTS idx_api_logs_ts         ON api_logs(ts);
CREATE INDEX IF NOT EXISTS idx_api_logs_request_id ON api_logs(request_id);
```

---

## 4. `watering_history` — 実際に与えた水の履歴

AI 個体の自動給水と、対照個体の手動給水(動画比較用)の両方を記録する。

```sql
CREATE TABLE IF NOT EXISTS watering_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT    NOT NULL,
    individual   TEXT    NOT NULL,                  -- 'ai' or 'control'
    ml           INTEGER NOT NULL,
    source       TEXT    NOT NULL,                  -- 'claude_guarded' | 'rule_based' | 'manual'
    request_id   TEXT,                              -- decisions と連結する場合
    notes        TEXT
);

CREATE INDEX IF NOT EXISTS idx_watering_ts         ON watering_history(ts);
CREATE INDEX IF NOT EXISTS idx_watering_individual ON watering_history(individual, ts);
```

---

## 参照関係

```
decisions.request_id  ──┐
                        ├──> api_logs.request_id
watering_history.request_id ─┘
```

`request_id` は `raspi/` 側で UUID ベースに生成する(形式: `req-<ts>-<rand>`)。
外部キーは張らない(運用中のデータ移行を柔軟にしたい)。
