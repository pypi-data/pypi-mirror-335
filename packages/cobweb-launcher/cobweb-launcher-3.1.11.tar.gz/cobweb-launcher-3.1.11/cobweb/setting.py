import os

# redis db config
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "password": os.getenv("REDIS_PASSWORD"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
}

# loghub db config
LOGHUB_TOPIC = os.getenv("LOGHUB_TOPIC")
LOGHUB_SOURCE = os.getenv("LOGHUB_SOURCE")
LOGHUB_PROJECT = os.getenv("LOGHUB_PROJECT")
LOGHUB_CONFIG = {
    "endpoint": os.getenv("LOGHUB_ENDPOINT"),
    "accessKeyId": os.getenv("LOGHUB_ACCESS_KEY"),
    "accessKey": os.getenv("LOGHUB_SECRET_KEY")
}

# # oss util config
OSS_BUCKET = os.getenv("OSS_BUCKET")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")
OSS_ACCESS_KEY = os.getenv("OSS_ACCESS_KEY")
OSS_SECRET_KEY = os.getenv("OSS_SECRET_KEY")
OSS_CHUNK_SIZE = 10 * 1024 ** 2
OSS_MIN_UPLOAD_SIZE = 1024


# 采集器选择
CRAWLER = "cobweb.crawlers.Crawler"

# 数据管道
PIPELINE = "cobweb.pipelines.Console"

# 调度器
SCHEDULER = "cobweb.schedulers.RedisScheduler"


# Launcher 等待时间

BEFORE_SCHEDULER_WAIT_SECONDS = 60  # 调度前等待时间,只作用于单次任务
SCHEDULER_WAIT_SECONDS = 15  # 调度等待时间
TODO_QUEUE_FULL_WAIT_SECONDS = 5  # todo队列已满时等待时间
NEW_QUEUE_WAIT_SECONDS = 30   # new队列等待时间
DONE_QUEUE_WAIT_SECONDS = 5   # done队列等待时间
UPLOAD_QUEUE_WAIT_SECONDS = 15   # upload队列等待时间
SEED_RESET_SECONDS = 60   # 种子重制时间


# Launcher 队列长度
TODO_QUEUE_SIZE = 100  # todo队列长度
NEW_QUEUE_MAX_SIZE = 100  # new队列长度
DONE_QUEUE_MAX_SIZE = 100  # done队列长度
UPLOAD_QUEUE_MAX_SIZE = 100  # upload队列长度

# DONE_MODEL IN (0, 1), 种子完成模式
DONE_MODEL = 0   # 0:种子消费成功直接从队列移除，失败则添加至失败队列；1:种子消费成功添加至成功队列，失败添加至失败队列

# spider
SPIDER_THREAD_NUM = 10
SPIDER_MAX_RETRIES = 5
SPIDER_TIME_SLEEP = 10
RECORD_FAILED_SPIDER = False

SPIDER_MAX_COUNT = 1000   # 在规定时间窗口内最大采集数
TIME_WINDOW = 60   # 频控固定时间窗口（秒）

# 任务模式
TASK_MODEL = 0  # 0:单次，1:常驻

# 流控措施
SPEED_CONTROL = 1  # 0:关闭，1:开启

# # bloom过滤器
# CAPACITY = 100000000
# ERROR_RATE = 0.001
# FILTER_FIELD = "url"
# 文件下载响应类型过滤
# FILE_FILTER_CONTENT_TYPE = ["text/html", "application/xhtml+xml"]
