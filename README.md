# ruankao-results-query
计算机技术与软件专业技术资格考试成绩查询脚本

## 依赖

- python3
- pip3

- requests
- BeautifulSoup
- ddddocr

## 用法

依赖：

参数配置：
``` python
STAGE = '2022年上半年'
CANDIDATE_NAME = '张三'  # 准考证姓名
CANDIDATE_NO = '20228888888888888'  # 准考证号
PUSH_KEY = 'xxx'  # 推送消息的key
```

运行：
```
nohup ./ruankao.py > /dev/null 2>&1 &
```

## 消息推送

pushdeer
``` sh
# 详看官网，需要修改 PUSH_KEY
```

loki
``` sh
docker-compose up -d
# 浏览器访问：localhost:3000
```

