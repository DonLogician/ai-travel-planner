# 接口文档

## 基本信息
```
开发环境基地址：http://localhost:8000/api
正式环境基地址：<部署后填入>
```

### 认证说明
- 当前为课程作业，默认使用模拟用户。后续上线应启用 JWT，并在请求头添加：
```
Authorization: Bearer <token>
Content-Type: application/json
```

## 系统健康检查
### GET /health
用于监控服务状态。

**响应示例**
```json
{
  "status": "healthy",
  "app": "AI Travel Planner",
  "version": "1.0.0"
}
```

---

## 行程相关接口（/itineraries）

### 1. 创建行程 - POST /itineraries/
根据用户输入调用 LLM 生成行程，并写入数据库。

**请求体参数**
| 字段             | 类型          | 必填 | 说明                                  |
| ---------------- | ------------- | ---- | ------------------------------------- |
| destination      | string        | ✅    | 目的地（城市/地区名称）               |
| start_date       | date          | ✅    | 开始日期，格式 YYYY-MM-DD             |
| end_date         | date          | ✅    | 结束日期                              |
| budget           | number        | ✅    | 旅行总预算（货币单位自定）            |
| preferences      | array[string] | ❌    | 旅行偏好标签，如 `"food"`、`"family"` |
| additional_notes | string        | ❌    | 其他补充需求                          |

**返回示例（201）**
```json
{
  "id": "uuid",
  "destination": "东京",
  "start_date": "2025-02-01",
  "end_date": "2025-02-05",
  "budget": 10000,
  "daily_itinerary": [
    {
      "day": 1,
      "date": "2025-02-01",
      "activities": [
        {
          "time": "09:00",
          "activity": "浅草寺参观",
          "location": "浅草寺",
          "estimated_cost": 0,
          "notes": "建议提前到场避开人流"
        }
      ],
      "total_estimated_cost": 800
    }
  ],
  "total_estimated_cost": 4200,
  "recommendations": "建议提前预约热门餐厅，地铁交通最省时",
  "created_at": "2025-01-10T12:00:00"
}
```

### 2. 行程列表 - GET /itineraries/
获取当前用户全部行程。

**查询参数**
| 参数  | 类型    | 说明                  |
| ----- | ------- | --------------------- |
| limit | integer | 返回数量上限，默认 20 |

**返回示例（200）**
```json
[
  {
    "id": "uuid",
    "destination": "东京",
    "start_date": "2025-02-01",
    "end_date": "2025-02-05",
    "budget": 10000,
    "daily_itinerary": [...],
    "total_estimated_cost": 4200,
    "created_at": "2025-01-10T12:00:00"
  }
]
```

### 3. 行程详情 - GET /itineraries/{id}
根据行程 ID 获取详情。

**路径参数**
| 参数 | 类型   | 说明      |
| ---- | ------ | --------- |
| id   | string | 行程 UUID |

**错误响应（404）**
```json
{
  "detail": "Itinerary not found"
}
```

### 4. 删除行程 - DELETE /itineraries/{id}
删除指定行程。

**成功响应**：204 No Content

### 5. 预算对比 - GET /itineraries/{id}/budget-status
返回计划预算、AI 估算和实际支出对比。

**返回示例（200）**
```json
{
  "itinerary_id": "uuid",
  "planned_budget": 10000,
  "estimated_cost": 4200,
  "actual_spent": 1800,
  "remaining": 8200,
  "spent_percentage": 18,
  "expense_breakdown": {
    "food": 600,
    "transportation": 400,
    "accommodation": 800
  }
}
```

---

## 费用相关接口（/expenses）

### 1. 新增费用 - POST /expenses/

**请求体参数**
| 字段         | 类型     | 必填 | 说明                                                                          |
| ------------ | -------- | ---- | ----------------------------------------------------------------------------- |
| itinerary_id | string   | ❌    | 对应行程 ID，可为空（独立记账）                                               |
| category     | string   | ✅    | 分类：`accommodation`/`food`/`transportation`/`activities`/`shopping`/`other` |
| amount       | number   | ✅    | 金额                                                                          |
| description  | string   | ✅    | 描述                                                                          |
| date         | datetime | ❌    | 发生时间，默认当前时间                                                        |
| location     | string   | ❌    | 地点                                                                          |

**返回示例（201）**
```json
{
  "id": "uuid",
  "user_id": "user-1",
  "itinerary_id": "uuid",
  "category": "food",
  "amount": 120.5,
  "description": "晚餐-筑地寿司",
  "date": "2025-02-01T19:30:00",
  "location": "东京",
  "created_at": "2025-02-01T20:00:00",
  "updated_at": "2025-02-01T20:00:00"
}
```

### 2. 费用列表 - GET /expenses/

**查询参数**
| 参数         | 类型    | 说明                   |
| ------------ | ------- | ---------------------- |
| itinerary_id | string  | 按行程筛选             |
| category     | string  | 按分类筛选             |
| limit        | integer | 返回数量上限，默认 100 |

### 3. 费用汇总 - GET /expenses/summary
返回总额与按分类聚合结果。

```json
{
  "total_expenses": 1500,
  "by_category": {
    "food": 500,
    "transportation": 300,
    "accommodation": 600,
    "activities": 100
  },
  "count": 15
}
```

### 4. 查看/更新/删除单条费用
- GET /expenses/{id}
- PUT /expenses/{id}
  ```json
  {
    "category": "shopping",
    "amount": 150,
    "description": "纪念品"
  }
  ```
- DELETE /expenses/{id}

成功删除返回 204。

---

## 导航接口（/navigation）

### 1. 地点搜索 - POST /navigation/search
调用高德 POI 搜索。

```json
{
  "query": "浅草寺",
  "city": "东京"
}
```

**响应示例**
```json
[
  {
    "name": "浅草寺",
    "address": "日本东京都台东区浅草2-3-1",
    "longitude": 139.796655,
    "latitude": 35.714765
  }
]
```

### 2. 路线规划 - POST /navigation/route

```json
{
  "origin": "东京站",
  "destination": "浅草寺",
  "mode": "transit"
}
```

**响应示例**
```json
{
  "distance": 5.2,
  "duration": 28,
  "steps": [
    "从东京站乘坐丸之内线到银座站",
    "步行换乘银座线到浅草站",
    "步行 400 米抵达浅草寺"
  ]
}
```

---

## 语音接口（/voice）

### 语音识别 - POST /voice/recognize
调用科大讯飞语音转写。

**请求体**
```json
{
  "audio_data": "<base64 编码音频>",
  "language": "zh_cn"
}
```
- `audio_data`：必填，建议 16k PCM 或 WAV 转 Base64。
- `language`：可选，默认 `zh_cn`。

**响应示例（200）**
```json
{
  "text": "我想去东京玩五天，预算一万块",
  "confidence": 0.92
}
```

---

## 错误码约定
| 状态码 | 含义              | 返回示例                                     |
| ------ | ----------------- | -------------------------------------------- |
| 400    | 参数错误          | `{ "detail": "Invalid request parameters" }` |
| 401    | 未认证/Token 失效 | `{ "detail": "Not authenticated" }`          |
| 404    | 资源不存在        | `{ "detail": "Resource not found" }`         |
| 500    | 服务器异常        | `{ "detail": "Internal server error: ..." }` |

---

## 限流建议（生产环境）
- 行程生成：10 次/分钟/用户
- 导航请求：50 次/分钟/用户
- 费用操作：100 次/分钟/用户

## 在线文档
 - Swagger UI：`http://localhost:8000/api/docs`
 - ReDoc：`http://localhost:8000/api/redoc`
