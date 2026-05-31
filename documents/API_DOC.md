# AI问答流式接口（SSE）

## 接口说明

用于获取 AI 问答结果，采用 Server-Sent Events（SSE）方式返回数据。

服务端会按照事件类型逐步推送：

1. 返回检索得到的最终答案（content）
2. 返回参考来源（source）
3. 流式返回大模型生成内容（llm）
4. 返回结束事件（done）

---

## 请求信息

### 请求地址

```http
POST /api/chat
```

### 请求头

```http
Content-Type: application/json
Accept: text/event-stream
```

### 请求参数

```json
{
  "question": "清明上河图收藏在哪里？"
}
```

### 参数说明

| 参数名      | 类型     | 是否必填 | 说明     |
| -------- | ------ | ---- | ------ |
| question | String | 是    | 用户提问内容 |

---

## 响应格式

### Content-Type

```http
Content-Type: text/event-stream
```

### SSE事件类型

| 事件名     | 说明      |
| ------- | ------- |
| content | 检索答案    |
| source  | 参考来源    |
| llm     | 大模型生成内容 |
| done    | 流式输出结束  |

---

## content事件

用于返回知识库检索得到的最终答案。

### 示例

```text
event: content
data: 《清明上河图》现藏于北京故宫博物院。
```

---

## source事件

用于返回参考来源信息。

### Data结构

```json
{
  "name": "故宫博物院官网",
  "url": "https://www.dpm.org.cn/"
}
```

### 示例

```text
event: source
data: {"name":"故宫博物院官网","url":"https://www.dpm.org.cn/"}
```

一个回答可能对应多个 source 事件。

---

## llm事件

用于流式返回大模型生成内容。

### 示例

```text
event: llm
data: 《清明
```

```text
event: llm
data: 上河图》
```

```text
event: llm
data: 是北宋画家张择端的代表作
```

前端应将所有 llm 事件内容按顺序拼接。

最终效果：

```text
《清明上河图》是北宋画家张择端的代表作
```

---

## done事件

表示本次回答结束。

### 示例

```text
event: done
data: end
```

收到该事件后，客户端应关闭连接并结束本次会话处理。

---

## 完整响应示例

```text
event: content
data: 《清明上河图》现藏于北京故宫博物院。

event: source
data: {"name":"故宫博物院官网","url":"https://www.dpm.org.cn/"}

event: source
data: {"name":"故宫博物院官网","url":"https://www.dpm.org.cn/"}

event: llm
data: 《清明

event: llm
data: 上河图》

event: llm
data: 是北宋画家张择端的代表作

event: done
data: end
```

---

## 前端处理逻辑

### content事件

更新检索答案区域。

### source事件

追加参考来源列表。

### llm事件

追加大模型实时生成内容。

### done事件

结束流式接收，关闭连接。

---

## 错误处理

当服务端出现异常时：

```text
event: error
data: 系统异常，请稍后重试
```

客户端收到 error 事件后应终止本次请求并提示用户。
