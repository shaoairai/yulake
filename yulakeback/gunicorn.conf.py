# Gunicorn 設定檔

# 綁定位址和埠
bind = '0.0.0.0:5000'

# Worker 數量（建議 CPU 核心數 * 2 + 1）
workers = 4

# Worker 類型
worker_class = 'sync'

# 超時時間（秒）
timeout = 120

# 日誌
accesslog = '-'
errorlog = '-'
loglevel = 'info'
