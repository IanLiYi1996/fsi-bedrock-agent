# 基金投资顾问Agent（Callback处理器版本）

这个项目实现了一个基金投资顾问Agent，使用Strands Agents SDK的callback-handlers功能处理工具调用、工具结果、子agent被调用等信息。

## 项目结构

- `agents/`: 包含各种专家Agent的实现
- `tools/`: 包含工具函数的实现
- `utils/`: 包含工具类和辅助函数
  - `callback_handlers.py`: 实现了各种回调处理器
- `main.py`: 命令行入口
- `app.py`: FastAPI入口
- `static/`: 静态文件目录
- `knowledge/`: 知识库目录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行方式

### 命令行方式

```bash
# 单次查询模式
python main.py --query "我想了解股票型基金"

# 交互模式
python main.py --interactive

# 详细输出模式
python main.py --interactive --verbose
```

### API服务方式

```bash
# 启动API服务器
python app.py
```

## API文档

启动API服务器后，可以访问以下URL查看API文档：

```
http://localhost:8000/docs
```

## 在APIDogs中测试API

1. 首先启动API服务器：

```bash
python app.py
```

2. 打开APIDogs（或其他API测试工具，如Postman）

3. 测试非流式响应：

   - 请求方法：POST
   - 请求URL：http://localhost:8000/query
   - 请求头：Content-Type: application/json
   - 请求体：
     ```json
     {
       "query": "我想了解股票型基金",
       "stream": false,
       "include_events": false
     }
     ```

4. 测试流式响应：

   - 请求方法：POST
   - 请求URL：http://localhost:8000/query
   - 请求头：Content-Type: application/json
   - 请求体：
     ```json
     {
       "query": "我想了解股票型基金",
       "stream": true,
       "include_events": false
     }
     ```
   - 注意：流式响应需要APIDogs支持Server-Sent Events (SSE)，如果不支持，可能无法正确显示流式响应

5. 测试包含事件信息的流式响应：

   - 请求方法：POST
   - 请求URL：http://localhost:8000/query
   - 请求头：Content-Type: application/json
   - 请求体：
     ```json
     {
       "query": "我想了解股票型基金",
       "stream": true,
       "include_events": true
     }
     ```
   - 这将返回包含事件信息的流式响应，可以看到工具调用、子agent调用等事件

## WebSocket测试

可以使用以下HTML文件测试WebSocket连接：

```html
<!DOCTYPE html>
<html>
<head>
    <title>基金投资顾问WebSocket测试</title>
    <style>
        #output {
            width: 100%;
            height: 400px;
            border: 1px solid #ccc;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>基金投资顾问WebSocket测试</h1>
    <div id="output"></div>
    <input type="text" id="message" placeholder="输入您的问题" style="width: 80%;">
    <button onclick="sendMessage()">发送</button>
    <label><input type="checkbox" id="include_events"> 包含事件信息</label>

    <script>
        let socket = new WebSocket("ws://localhost:8000/ws");
        let output = document.getElementById("output");

        socket.onopen = function(e) {
            appendMessage("连接已建立");
        };

        socket.onmessage = function(event) {
            appendMessage(event.data);
        };

        socket.onclose = function(event) {
            if (event.wasClean) {
                appendMessage(`连接已关闭，代码=${event.code} 原因=${event.reason}`);
            } else {
                appendMessage('连接已断开');
            }
        };

        socket.onerror = function(error) {
            appendMessage(`错误: ${error.message}`);
        };

        function sendMessage() {
            let messageInput = document.getElementById("message");
            let includeEvents = document.getElementById("include_events").checked;
            let message = {
                query: messageInput.value,
                include_events: includeEvents
            };
            socket.send(JSON.stringify(message));
            appendMessage(`发送: ${messageInput.value}`);
            messageInput.value = "";
        }

        function appendMessage(message) {
            output.innerHTML += message + "<br>";
            output.scrollTop = output.scrollHeight;
        }
    </script>
</body>
</html>
```

将此文件保存为`websocket_test.html`，然后在浏览器中打开即可测试WebSocket连接。

## 回调处理器

项目实现了多种回调处理器，用于处理agent执行过程中的各种事件：

- `BaseCallbackHandler`：基础回调处理器类，定义了处理各种事件的接口
- `ConsoleCallbackHandler`：控制台输出回调处理器，将事件信息打印到控制台
- `StreamingCallbackHandler`：流式响应回调处理器，用于FastAPI的StreamingResponse
- `LoggingCallbackHandler`：日志记录回调处理器，将事件信息记录到日志
- `CompositeCallbackHandler`：组合回调处理器，可以同时使用多个回调处理器
- `create_custom_callback_handler`：创建自定义回调处理器函数

回调处理器可以处理以下类型的事件：
- 文本生成事件
- 工具使用事件（开始和结束）
- 子Agent事件（开始和结束）
- 子Agent工具使用事件（开始和结束）
