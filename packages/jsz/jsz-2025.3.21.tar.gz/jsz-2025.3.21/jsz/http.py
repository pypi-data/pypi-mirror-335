import httpx
import asyncio
from rich import print
from .tools import logger

__all__ = [
    "async_fetch",
    "curl_cffi",
    "download",
    "fetch",
    "httpx",
    "requests",
]


async def _async_fetch(
    url: str,
    method: str = "GET",
    *,
    params: dict[str] | None = None,
    content=None,
    data=None,
    json=None,
    headers=None,
    cookies=None,
    files=None,
    auth=None,
    proxy=None,
    proxies=None,
    mounts=None,
    timeout=None,
    follow_redirects: bool = True,
    verify: bool = True,
    cert=None,
    trust_env: bool = True,
    http1=True,
    http2=False,
    default_encoding="utf-8",
):
    """
    ## 发送异步请求（基于 httpx.AsyncClient）

    - url: 请求地址
    - method: 请求方法, 默认为 GET, 支持 GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT
    - params: 查询参数
    - content: 请求内容
    - data: 请求内容
    - json: 请求内容
    - headers: 请求头
    - cookies: 请求 Cookie
    - files: 文件
    - auth: 认证
    - proxy: 代理
    - proxies: 代理
    - mounts: 挂载
    - timeout: 超时
    - follow_redirects: 是否跟随重定向
    - verify: 是否验证 SSL 证书
    - cert: 证书
    - trust_env: 是否信任环境变量
    - http1: 是否使用 HTTP/1.1
    - http2: 是否使用 HTTP/2
    - default_encoding: 默认编码
    """
    if not proxy and proxies:
        if isinstance(proxies, dict):
            proxy = (
                proxies.get("http")
                or proxies.get("https")
                or proxies.get("all")
                or proxies.get("http://")
                or proxies.get("https://")
            )
        elif isinstance(proxies, str):
            proxy = proxies
    async with httpx.AsyncClient(
        verify=verify,
        cert=cert,
        http1=http1,
        http2=http2,
        proxy=proxy,
        mounts=mounts,
        trust_env=trust_env,
        default_encoding=default_encoding,
    ) as client:
        return await client.request(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
        )


async def async_fetch(
    url: str,
    method: str = "GET",
    *,
    params: dict[str] | None = None,
    content=None,
    data=None,
    json=None,
    headers=None,
    cookies=None,
    files=None,
    auth=None,
    proxy=None,
    proxies=None,
    mounts=None,
    timeout=None,
    follow_redirects: bool = True,
    verify: bool = True,
    cert=None,
    trust_env: bool = True,
    http1=True,
    http2=False,
    default_encoding="utf-8",
    retry: int = 1,
):
    """
    ## 发送异步请求（基于 httpx.AsyncClient）

    - url: 请求地址
    - method: 请求方法, 默认为 GET, 支持 GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT
    - params: 查询参数
    - content: 请求内容
    - data: 请求内容
    - json: 请求内容
    - headers: 请求头
    - cookies: 请求 Cookie
    - files: 文件
    - auth: 认证
    - proxy: 代理
    - proxies: 代理
    - mounts: 挂载
    - timeout: 超时
    - follow_redirects: 是否跟随重定向
    - verify: 是否验证 SSL 证书
    - cert: 证书
    - trust_env: 是否信任环境变量
    - http1: 是否使用 HTTP/1.1
    - http2: 是否使用 HTTP/2
    - default_encoding: 默认编码
    - retry: 重试次数
    """
    for _ in range(retry):
        try:
            response = await _async_fetch(
                url=url,
                method=method,
                params=params,
                content=content,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                files=files,
                auth=auth,
                proxy=proxy,
                proxies=proxies,
                mounts=mounts,
                timeout=timeout,
                follow_redirects=follow_redirects,
                verify=verify,
                cert=cert,
                trust_env=trust_env,
                http1=http1,
                http2=http2,
                default_encoding=default_encoding,
            )
            return response
        except Exception as e:
            logger.error(f"{url} 请求失败: {e!r}")


