#!/bin/bash
set -e

echo "🚀 Yulake Backend Starting..."

# 等待資料庫準備好
echo "⏳ Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Database not ready, waiting 2 seconds... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Failed to connect to database after $MAX_RETRIES attempts"
    exit 1
fi

# ============================================================
# 資料庫初始化安全檢查
# ⚠️ 重要：此邏輯確保不會誤刪現有資料
# ============================================================
echo "🔍 Checking database status..."

# 檢查資料表數量
TABLES_COUNT=$(python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()
cur.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'\")
print(cur.fetchone()[0])
conn.close()
")

# 檢查是否有實際業務資料（額外安全檢查）
HAS_DATA=$(python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()
try:
    # 檢查 salons 表是否有資料
    cur.execute(\"SELECT COUNT(*) FROM salons\")
    salon_count = cur.fetchone()[0]
    # 檢查 customers 表是否有資料
    cur.execute(\"SELECT COUNT(*) FROM customers\")
    customer_count = cur.fetchone()[0]
    # 檢查 bookings 表是否有資料
    cur.execute(\"SELECT COUNT(*) FROM bookings\")
    booking_count = cur.fetchone()[0]
    has_data = salon_count > 0 or customer_count > 0 or booking_count > 0
    print('yes' if has_data else 'no')
except:
    # 如果表不存在，代表是空資料庫
    print('no')
conn.close()
" 2>/dev/null || echo "no")

echo "   Tables: $TABLES_COUNT, Has business data: $HAS_DATA"

# 只有在「沒有資料表」且「沒有業務資料」時才初始化
if [ "$TABLES_COUNT" -eq "0" ]; then
    echo "📦 Empty database detected (no tables), initializing..."

    # 建立資料表（透過 Flask app context）
    python -c "
from app import create_app
app = create_app()
print('   Tables created successfully!')
"

    # 執行種子資料（seed.py 也有自己的安全檢查）
    echo "🌱 Seeding initial data..."
    python seed.py

    echo "✅ Database initialization complete!"

elif [ "$HAS_DATA" = "no" ] && [ "$TABLES_COUNT" -gt "0" ]; then
    # 有表但沒資料 - 可能是之前建表但沒 seed
    echo "📦 Tables exist but no data, seeding..."
    python seed.py
    echo "✅ Seed data complete!"

else
    # 有資料 - 絕對不能動
    echo "✅ Database already initialized ($TABLES_COUNT tables, has business data)"
    echo "   Skipping initialization to protect existing data."
fi

# 啟動應用程式
echo "🎉 Starting Flask development server..."
exec "$@"
