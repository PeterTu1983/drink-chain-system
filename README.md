# 連鎖飲料店分散式菜單與經營管理系統

本專案以 Docker 與 PostgreSQL 建立分散式架構，支援桃園 3 間分店與台北、台中、台南各 1 間分店（共 6 間分店），提供一致的網頁操作介面、固定 5 款連鎖飲品、各分店獨立新增特色飲品，以及分店店長經營資訊與老闆全分店營收彙整。

## 系統特色與架構
- **固定連鎖菜單**：開心奶茶（70 元）、快樂紅茶（55 元）、烏龍綠茶（60 元）、茉莉花茶（70 元）、甘蔗青茶（65 元）。
- **分散式分店節點**：桃園一店（ty-1）、桃園二店（ty-2）、桃園三店（ty-3）、台北一店（tpe-1）、台中一店（txg-1）、台南一店（tnn-1）各自搭配獨立資料庫與 Volume 持久化儲存。
- **特色飲品差異化**：各分店可各自新增本店特色飲品，不影響其他分店。
- **經營與營收檢視**：分店店長可查看本店訂單數、總營收與近期訂單；老闆可查看全連鎖各分店營收與特色飲品數量彙整。

## 環境需求
- Ubuntu Linux（建議 22.04 LTS / 24.04 LTS）
- Git、Docker Engine 與 Docker Compose Plugin

## 部署步驟

### 1. 安裝基礎工具與 Docker
若尚未安裝，請在 Ubuntu 終端機執行：

sudo apt-get update
sudo apt-get install -y ca-certificates curl openssh-server git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

### 2. 下載專案並啟動服務
git clone <你的_GITHUB_專案網址>
cd drink-chain-system
docker compose up -d --build

### 3. 驗證系統運作
docker compose ps

確認 6 個資料庫容器與 drink_chain_web 狀態皆為 Up 後，開啟瀏覽器前往：
http://localhost:8000（或 http://<Ubuntu虛擬機IP>:8000）

## 停止與清理服務
停止容器並保留資料：
docker compose down

停止容器並清除資料卷：
docker compose down -v
