# Exa Register

<p align="center"> <a href="README.md">简体中文</a> | English </p>

This is a script project for automatically registering [Exa](https://exa.ai/) accounts and obtaining API Keys.

The program uses the BitBrowser local API to create isolated browser environments, opens the Exa login and registration page, receives verification codes through temporary email addresses, completes the registration process, enters the dashboard to obtain the API Key, and appends the email address and API Key to `data.txt`.

## Highlights

Built on the latest version of the [DrissionPage](https://www.drissionpage.cn/) framework, taking advantage of its ability to seamlessly interact with `iframe` and `shadow` elements. This makes automated handling of Cloudflare-protected pages possible. The entire workflow runs automatically, requiring no manual intervention.

## Requirements

- Python 3.12+
- BitBrowser installed and running
- BitBrowser local API accessible at: `http://127.0.0.1:54345`
- A configured temporary email service; currently supports `mailnest`
- If you need to use proxies, configure and run `proxy.py` first

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

On the first run, if `cfg.yaml` does not exist in the project root directory, the program will automatically copy `cfg.example.yaml` to create it and then exit. Edit `cfg.yaml` before running the program again.

Example configuration:

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

Configuration fields:

- `email.provider_name`: Email service provider name. Currently set this to `mailnest`.
- `email.mailnest.project_code`: MailNest project code.
- `email.mailnest.api_key`: MailNest API Key. This field is required.
- `use_proxy`: Whether to configure a dynamic proxy for the BitBrowser browser environment.
- `proxy_backend_port`: Port used by the local proxy retrieval service provided by `proxy.py`.
- `timeout`: Timeout for a single waiting process, in seconds.
- `max_workers`: Number of concurrent registration tasks. Higher values open more browser windows simultaneously and require better machine performance, BitBrowser capacity, email service availability, and proxy quality.

## Proxy Configuration

If `use_proxy: false` is set in `cfg.yaml`, the program will not configure a proxy for BitBrowser, and you can run `python main.py` directly.

If `use_proxy: true`, you need to configure and start `proxy.py` first. The main program will set BitBrowser's dynamic proxy URL to:

```text
http://127.0.0.1:{proxy_backend_port}/get-proxy
```

This means that whenever BitBrowser needs a proxy, it requests the `/get-proxy` endpoint provided by the local `proxy.py` service. This endpoint must return a single proxy address as plain text, for example:

```text
127.0.0.1:7899
```

### Using a Local Proxy Application

If you use a local proxy application, simply configure `proxy.py` to return its local HTTP proxy address.

For example, if the local HTTP proxy port is `7899`:

```python
@app.route("/get-proxy", methods=["GET"])
def get_proxy():
    ip = '127.0.0.1:7899'
    return ip, 200, {
        "Content-Type": "text/plain"
    }
```

The actual port varies depending on the application, so adjust it according to your local proxy settings.

### Using a Purchased Proxy Service

If you use a dynamic proxy service, the proxy provider will usually provide a proxy extraction URL. Modify the example in `proxy.py` to request the provider's extraction URL and return the proxy IP received from the provider.

Example:

```python
@app.route("/get-proxy", methods=["GET"])
def get_proxy():
    ip = requests.get('http://proxy-extract-url').text.strip()
    return ip, 200, {
        "Content-Type": "text/plain"
    }
```

Replace `http://proxy-extract-url` with the actual extraction URL provided by your proxy service.

The returned content should use a proxy address format recognized by BitBrowser. A common format is:

```text
host:port
```

If the proxy provider returns JSON or multiple lines of data, parse the response in `proxy.py` and return only one usable proxy address.

Start the proxy backend:

```bash
python proxy.py
```

Keep `proxy.py` running, then open another terminal and start the main program.

Only `HTTP` proxies are supported by default. If you need to use a `SOCKS` proxy, modify `proxyType` in `register`.

## Running

Run the following command in the project root directory:

```bash
python main.py
```

The program will start multiple registration tasks according to `max_workers`.

Each task will create a BitBrowser browser profile, launch the browser, obtain a temporary email address, handle the Exa email verification code, retrieve the API Key, and append one line to `data.txt` after successful completion:

```text
email@example.com----api_key
```

## Stopping the Program

The program supports graceful shutdown with `Ctrl+C`.

After pressing `Ctrl+C`, the main thread will stop creating new registration tasks and wait for already submitted tasks to finish. When each task ends, the program will attempt to close and delete the corresponding BitBrowser browser profile to avoid leaving unclosed browser windows or unused browser profiles behind.

It is not recommended to force-close the terminal or terminate the Python process unless the program has become unresponsive. A forced shutdown may leave active browser windows or BitBrowser profiles that have not been cleaned up.