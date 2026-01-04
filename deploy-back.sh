#!/bin/bash

# ===== 後端部署腳本 =====
# 適用於 Windows (Git Bash / WSL) 和 Linux
# dev (5000) 和 prod (5001) 可同時運行，互不影響

# 映像檔名稱
IMAGE_NAME="shaoairai/yulakeback:latest"

echo "===== 開始建置後端正式版映像檔 ====="

# 建置映像檔（讀取 dev 的最新程式碼並打包）
docker build -f dockerfile/Dockerfile.back.prod -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "===== 建置失敗 ====="
    exit 1
fi

echo "===== 建置成功 ====="

# 詢問是否推送到 Docker Hub
read -p "是否推送到 Docker Hub？(y/n): " push_choice
if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
    echo "===== 推送映像檔到 Docker Hub ====="
    docker push $IMAGE_NAME

    # 檢查推送是否失敗（可能是認證問題）
    if [ $? -ne 0 ]; then
        echo ""
        echo "===== 推送失敗，可能需要登入 ====="
        echo "請執行: docker login"
        read -p "登入完成後按 Enter 重試推送，或輸入 n 跳過: " retry_choice
        if [ "$retry_choice" != "n" ] && [ "$retry_choice" != "N" ]; then
            docker push $IMAGE_NAME
            if [ $? -ne 0 ]; then
                echo "===== 推送仍然失敗，請檢查認證 ====="
            else
                echo "===== 推送成功 ====="
            fi
        fi
    else
        echo "===== 推送成功 ====="
    fi
fi

# 詢問是否啟動正式版容器
read -p "是否啟動正式版容器（含資料庫）？(y/n): " run_choice
if [ "$run_choice" = "y" ] || [ "$run_choice" = "Y" ]; then
    echo "===== 啟動正式版容器 ====="
    docker-compose -f docker-compose.back.prod.yml up -d
    echo "===== 正式版已啟動 ====="
    echo "===== 後端 API：http://localhost:5001 ====="
    echo "===== 資料庫：localhost:5433 ====="
    echo "===== dev (5000/5432) 和 prod (5001/5433) 可同時運行 ====="
fi
