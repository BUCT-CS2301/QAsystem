

## POST QA

POST /qa/ask

### 请求参数

|名称|位置|类型|必填|说明|
|---|---|---|---|---|
|question|query|string| 是 |none|

> 返回示例

> 200 Response

```json
{
    "code": 200,
    "data": {
        "content": "《清明上河图》现藏于北京故宫博物院。",
        "sources": [
            {
                "name": "故宫博物院官网",
                "url": "https://www.dpm.org.cn/"
            },
            {
                "name": "故宫博物院官网",
                "url": "https://www.dpm.org.cn/"
            }
        ],
        "llmContent": "《清明上河图》是北宋画家张择端的代表作，描绘了北宋都城汴京的繁华景象。"
    }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|**code**|integer|true|状态码||none|
|**data**|object|true|数据对象||none|
|**content**|string|true|回答文本||none|
|**sources**|list<object>|true|来源列表||none|  
|**name**|string|true|来源名称||none|
|**url**|string|true|来源URL||none|
|**llmContent**|string|true|延申内容||none|