def fetch(
    url: str,
    method: str = "GET",
    *,
    params: dict[str] | None = None,
    content=None,
    data=None,
    json=None,
    headers=None,
    cookies=None,
    files=None,
    auth=None,
    proxy=None,
    proxies=None,
    mounts=None,
    timeout=None,
    follow_redirects: bool = True,
    verify: bool = True,
    cert=None,
    trust_env: bool = True,
    http1=True,
    http2=False,
    default_encoding="utf-8",
    retry: int = 1,
):
    """
    - 发送同步请求（基于 httpx.AsyncClient）

    - url: 请求地址
    - method: 请求方法, 默认为 GET, 支持 GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT
    - params: 查询参数
    - content: 请求内容
    - data: 请求内容
    - json: 请求内容
    - headers: 请求头
    - cookies: 请求 Cookie
    - files: 文件
    - auth: 认证
    - proxy: 代理
    - proxies: 代理
    - mounts: 挂载
    - timeout: 超时
    - follow_redirects: 是否跟随重定向
    - verify: 是否验证 SSL 证书
    - cert: 证书
    - trust_env: 是否信任环境变量
    - http1: 是否使用 HTTP/1.1
    - http2: 是否使用 HTTP/2
    - default_encoding: 默认编码
    - retry: 重试次数
    """
    response = asyncio.run(
        async_fetch(
            url,
            method,
            params=params,
            content=content,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            proxy=proxy,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            http1=http1,
            http2=http2,
            default_encoding=default_encoding,
            retry=retry,
        )
    )
    return response


def curl_cffi(
    url: str,
    method: str = "GET",
    *,
    params: dict | list | tuple | None = None,
    data: dict[str, str] | list[tuple] | str | bytes | None = None,
    json: dict | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    files: dict | None = None,
    auth: None = None,
    timeout: float = 30,
    allow_redirects: bool = True,
    max_redirects: int = 30,
    proxies: None = None,
    proxy: str | None = None,
    proxy_auth: None = None,
    verify: bool | None = None,
    referer: str | None = None,
    accept_encoding: str | None = "gzip, deflate, br, zstd",
    content_callback: None = None,
    impersonate: str | None = "chrome",
    ja3: str | None = None,
    akamai: str | None = None,
    extra_fp: None = None,
    thread: None = None,
    default_headers: bool | None = None,
    default_encoding: str = "utf-8",
    curl_options: dict | None = None,
    http_version: None = None,
    debug: bool = False,
    interface: str | None = None,
    cert: str | tuple[str, str] | None = None,
    stream: bool = False,
    max_recv_speed: int = 0,
    multipart: None = None,
    retry: int = 1,
):
    """
    基于 curl_cffi 封装, 可以过 ja3 和 cloudflare 等验证

    - url: 请求地址
    - method: 请求方法, 默认为 GET, 支持 GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT
    - params: 查询参数
    - data: 请求内容
    - json: 请求内容
    - headers: 请求头
    - cookies: 请求 Cookie
    - files: 文件
    - auth: 认证
    - timeout: 超时
    - allow_redirects: 是否跟随重定向
    - max_redirects: 最大重定向次数
    - proxies: 代理
    - proxy: 代理
    - proxy_auth: 代理认证
    - verify: 是否验证 SSL 证书
    - referer: 来源
    - accept_encoding: 接受编码
    - content_callback: 内容回调
    - impersonate: 模拟浏览器
    - ja3: JA3 指纹
    - akamai: Akamai 指纹
    - extra_fp: 额外的指纹
    - thread: 线程
    - default_headers: 默认头
    - default_encoding: 默认编码
    - curl_options: curl 选项
    - http_version: http 版本, 默认为 HTTP/2
    - debug: 是否调试
    - interface: 接口
    - cert: 证书
    - stream: 是否流式
    - max_recv_speed: 最大接收速度
    - multipart: 多部分
    - retry: 重试次数
    """
    try:
        from curl_cffi import requests
    except Exception:
        print("[red]请先安装 curl_cffi, 否则无法使用[/]\n\npip install curl_cffi")
        return

    if proxies:
        if isinstance(proxies, str):
            proxies = {"all": proxies}
        elif isinstance(proxies, dict):
            proxies = {
                "all": (
                    proxies.get("http")
                    or proxies.get("https")
                    or proxies.get("all")
                    or proxies.get("http://")
                    or proxies.get("https://")
                )
            }

    except_list = []
    for _ in range(retry):
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                files=files,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                max_redirects=max_redirects,
                proxies=proxies,
                proxy=proxy,
                proxy_auth=proxy_auth,
                verify=verify,
                referer=referer,
                accept_encoding=accept_encoding,
                content_callback=content_callback,
                impersonate=impersonate,
                ja3=ja3,
                akamai=akamai,
                extra_fp=extra_fp,
                thread=thread,
                default_headers=default_headers,
                default_encoding=default_encoding,
                curl_options=curl_options,
                http_version=http_version,
                debug=debug,
                interface=interface,
                cert=cert,
                stream=stream,
                max_recv_speed=max_recv_speed,
                multipart=multipart,
            )
            return response
        except Exception as e:
            except_list.append(e)
            logger.error(f"{url} 请求失败: {e!r}")
    raise except_list[-1]


