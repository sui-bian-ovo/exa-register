# Exa Register

<p align="center">   简体中文 | <a href="README_EN.md">English</a> </p>

这是一个用于自动化注册 [Exa](https://exa.ai/) 账号并获取 API Key 的脚本项目。

程序会通过 BitBrowser 本地 API 创建独立浏览器环境，打开 Exa 登录注册页，使用临时邮箱接收验证码，完成注册后进入控制台获取 API Key，并把邮箱和 API Key 追加写入 `data.txt`。

## 项目亮点

基于最新版 [drissionpage](https://www.drissionpage.cn/) 框架随意穿透`iframe `与`shadow`的新特性，使得自动化优雅过`cloudflare`成为现实，代码全部全自动运行，解放双手！

## 环境要求

- Python 3.12+
- 已安装并启动 BitBrowser
- BitBrowser 本地 API 地址可访问：`http://127.0.0.1:54345`
- 可用的临时邮箱服务配置，目前支持 `mailnest`
- 如需使用代理，需要先配置并运行 `proxy.py`

安装依赖：

```bash
pip install -r requirements.txt
```

## 配置文件

首次运行时，如果项目根目录不存在 `cfg.yaml`，程序会自动从 `cfg.example.yaml` 复制一份并退出。你需要编辑 `cfg.yaml` 后再运行。

配置示例：

```yaml
email:
  provider_name: mailnest

  # https://mailnest.top/
  mailnest:
    project_code: 'exa001'
    api_key: ''

use_proxy: false
proxy_backend_port: 5000
timeout: 60
max_workers: 3
```

字段说明：

- `email.provider_name`：邮箱服务提供方名称，目前填写 `mailnest`。
- `email.mailnest.project_code`：MailNest 项目编号。
- `email.mailnest.api_key`：MailNest API Key，必须填写。
- `use_proxy`：是否给 BitBrowser 浏览器环境配置动态代理。
- `proxy_backend_port`：本项目本地代理提取服务端口，对应 `proxy.py` 启动端口。
- `timeout`：单个等待流程的超时时间，单位为秒。
- `max_workers`：并发注册任务数量。数值越大，同时打开的浏览器窗口越多，对机器性能、BitBrowser、邮箱服务和代理质量要求越高。

## 代理配置

如果 `cfg.yaml` 中 `use_proxy: false`，程序不会给 BitBrowser 配置代理，可以直接运行 `python main.py`。

如果 `use_proxy: true`，需要先配置并启动 `proxy.py`。主程序会把 BitBrowser 的动态代理地址设置为：

```text
http://127.0.0.1:{proxy_backend_port}/get-proxy
```

也就是说，BitBrowser 每次需要代理时，会请求本地 `proxy.py` 提供的 `/get-proxy` 接口。这个接口必须返回一行纯文本代理地址，例如：

```text
127.0.0.1:7899
```

### 使用本地翻墙软件

如果你使用的是本机翻墙软件，直接在 `proxy.py` 里返回翻墙软件的本地 HTTP 代理地址即可。比如本地 HTTP 代理端口是 `7899`：

```python
@app.route("/get-proxy", methods=["GET"])
def get_proxy():
    ip = '127.0.0.1:7899'
    return ip, 200, {
        "Content-Type": "text/plain"
    }
```

不同软件的端口可能不一样，需要按你自己的软件设置修改。

### 使用购买的代理

如果你买的是动态代理，一般代理商会提供一个“提取代理”的 URL。需要把 `proxy.py` 里的示例改成请求代理商的提取 URL，然后返回代理商接口返回的代理 IP。

示例：

```python
@app.route("/get-proxy", methods=["GET"])
def get_proxy():
    ip = requests.get('http://proxy-extract-url').text.strip()
    return ip, 200, {
        "Content-Type": "text/plain"
    }
```

这里的 `http://proxy-extract-url` 要替换成你购买代理后拿到的真实提取 URL。返回内容应是 BitBrowser 能识别的代理地址格式，常见格式为：

```text
host:port
```

如果代理商返回的是 JSON 或多行数据，需要在 `proxy.py` 里解析后只返回一个可用的代理地址。

启动代理后端：

```bash
python proxy.py
```

保持 `proxy.py` 运行，再另开一个终端运行主程序。

默认只支持`http`代理，如果使用`socket`代理，需要在`register`中修改`proxyType`。

## 运行

在项目根目录执行：

```bash
python main.py
```

运行后，程序会按 `max_workers` 启动多个注册任务。每个任务会创建 BitBrowser 浏览器配置、打开浏览器、获取临时邮箱、处理 Exa 邮箱验证码、获取 API Key，并在成功后向 `data.txt` 追加一行：

```text
email@example.com----api_key
```

## 停止程序

程序支持通过 `Ctrl+C` 停止。

按下 `Ctrl+C` 后，主线程会停止创建新的注册任务，并等待当前已经提交的任务结束。每个任务结束时会尝试关闭并删除对应的 BitBrowser 浏览器配置，避免留下未清理的浏览器窗口。

不建议直接强制关闭终端或结束 Python 进程，除非程序已经无响应。强制退出可能导致当前浏览器窗口或 BitBrowser 配置没有被清理。
