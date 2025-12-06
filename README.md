# ROS 2 Humble / Jazzy Fast DDS 比較用コンポーズ

ROS 2 Humble と Jazzy で Fast DDS の挙動差を確認するための最小構成です。  
同一ホスト上で talker / listener をそれぞれのディストロで起動し、通信可否やレイテンシの違いを観察できます。

## 前提
- Docker / Docker Compose v2 が使える Linux 環境（`network_mode: host` を利用するため）。

## ビルド
```bash
docker compose build
```
サービスごとに `ROS_DISTRO` を切り替えて 2 種類のイメージ（humble/jazzy）が作られます。

## 典型的な試し方

### 1. Humble 同士
```bash
docker compose up humble_talker humble_listener
```

### 2. Jazzy 同士
```bash
docker compose up jazzy_talker jazzy_listener
```

### 3. 混在（Humble → Jazzy）
```bash
docker compose up humble_talker jazzy_listener
```

### 4. 混在（Jazzy → Humble）
```bash
docker compose up jazzy_talker humble_listener
```

## Fast DDS プロファイル調整
- `fastdds_profiles.xml` を編集することで、共有メモリを無効化したりプロパティを変更できます。
- 例: data-sharing を無効化したい場合は `fastdds.shm.disable` を有効化してください。

## カスタムテストノードを動かす場合
1. 追加で必要な依存を `Dockerfile` に追記する。
2. `command` を任意のノードに置き換える、あるいは `docker compose run humble_talker bash` で入って手動実行。

## 片付け
```bash
docker compose down
```

## 補足
- 共有メモリのデフォルト 64MB では足りないケースを避けるため、`shm_size: 512m` に設定しています。
- ホストネットワークを使うことで DDS のトラフィックを素直に流し、iptables/NAT 由来の差分を避けています。Docker Desktop (macOS/Windows) では `network_mode: host` が非対応なので、Linux での再現を推奨します。