def requests(
    url: str,
    method: str = "GET",
    *,
    params: dict | None = None,
    data: dict | str | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    files: dict | None = None,
    auth: None = None,
    timeout: int | float | None = None,
    allow_redirects: bool | None = True,
    proxies: dict | None = None,
    hooks: None = None,
    stream: bool | None = False,
    verify: bool | str | None = True,
    cert: None = None,
    json: dict | None = None,
    retry: int = 1,
):
    """
    发送同步请求(基于 requests)

    - method: 请求方法, 默认为 GET, 支持 GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT
    - url: 请求地址
    - params: 查询参数
    - data: 请求内容
    - headers: 请求头
    - cookies: 请求 Cookie
    - files: 文件
    - auth: 认证
    - timeout: 超时
    - allow_redirects: 是否跟随重定向
    - proxies: 代理
    - hooks: 钩子
    - stream: 是否流式
    - verify: 是否验证 SSL 证书
    - cert: 证书
    - json: 请求内容
    - retry: 重试次数
    """
    import requests

    if proxies:
        if isinstance(proxies, dict):
            proxies = {
                "all": (
                    proxies.get("http")
                    or proxies.get("https")
                    or proxies.get("all")
                    or proxies.get("http://")
                    or proxies.get("https://")
                )
            }
        elif isinstance(proxies, str):
            proxies = {"all": proxies}

    except_list = []
    for _ in range(retry):
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                files=files,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                proxies=proxies,
                hooks=hooks,
                stream=stream,
                verify=verify,
                cert=cert,
                json=json,
            )
            return response
        except Exception as e:
            except_list.append(e)
            logger.error(f"{url} 请求失败: {e!r}")
    raise except_list[-1]


def download(
    url: str,
    file_name: str,
    *,
    retry: int = 1,
    proxies: dict | None = None,
):
    """
    基于 requests 下载文件，支持断点续传和 rich 进度条

    - url: 文件地址
    - file_name: 文件名
    - retry: 重试次数
    - proxies: 代理
    """
    import os
    import requests
    import rich.progress

    # 处理代理配置
    if proxies:
        if isinstance(proxies, dict):
            proxies = {
                "all": (
                    proxies.get("http")
                    or proxies.get("https")
                    or proxies.get("all")
                    or proxies.get("http://")
                    or proxies.get("https://")
                )
            }
        elif isinstance(proxies, str):
            proxies = {"all": proxies}

    except_list = []
    for attempt in range(retry + 1):
        try:
            file_exists = os.path.isfile(file_name)
            resume_byte_pos = os.path.getsize(file_name) if file_exists else 0
            headers = (
                {"Range": f"bytes={resume_byte_pos}-"} if resume_byte_pos > 0 else {}
            )
            response = requests.get(url, stream=True, proxies=proxies, headers=headers)
            if response.status_code == 206:  # 支持断点续传
                content_length = int(response.headers.get("Content-Length", 0))
                total_size = resume_byte_pos + content_length
            elif response.status_code == 200:  # 不支持断点续传
                if resume_byte_pos > 0:
                    os.remove(file_name)
                total_size = int(response.headers.get("Content-Length", 0))
                resume_byte_pos = 0
            else:
                response.raise_for_status()
            mode = "ab" if resume_byte_pos > 0 else "wb"
            with open(file_name, mode) as f:
                with rich.progress.Progress(
                    rich.progress.SpinnerColumn(),
                    rich.progress.TextColumn(
                        "[progress.description]{task.description}"
                    ),
                    rich.progress.BarColumn(),
                    rich.progress.TextColumn(
                        "[progress.percentage]{task.percentage:>3.0f}%"
                    ),
                    rich.progress.DownloadColumn(),
                    rich.progress.TransferSpeedColumn(),
                ) as progress:
                    task = progress.add_task(
                        f"[green]{file_name}下载中...",
                        total=total_size,
                        completed=resume_byte_pos,
                    )
                    for data in response.iter_content(chunk_size=8192):
                        if not data:
                            break
                        f.write(data)
                        progress.update(task, advance=len(data))

            return file_name

        except Exception as e:
            except_list.append(e)
            if attempt < retry:
                if os.path.exists(file_name):
                    os.remove(file_name)
                continue
            raise Exception(
                f"下载失败，已尝试 {retry + 1} 次\n最后一次错误: {e!r}"
            ) from e
