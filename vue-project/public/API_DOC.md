# AI问答流式接口（SSE）

## 接口说明

用于获取 AI 问答结果，采用 Server-Sent Events（SSE）方式返回数据。

服务端会按照以下顺序推送事件：

1. llm：流式返回大模型生成内容
2. source：返回参考来源信息
3. img：返回图片链接信息
4. done：返回结束事件

其中：

* llm 事件可能出现多次
* source 事件可能出现多次
* img 事件可能出现多次
* done 事件仅出现一次

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

| 事件名    | 说明      |
| ------ | ------- |
| llm    | 大模型生成内容 |
| source | 参考来源    |
| img    | 图片信息    |
| done   | 流式输出结束  |
| error  | 异常信息    |

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
data: 现藏于北京故宫博物院。
```

前端应将所有 llm 事件内容按顺序拼接。

最终效果：

```text
《清明上河图》现藏于北京故宫博物院。
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

## img事件

用于返回与回答相关的图片资源。

### Data结构

```json
{
  "url": "https://example.com/images/qingming.jpg"
}
```

### 示例

```text
event: img
data: {"url":"https://example.com/images/qingming.jpg"}
```

```text
event: img
data: {"url":"https://example.com/images/qingming2.jpg"}
```

一个回答可能对应多个 img 事件。

客户端收到后可直接展示图片或加入图片列表。

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
event: llm
data: 《清明

event: llm
data: 上河图》

event: llm
data: 现藏于北京故宫博物院。

event: source
data: {"name":"故宫博物院官网","url":"https://www.dpm.org.cn/"}

event: source
data: {"name":"中国国家博物馆","url":"https://www.chnmuseum.cn/"}

event: img
data: {"url":"https://example.com/images/qingming1.jpg"}

event: img
data: {"url":"https://example.com/images/qingming2.jpg"}

event: done
data: end
```

---

## 前端处理逻辑

### llm事件

将内容实时追加到回答区域。

### source事件

将来源信息追加到参考来源列表。

### img事件

将图片链接加入图片展示区域。

### done事件

结束流式接收并关闭连接。

---

## 错误处理

服务端发生异常时：

```text
event: error
data: 系统异常，请稍后重试
```

客户端收到 error 事件后应终止本次请求并提示用户。

---

## 事件顺序约定

正常情况下，服务端按照以下顺序推送：

```text
llm*
→ source*
→ img*
→ done
```

说明：

* llm* 表示 0~N 次 llm 事件
* source* 表示 0~N 次 source 事件
* img* 表示 0~N 次 img 事件
* done 表示结束事件

客户端应根据 event 类型进行处理，而不应依赖具体事件数量。
