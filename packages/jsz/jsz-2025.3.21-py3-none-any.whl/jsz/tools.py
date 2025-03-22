"""
基本工具库
"""

import sys
import time
import datetime
import os
import random
import re
import urllib.parse as url
from loguru import logger
from .richx import track, print


__all__ = [
    "aes_encrypt",
    "aes_decrypt",
    "aes_keygen",
    "base64_decode",
    "base64_encode",
    "check_run",
    "clear",
    "cookies_dict2str",
    "cookies_str2dict",
    "copy_text",
    "copy_file",
    "date_next",
    "deque",
    "ddddocr",
    "datetime",
    "df",
    "faker",
    "filedir",
    "filepath",
    "fromtimestamp",
    "format_exception",
    "func_kv",
    "get_proxies",
    "getlock",
    "getpid",
    "gettid",
    "get_ip",
    "get_real_ip",
    "get_2fa_secret",
    "get_2fa_token",
    "ipython_extension",
    "iter_cycle",
    "iter_product",
    "iter_permutations",
    "iter_flatten",
    "jsonpath",
    "jsonpath_first",
    "listdir",
    "logger",
    "make_archive",
    "md2html",
    "moviepy_audio",
    "moviepy_video",
    "move_file",
    "md5",
    "now",
    "num2cn",
    "os",
    "open_url",
    "paste_text",
    "pdf2text",
    "pl",
    "print_exception",
    "python",
    "queue",
    "random",
    "random_str",
    "re",
    "re_first",
    "read_csv",
    "read_json",
    "read_excel",
    "remove_file",
    "retry",
    "run_myself",
    "run_nohup",
    "run_process",
    "run_remote",
    "rsa_encrypt",
    "rsa_decrypt",
    "rsa_keygen",
    "send_bot",
    "set_title",
    "sha1",
    "sha256",
    "sha512",
    "sleep",
    "sleep_progress",
    "sys",
    "time_next",
    "time",
    "timeit",
    "time_fmt",
    "timeparse",
    "timeparse2",
    "timestamp",
    "to_excel",
    "to_gzip",
    "to_json",
    "today",
    "tongji_content",
    "try_get",
    "ua",
    "url",
    "unzip_file",
    "unpack_archive",
    "wait",
    "which",
    "win11toast",
    "zip_file",
]

getpid = os.getpid
python = sys.executable


def queue(maxsize=0):
    """
    队列, 默认为 0 表示不限制。

    - maxsize: 最大长度
    """
    import queue

    return queue.Queue(maxsize=maxsize)


def deque(maxlen=None):
    """
    队列, 默认为 None 表示不限制。

    - maxlen: 最大长度
    """
    import collections

    return collections.deque(maxlen=maxlen)


def timeparse(
    timestr: str,
    parserinfo: None = None,
    dayfirst: bool | None = None,
    yearfirst: bool | None = None,
    ignoretz: bool = True,
    fuzzy: bool = False,
    fuzzy_with_tokens: bool = False,
    default: None = None,
    tzinfos: None = None,
):
    """
    ## 基于 dateutil.parser 封装

    - timestr: 时间字符串
    - parserinfo: 解析器信息
    - dayfirst: 无法判断时, 第一个数字是否为日
    - yearfirst: 无法判断时, 第一个数字是否为年份
    - ignoretz: 是否忽略时区信息, 默认忽略时区信息
    - fuzzy: 是否启用模糊匹配, 启动后可以从字符串中提取出时间字符串中的日期和时间信息
    - fuzzy_with_tokens: 是否返回模糊匹配的结果
    - default: 当解析失败时返回的默认值
    - tzinfos: 时区信息
    """
    from dateutil.parser import parse

    return parse(
        timestr,
        parserinfo=parserinfo,
        dayfirst=dayfirst,
        yearfirst=yearfirst,
        ignoretz=ignoretz,
        fuzzy=fuzzy,
        fuzzy_with_tokens=fuzzy_with_tokens,
        default=default,
        tzinfos=tzinfos,
    )


def timeparse2(
    date_string,
    date_formats=None,
    languages=None,
    locales=None,
    region=None,
    settings=None,
    detect_languages_function=None,
):
    """
    ## dateparser 封装

    - date_string: 时间字符串
    - date_formats: 时间格式列表, 例如 ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
    - languages: 语言列表, 例如 ["zh", "en"]
    - locales: 地区列表, 例如 ["zh", "en"]
    - region: 地区
    - settings: 设置
    - detect_languages_function: 检测语言函数
    """
    try:
        from dateparser import parse
    except ImportError:
        raise ImportError("请先安装 dateparser 模块\n\npip install dateparser")

    return parse(
        date_string,
        date_formats=date_formats,
        languages=languages,
        locales=locales,
        region=region,
        settings=settings,
        detect_languages_function=detect_languages_function,
    )


def filedir():
    """
    当前脚本文件所在目录
    """
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def filepath(abs=True):
    """
    文件路径, 默认为绝对路径

    - abs: 是否返回绝对路径
    """
    path = sys.argv[0]
    if abs:
        return os.path.abspath(path)
    return path.rsplit(os.path.sep, 1)[-1]


def get_2fa_secret():
    """
    2FA(双因素身份验证)密钥生成
    """
    secret = "".join(random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", 32))
    return secret


def get_2fa_token(secret):
    """
    2FA(双因素身份验证)通过密钥获取实时 token

    - secret: 2FA(双因素身份验证)密钥, 可以调用 get_2fa_secret() 获取
    """
    import base64
    import hmac
    import time

    secret_bytes = base64.b32decode(secret)
    time_interval = int(time.time()) // 30
    hmac_value = hmac.new(secret_bytes, time_interval.to_bytes(8), "sha1").digest()
    offset = hmac_value[-1] & 0x0F
    dynamic_code = (
        (hmac_value[offset] & 0x7F) << 24
        | (hmac_value[offset + 1] & 0xFF) << 16
        | (hmac_value[offset + 2] & 0xFF) << 8
        | (hmac_value[offset + 3] & 0xFF)
    )
    return f"{dynamic_code % 10**6:06d}"


def sha1(string: str | bytes) -> str:
    """
     hashlib.sha1 封装

    - string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha1(string).hexdigest()


def sha256(string: str | bytes) -> str:
    """
     hashlib.sha256 封装

    - string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha256(string).hexdigest()


def sha512(string: str | bytes) -> str:
    """
     hashlib.sha512 封装

    - string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha512(string).hexdigest()


def md5(string: bytes | str):
    """
    md5 加密

    - string: 字符串或字节
    """
    import hashlib

    if isinstance(string, str):
        string = string.encode()
    result = hashlib.md5(string).hexdigest()
    return result


def gettid():
    """
    获取线程ID
    """
    import threading

    return threading.get_ident()


def getlock():
    """
    获取线程锁
    """
    import threading

    return threading.Lock()


def ipython_extension():
    """
    ipython 插件, 全局 pretty print, 全局 traceback
    """
    from rich.pretty import install
    from rich.traceback import install as tr_install

    install()
    tr_install()


def faker():
    """
    faker 封装，增加 faker().zh 为中文
    """
    if hasattr(faker, "fake"):
        return faker.fake

    from faker import Faker

    fake = Faker()
    fake.zh = Faker("zh")
    faker.fake = fake
    return fake


def base64_encode(string: bytes | str, decode: bool = True):
    """
    base64编码

    - string: 字符串或字节
    - decode: 是否解码, 默认为 True
    """
    import base64

    if isinstance(string, str):
        string = string.encode()
    if decode:
        return base64.b64encode(string).decode()
    return base64.b64encode(string)


def base64_decode(string: bytes | str, decode: bool = True):
    """
    base64解码

    - string: 字符串或字节
    - decode: 是否解码, 默认为 True
    """
    import base64

    if isinstance(string, str):
        string = string.encode()
    if decode:
        return base64.b64decode(string).decode()
    return base64.b64decode(string)


def clear():
    """
    清屏
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_proxies(
    n: int | str | list = 1,
    httpx: bool = False,
    proxies_dict: dict | None = None,
):
    """
    ## 随机返回代理

    如果未设置 proxies_dict，则检测 get_proxies.proxies_dict

    - n: 代理选择, 数字会自动转换为对应的字符串, 列表会随机选择一个
    - httpx: 是否返回 httpx 格式的代理, 默认为 False
    - proxies_dict: 代理字典，{'1': ['https://localhost:7890'], '2': ['https://localhost:7891']}
    """
    if not proxies_dict:
        if hasattr(get_proxies, "proxies_dict"):
            proxies_dict = get_proxies.proxies_dict
        if not proxies_dict:
            print("[red]未配置 proxies_dict 或 get_proxies.proxies_dict[/]")
            raise Exception()
    if isinstance(n, list):
        n = random.choice(n)
    proxyurl = proxies_dict.get(str(n), [None])
    if isinstance(proxyurl, list):
        proxyurl = random.choice(proxyurl)
    if type(proxyurl).__name__ == "function":
        proxyurl = proxyurl()
    if httpx:
        proxies = proxyurl
    else:
        proxies = {
            "http": proxyurl,
            "https": proxyurl,
        }
    return proxies


def listdir(
    path=None,
    key=None,
    reverse: bool = False,
    glob: bool = False,
    *,
    root_dir: str | None = None,
    dir_fd: int | None = None,
    recursive: bool = False,
    include_hidden: bool = False,
):
    """
    文件夹下文件列表, 基于 os.listdir 和 glob 封装。

    - path: 目录路径, 默认当前目录。
    - key: 排序方式, 默认为 None。
    - reverse: 指定是否反转, 默认否。
    - glob: 是否使用 glob 方式, 默认否。
    - root_dir: 根目录, 默认当前目录。
    - dir_fd: 目录描述符, 默认 None。
    - recursive: 是否递归, 默认否。
    - include_hidden: 是否包含隐藏文件, 默认否。
    """
    if glob or root_dir or dir_fd or recursive or include_hidden:
        from glob import glob as _glob

        return sorted(
            _glob(
                path,
                root_dir=root_dir,
                dir_fd=dir_fd,
                recursive=recursive,
                include_hidden=include_hidden,
            ),
            key=key,
            reverse=reverse,
        )

    return sorted(
        os.listdir(path),
        key=key,
        reverse=reverse,
    )


def now(fmt_type: int | None = None, fmt: str | None = None):
    """
    默认返回当前时间, 精度到秒。

    - fmt_type: 格式化类型。
    - fmt: 通过 strformat 格式化。

    - fmt=None -> datetime.datetime(2024, 1, 18, 11, 44, 57)
    - fmt_type=1 -> "2024-01-18 11:44:57"
    - fmt_type=2 -> 1705549497 # 10位时间戳
    - fmt_type=3 -> 1705555472772 # 13位时间戳
    - fmt_type=4 -> datetime.date(2024, 1, 18)
    - fmt_type=5 -> "2024-01-18"
    - fmt_type=6 -> "2024/01/18"
    - fmt_type=7 -> "20240118"
    """
    if fmt:
        return datetime.datetime.now().strftime(fmt)
    if fmt_type == 1:
        return f"{datetime.datetime.now().replace(microsecond=0)}"
    elif fmt_type == 2:
        return int(time.time())
    elif fmt_type == 3:
        return int(time.time() * 1000)
    elif fmt_type == 4:
        return datetime.date.today()
    elif fmt_type == 5:
        return f"{datetime.date.today()}"
    elif fmt_type == 6:
        return f"{datetime.date.today():%Y/%m/%d}"
    elif fmt_type == 7:
        return f"{datetime.date.today():%Y%m%d}"
    else:
        return datetime.datetime.now().replace(microsecond=0)


def timestamp(n: int = 10):
    """
    返回时间戳

    - n: 时间戳位数, 可选 10位和13位。
    """
    if n == 13:
        return int(time.time() * 1000)
    return int(time.time())


def today(fmt_type=None):
    """
    返回今天日期

    - fmt_type: 格式化类型

    ```
    1 -> "2024-01-18"
    2 -> "2024/01/18"
    3 -> "20240118"
    ```
    """
    if not fmt_type:
        return datetime.date.today()
    if fmt_type == 1:
        return f"{datetime.date.today()}"
    elif fmt_type == 2:
        return f"{datetime.date.today():%Y/%m/%d}"
    elif fmt_type == 3:
        return f"{datetime.date.today():%Y%m%d}"


def tongji_content(
    content: str,
    keywords: list[str],
    strict: bool = False,
    to_dict: bool = False,
):
    """
    统计每篇文章中关键词出现次数

    - content: 需要统计的文本。
    - keywords: 需要统计的关键词。
    - strict: 是否严格模式，默认False 忽略大小写, True 不忽略。
    - to_dict: 是否导出为字典格式。
    """
    keyword_tongji_list = []
    for keyword in set(keywords):
        if not strict:
            p1 = content.upper().count(keyword.upper())
        else:
            p1 = content.count(keyword)
        if p1 > 0:
            keyword_tongji_list.append([keyword, p1])
    if to_dict:
        return dict(keyword_tongji_list)
    return [
        f"{k[0]}({k[1]})"
        for k in sorted(
            keyword_tongji_list,
            key=lambda x: x[-1],
            reverse=True,
        )
    ]


def date_next(
    days: int = 0,
    weeks: int = 0,
    start: datetime.date | None = None,
):
    """
    返回下一个的日期, 默认为0, 负数为过去, 正数为未来。

    - days: 偏移天数
    - weeks: 偏移周数
    - start: 开始时间, (2024, 1, 20, 10, 12, 23) 或者 datetime.datetime(2024, 1, 20, 10, 12, 23)
    """
    if start:
        if isinstance(start, datetime.datetime):
            start = start
        elif isinstance(start, datetime.date):
            start = datetime.datetime(*start.timetuple()[:6])
        else:
            start = datetime.datetime(*start)
    else:
        start = datetime.datetime.now().replace(microsecond=0)
    return start + datetime.timedelta(days=days, weeks=weeks)


def time_next(
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    weeks: int = 0,
    months: int = 0,
    years: int = 0,
    weekday: int | None = None,
    start: tuple | datetime.datetime | None = None,
    fmt: str | None = None,
):
    """
    返回下一个的时间, 默认为0, 负数为过去, 正数为未来。先算月份再算年, 然后依次计算。

    - days: 偏移天数
    - hours: 偏移小时数
    - minutes: 偏移分钟数
    - seconds: 偏移秒数
    - weeks: 偏移周数
    - months: 偏移月数
    - years: 偏移年数
    - weekday: 下一个周几，1~7表示周一到周日。-1~-7表示上一个周一到周日。可以配合 start 参数来指定开始时间。
    - start: 开始时间, (2024, 1, 20, 10, 12, 23) 或者 datetime.datetime(2024, 1, 20, 10, 12, 23)
    - fmt: 指定输出格式。
    """
    import calendar
    import datetime

    if start:
        if isinstance(start, datetime.datetime):
            start = start
        elif isinstance(start, datetime.date):
            start = datetime.datetime(*start.timetuple()[:6])
        else:
            start = datetime.datetime(*start)
    else:
        start = datetime.datetime.now().replace(microsecond=0)
    if months:
        # 获取下个时间的年份和月份
        next_year = start.year + (start.month == 12)
        next_month = start.month + months
        if next_month > 12:
            next_year += next_month // 12
            next_month = next_month % 12
        if next_month < 1:
            next_year -= abs(next_month) // 12 + 1
            next_month = 12 - abs(next_month) % 12

        # 获取下个时间的最大天数
        next_month_max_day = calendar.monthrange(next_year, next_month)[1]
        start = start.replace(
            year=next_year, month=next_month, day=min(start.day, next_month_max_day)
        )
    if years:
        real_next_year = start.year + years
        next_month_max_day = calendar.monthrange(real_next_year, start.month)[1]
        start = start.replace(
            year=real_next_year,
            month=start.month,
            day=min(start.day, next_month_max_day),
        )
    if weekday:
        days = days + abs(weekday) - 1 - start.weekday()
        if weekday > 0:
            days += 7 * (days < 0)
        if weekday < 0:
            days -= 7 * (days > 0)
    results = start + datetime.timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        weeks=weeks,
    )

    if fmt:
        return results.strftime(fmt)
    else:
        return results


def sleep(seconds: float):
    """
    等待n秒, 模拟阻塞

    - seconds: 等待秒数
    """
    return time.sleep(seconds)


def sleep_progress(
    n: int = 1,
    info: str | None = None,
    transient=False,
):
    """
    等待n秒, 模拟阻塞, 进度条。

    - n: 等待秒数
    - info: 定制输出信息
    - transient: 运行完是否隐藏, 默认为 False
    """
    if not info:
        info = f"等待{n}秒"
    for _ in track(range(int(n // 0.02)), info, transient=transient):
        time.sleep(0.02)


def fromtimestamp(timestamp: int | str | float, split: bool = True):
    """
    从时间戳返回 datetime 格式, 自动判断字符串和数字, 不符合格式要求会原样返回。

    - timestamp: 时间戳
    - split: 是否截取10位时间戳
    """
    try:
        if split:
            return datetime.datetime.fromtimestamp(float(str(timestamp)[:10]))
        else:
            return datetime.datetime.fromtimestamp(float(timestamp))
    except Exception:
        return timestamp


def read_json(path_string, encoding="utf-8"):
    """
    JSON 反序列化, 读取 JSON 文件

    - path_string: JSON 文件路径或字符串
    - encoding: 编码
    """
    import json

    if not os.path.isfile(path_string):
        try:
            return json.loads(path_string)
        except Exception:
            try:
                import ast

                return ast.literal_eval(path_string)
            except Exception:
                import demjson3

                return demjson3.decode(path_string)
    with open(path_string, "r", encoding=encoding) as f:
        try:
            q = json.load(f)
        except Exception:
            try:
                import ast

                q = ast.literal_eval(f.read())
            except Exception:
                import demjson3

                q = demjson3.decode(f.read())
    return q


def read_excel(
    io,
    sheet_name: str | int | list | None = 0,
    **kwargs,
):
    """
    读取 Excel 文件

    - io: 文件路径或文件对象
    - sheet_name: 工作表名称
    ---
    其他参数
    - header: 表头所在行
    - names: 列名
    - index_col: 索引列
    - usecols: 列选择
    - dtype: 数据类型
    - engine: 引擎
    - converters: 转换器
    - true_values: 真值
    - false_values: 假值
    - skiprows: 跳过行数
    - nrows: 读取行数
    - na_values: 空值
    - keep_default_na: 默认空值
    - na_filter: 空值过滤
    - verbose: 详细信息
    - parse_dates: 解析日期
    - date_format: 日期格式
    - thousands: 千位分隔符
    - decimal: 小数点分隔符
    - comment: 注释
    - skipfooter: 跳过尾部行数
    - storage_options: 存储选项
    - dtype_backend: "pyarrow" | "numpy_nullable"
    - engine_kwargs: 引擎参数
    """
    import pandas as pd

    return pd.read_excel(
        io,
        sheet_name=sheet_name,
        **kwargs,
    )


def read_csv(
    filepath_or_buffer,
    encoding="utf-8",
    sep=",",
    header: int | list[int] | None = 0,
    names: list[str] | None = None,
    **kwargs,
):
    """
    CSV 序列化, 读取 CSV 文件

    - filepath_or_buffer: 文件路径或文件对象
    - encoding: 编码
    - sep: 分隔符
    - header: 表头所在行
    - names: 列名
    """
    import pandas as pd

    return pd.read_csv(
        filepath_or_buffer,
        encoding=encoding,
        sep=sep,
        header=header,
        names=names,
        **kwargs,
    )


def to_json(
    obj,
    filename=None,
    encoding="utf-8",
    ensure_ascii: bool = False,
    indent: int | None = None,
    separators: tuple | None = None,
    default_dict: dict | None = None,
):
    """
    JSON 序列化, 将Python 对象写入文件或转换为字符串。

    - filename: JSON 文件路径
    - indent: 缩进
    - ensure_ascii: 默认不转为unicode
    - separators: 分隔符, 默认为 (", ", ": ")
    - default_dict: 自定义转换类型, 启用后默认会转换成字符串。例如: {numpy.ndarray: lambda x: x.tolist()}
    """
    import json

    def default_tool(obj):
        for i in default_dict:
            if isinstance(obj, i):
                return default_dict[i](obj)
        else:
            return str(obj)

    default = default_tool if default_dict else None

    if not filename:
        return json.dumps(
            obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
            separators=separators,
            default=default,
        )
    else:
        with open(filename, "w", encoding=encoding) as f:
            json.dump(
                obj,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                separators=separators,
                default=default,
            )


def get_ip():
    """
    获取本机 IP
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_real_ip(proxies=None):
    """
    获取本机真实 IP

    - proxies: 代理
    """
    import requests

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

    ip = requests.get("https://httpbin.org/ip", proxies=proxies).json()
    ip.update({"proxies": proxies})
    return ip


def df(
    data,
    index: list | None = None,
    columns: list | None = None,
    dtype: dict | None = None,
    copy: bool = False,
):
    """
    转换为 DataFrame

    - data: 数据
    - index: 索引
    - columns: 列名
    - dtype: 数据类型
    - copy: 是否复制
    """
    import pandas as pd

    return pd.DataFrame(
        data,
        index=index,
        columns=columns,
        dtype=dtype,
        copy=copy,
    )


def pl(data, **kwargs):
    """
    转换为 Polars DataFrame

    - data: 数据
    """
    import polars as pl

    return pl.DataFrame(data, **kwargs)


def md2html(text: str, **kwargs):
    """
    将 markdown 转换为 html

    - text: markdown 字符串
    """
    import markdown

    return markdown.markdown(text, **kwargs)


def to_excel(
    df,
    path: str,
    mode: str = "w",
    index: bool = False,
    engine: str = "xlsxwriter",
):
    """
    ## 导出 excel

    - df: dataframe 对象, 多个sheet可以通过字典传入, 键为sheet名称。`{"sheet_name1": df1, "sheet_name2": df2}`
    - path: 文件保存路径
    - mode: 默认 `w` 为全新写入; 如果为 `a` 则为插入, 引擎会改为 openpyxl。
    - strings_to_urls: 默认不转换url
    - index: 默认不导出索引
    - engine: 默认引擎使用xlsxwriter, 其他选项有 'auto'、'openpyxl'、'odf'
    """
    import pandas as pd

    if engine == "xlsxwriter":
        engine_kwargs = {"options": {"strings_to_urls": False}}

    if mode == "a":
        engine = "openpyxl"
        engine_kwargs = None

    with pd.ExcelWriter(
        path,
        engine=engine,  # type: ignore
        mode=mode,  # type: ignore
        engine_kwargs=engine_kwargs,
    ) as writer:
        if isinstance(df, dict):
            for sheet in df:
                df.get(sheet).to_excel(
                    writer,
                    index=index,
                    sheet_name=sheet,
                )
        else:
            df.to_excel(writer, index=index)


def print_exception(limit=None, file=None, chain=True) -> None:
    """
    打印异常信息

    - limit: 限制打印行数
    - file: 文件
    - chain: 是否打印异常链
    """
    from traceback import print_exc

    print_exc(limit=limit, file=file, chain=chain)


def format_exception(limit=None, chain=True) -> str:
    """
    # 格式化异常信息

    - limit: 限制打印行数
    - chain: 是否打印异常链
    """
    from traceback import format_exc

    return format_exc(limit=limit, chain=chain)


def retry(
    nums: int = 3,
    log: bool = False,
    show_error: bool = False,
    sleep: float = 0.1,
):
    """
    ## 重试, 支持同步和异步函数

    - nums: 默认重试 3 次。
    - log: 日志, 开启后会打印详细的错误日志。
    - show_error: 重试周期内未成功是否抛出错误, 默认不抛出, 多线程池建议打开该选项, 可以更好的统计运行情况。
    - sleep: 每次重试间隔时间, 默认 1 秒。

    ```python
    import jsz

    @jsz.retry(3, log=True)
    def crawl():
        url = "https://www.google.com"
        res = jsz.requests(url, timeout=2)
        print(res)

    crawl()
    ```
    """
    from functools import wraps
    import asyncio

    def wrap(f):
        @wraps(f)
        def func(*args, **kwargs):
            error = Exception
            for num in range(nums):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    error = e
                    if log:
                        logger.error(
                            f"函数 {f.__name__} | 第 {num + 1}/{nums} 次运行失败: {format_exception()}"
                        )
                    time.sleep(sleep)
            if show_error:
                raise error

        @wraps(f)
        async def async_func(*args, **kwargs):
            error = Exception
            for num in range(nums):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    error = e
                    if log:
                        logger.error(
                            f"函数 {f.__name__} | 第 {num + 1}/{nums} 次运行失败: {format_exception()}"
                        )
                    await asyncio.sleep(sleep)

            if show_error:
                raise error

        if asyncio.iscoroutinefunction(f):
            return async_func
        else:
            return func

    return wrap


def send_bot(
    content: str = "测试",
    bot_key: str = "",
    msgtype: str = "markdown",
    filepath: str | None = None,
    mentioned_list: list = [],
    proxies=None,
):
    """
    ## 企业微信群机器人

    ```
    <font color="info">绿色</font>
    <font color="comment">灰色</font>
    <font color="warning">橙红色</font>
    ```

    - content: 文本
    - bot_key: 微信机器人key, 也可以设置环境变量 BOT_KEY 自动读取, 参数权重高于环境变量。
    - msgtype: 类型, 包括 markdown, text, file, voice, image
    - filepath: 文件路径，非文本类型使用。
    - mentioned_list: 提醒用户列表, 填入手机号或 "@all", 仅支持 text 类型。
    - proxies: 代理
    """
    import requests

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

    msg = {}
    if msgtype not in ["markdown", "text", "file", "voice", "image"]:
        raise NameError('类型仅支持 "markdown", "text", "file", "voice", "image"')
    if not bot_key:
        bot_key = os.getenv("BOT_KEY", "")
        if not bot_key:
            print("[red]未配置全局变量 BOT_KEY，也未填写参数 bot_key[/]")
            raise Exception("请填写 bot_key")
    if "key=" in bot_key:
        raise Exception("bot_key 只需要填入 `key=` 后面的部分")
    if mentioned_list:
        msgtype = "text"
    if msgtype == "file" or msgtype == "voice":
        file_upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={bot_key}&type=file"
        files = {filepath.rsplit(".", 1)[0]: open(filepath, "rb")}
        for _ in range(3):
            try:
                resp = requests.post(
                    file_upload_url, files=files, proxies=proxies, timeout=100
                )
                msg = {"media_id": resp.json().get("media_id")}
                break
            except Exception:
                time.sleep(0.5)
        else:
            logger.error("上传文件失败")
            return
    elif msgtype == "image":
        content = open(filepath, "rb").read()
        msg = {"base64": base64_encode(content), "md5": md5(content)}
    elif msgtype == "text":
        msg = {"content": content, "mentioned_mobile_list": mentioned_list}
    else:
        msg = {"content": content}
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    for _ in range(3):
        try:
            response = requests.post(
                url,
                json={"msgtype": msgtype, msgtype: msg},
                proxies=proxies,
                timeout=100,
            )
            return response
        except Exception:
            time.sleep(0.5)
    logger.error("发送失败")


def pdf2text(filepath):
    """
    从 pdf 提取文本内容

    - filepath: 文件路径
    """
    from pypdf import PdfReader

    reader = PdfReader(filepath)
    content = "".join([i.extract_text() for i in reader.pages])
    return content


def timeit(function):
    """
    计时器, 支持同步和异步函数

    ```
    @timeit
    def hello():
        time.sleep(5)
    ```
    """
    from functools import wraps
    import asyncio

    @wraps(function)
    def func(*args, **kwargs):
        t0 = time.time() * 1000
        result = function(*args, **kwargs)
        print(f"运行 {function.__name__} 耗时: {time.time() * 1000 - t0:.2f} ms")
        return result

    @wraps(function)
    async def async_func(*args, **kwargs):
        t0 = time.time() * 1000
        result = await function(*args, **kwargs)
        print(f"运行 {function.__name__} 耗时: {time.time() * 1000 - t0:.2f} ms")
        return result

    if asyncio.iscoroutinefunction(function):
        return async_func
    else:
        return func


def ua(version_from=101, version_to=133, close=True):
    """
    随机ua

    - versison_from: chrome 版本大于101
    - version_to: chrome 版本小于132
    - close: 是否关闭连接, 默认为 True
    """
    ua_list = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(version_from, version_to)}.0) Gecko/20100101 Firefox/{random.randint(version_from, version_to)}.0",
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(version_from, version_to)}.0.0.0 Safari/537.36 Edg/{random.randint(version_from, version_to)}.0.0.0",
    ]

    return {
        "connection": "close" if close else "keep-alive",
        "user-agent": random.choice(ua_list),
    }


def wait(n: int = 0):
    """
    后台运行, 异步不阻塞。

    - n: 等待秒数

    ```python
    @jsz.wait(2)
    def hello():
        print('运行完毕')

    hello()
    ```
    """
    from threading import Timer
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def delayed_call():
                return func(*args, **kwargs)

            t = Timer(n, delayed_call)
            t.start()
            return t

        return wrapper

    return decorator


def ddddocr(
    img,
    png_fix: bool = False,
    old: bool = False,
    new: bool = False,
    use_gpu: bool = False,
    onnx_path: str = "",
    charsets_path: str = "",
):
    """
    ## 使用ddddocr识别验证码

    - img: 图片对象，支持传入文件路径
    - png_fix: 是否修复图片，修复后支持黑色透明图片
    - old: 老模型
    - new: 新模型
    - use_gpu: 使用GPU
    - onnx_path: onnx 模型路径
    - charsets_path: 字符集路径
    """
    try:
        import ddddocr
    except Exception:
        print("[red]请先安装 ddddocr, 否则无法使用[/]\n\npip install ddddocr")
        return

    if os.path.exists(img):
        img = open(img, "rb").read()
    d = ddddocr.DdddOcr(
        show_ad=False,
        old=old,
        beta=new,
        use_gpu=use_gpu,
        import_onnx_path=onnx_path,
        charsets_path=charsets_path,
    )
    return d.classification(img=img, png_fix=png_fix)


def win11toast(
    message="",
    app_id="通知",
    duration="short",
    icon_path="",
):
    """
    Windows 通知

    - message: 通知内容, 最多5行, 尽量精简内容
    - app_id: 应用ID，可以作为标题
    - duration: 通知时间长度, 可以设置 short 和 long
    - icon_path: 文本左侧图片
    """
    if sys.platform != "win32":
        print("[red]win11toast 只支持 Windows 系统[/]")
        return
    import winsdk.windows.ui.notifications as notifications
    import winsdk.windows.data.xml.dom as dom

    toast_xml = f"""
    <toast activationType="protocol" launch="" scenario="default" duration="{duration}">
        <visual>
            <binding template="ToastGeneric">
                <image placement="appLogoOverride" src="{icon_path}" />
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
    """
    xml_doc = dom.XmlDocument()
    xml_doc.load_xml(toast_xml)
    toast = notifications.ToastNotification(xml_doc)
    notifier = notifications.ToastNotificationManager.create_toast_notifier(app_id)
    notifier.show(toast)


def run_process(
    command: str,
    n: int = 1,
    stdout: bool = False,
):
    """
    ## 多个进程运行程序
    脚本中可以使用 getpid() 获取进程号, gettid() 获取线程号, 使用 python 建议使用 sys.executable

    - command: 命令, 字符串
    - n: 并发运行的实例数量
    - stdout: 默认不输出, True 输出
    """
    import subprocess

    if stdout:
        return subprocess.getoutput(command)

    processes = []

    for _ in range(n):
        process = subprocess.Popen(
            command,
            shell=True if isinstance(command, str) else False,
        )
        processes.append(process)

    # 等待所有进程完成
    for process in processes:
        process.wait()


def run_nohup(command: str, *args, **kwargs):
    """
    后台运行命令

    - command: 命令, 字符串
    """
    import subprocess

    process = subprocess.Popen(
        command,
        shell=True if isinstance(command, str) else False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        *args,
        **kwargs,
    )
    return process


def to_gzip(input_path, dir_format="gztar"):
    """
    ## 压缩文件或目录

    压缩目录时，需要配置 dir_format 参数。

    - input_path: 输入路径，文件路径或目录
    - dir_format: 压缩目录格式, 支持 "zip", "tar", "gztar", "bztar", or "xztar"
    """
    import os
    import gzip
    import shutil

    if os.path.isfile(input_path):
        with (
            open(input_path, "rb") as f_in,
            gzip.open(f"{input_path}.gz", "wb") as f_out,
        ):
            shutil.copyfileobj(f_in, f_out)
        print(f"文件 {input_path} 成功压缩为 {input_path}.gz")
    elif os.path.isdir(input_path):
        output_path = shutil.make_archive(
            f"{input_path.replace('/', '')}",
            dir_format,
            input_path,
        )
        print(f"目录 {input_path} 成功压缩为 {output_path}")
    else:
        print(f"提供的路径 ({input_path}) 无效.")


def jsonpath(obj, expr, result_type="VALUE", debug=0, use_eval=True):
    """
    jsonpath 解析器 https://goessner.net/articles/JsonPath/

    - obj: 目标对象
    - expr: 表达式
    - result_type: 结果类型, 支持 "VALUE", "IPATH", "PATH"
    - debug: 调试模式, 0 为关闭, 1 为开启
    - use_eval: 使用 eval 函数, 默认开启
    """
    from jsonpath import jsonpath

    return jsonpath(
        obj,
        expr,
        result_type=result_type,
        debug=debug,
        use_eval=use_eval,
    )


def run_remote(
    host,
    user,
    command: str | None = None,
    port=None,
    config=None,
    gateway=None,
    forward_agent=None,
    connect_timeout=None,
    connect_kwargs: dict | None = None,
    inline_ssh_env=None,
    hide=False,
    shell=False,
):
    """
    运行远程命令

    - host: 主机
    - user: 用户名
    - command: 命令
    - port: 端口
    - config: 配置文件
    - gateway: 网关
    - forward_agent: 转发代理
    - connect_timeout: 连接超时
    - connect_kwargs: 连接参数, 字典格式, 密码为 {"password": "password"}
    - inline_ssh_env: 内联 ssh 环境变量, 字典格式
    - hide: 隐藏命令
    - shell: 是否进入 shell, 当为 True 时, 进入 shell 模式, 不支持 command 参数
    """
    try:
        from fabric import Connection
    except Exception:
        print("[red]请先安装 fabric, 否则无法使用[/]\n\npip install fabric")
        return

    c = Connection(
        host,
        user=user,
        port=port,
        config=config,
        gateway=gateway,
        forward_agent=forward_agent,
        connect_timeout=connect_timeout,
        inline_ssh_env=inline_ssh_env,
        connect_kwargs=connect_kwargs,
    )
    if shell:
        return c.shell()
    if not command:
        return c
    return c.run(command, hide=hide)


def num2cn(num: int | float, precision: int = 2):
    """
    数字转中文

    - num: 数字, 必须是整数或浮点数
    - precision: 保留几位小数, 默认为 2, 必须是整数且大于等于0
    """
    if not isinstance(num, (int, float)):
        raise TypeError("必须是整数或浮点数")
    if not isinstance(precision, int) or precision < 0:
        raise Exception("精度必须是整数且大于等于0")
    int_len = len(str(int(abs(num))))
    if int_len < 5:
        if str(num) == str(int(num)):
            return f"{num}"
        return f"{num:.{precision}f}"
    else:
        if int_len < 9:
            return f"{num / 1e4:.{precision}f}万"
        elif 13 > int_len >= 9:
            return f"{num / 1e8:.{precision}f}亿"
        elif 17 > int_len >= 13:
            return f"{num / 1e12:.{precision}f}万亿"
        elif 21 > int_len >= 17:
            return f"{num / 1e16:.{precision}f}亿亿"
        else:
            return f"{num:.{precision}e}"


def check_run(run_word: str = "nostop", stop_word: None | str = None):
    """
    当前程序运行前检测是否正在运行, 当 run_word 在 sys.argv 中时忽略检测; 当 stop_word 在 sys.argv 中时结束程序。

    - run_word: 运行时的参数, 默认为 nostop
    - stop_word: 停止时的参数, 默认为 None
    """
    if os.name == "nt":
        print("暂不支持 Windows 系统")
        return
    if run_word in sys.argv:
        return
    if stop_word and stop_word in sys.argv:
        exit()

    import inspect

    stack = inspect.stack()
    caller_frame_record = stack[1]
    caller_file = caller_frame_record.filename
    filename = caller_file.rsplit(os.sep, 1)[-1]
    username = os.getlogin()
    results = run_process(
        f"ps aux | grep {username!r} | grep {filename!r} | grep -v 'sh -c' | grep -v grep",
        stdout=True,
    )
    print(results)
    if results.count(filename) > 1:
        print("程序正在运行")
        exit()


def run_myself(word="nostop", python=None):
    """
    运行脚本自身

    - word: 运行时的参数, 默认为 nostop
    - python: python 路径, 默认为 sys.executable
    """
    import inspect

    if not python:
        python_path = sys.executable

    stack = inspect.stack()
    caller_frame_record = stack[1]
    caller_file = caller_frame_record.filename
    run_nohup(f"{python_path} {caller_file} {word}")


def cookies_str2dict(cookies_str: str) -> dict[str, str]:
    """
    将 cookies 字符串转换为字典格式

    - cookies_str: 字符串格式的 cookies
    """
    cookies = dict([
        i.strip().split("=", 1) for i in cookies_str.strip("; ").split(";")
    ])
    print(cookies)
    return cookies


def cookies_dict2str(cookies: dict[str, str]) -> str:
    """
    将 cookies 字典转换为字符串格式

    - cookies: 字典格式的 cookies
    """
    return "; ".join([f"{k}={v}" for k, v in cookies.items()]) + ";"


def aes_encrypt(
    data: str,
    key: str,
    iv: str | None = None,
    mode: str = "ECB",
) -> str:
    """
    AES 加密, ECB 模式下 iv 无效

    - data: 数据
    - key: 密钥
    - iv: 向量
    - mode: 模式, 支持 "ECB", "CBC", "CFB", "OFB", "CTR"
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from base64 import b64encode

    if iv:
        cipher = AES.new(
            key.encode(),
            getattr(AES, f"MODE_{mode}"),
            iv=iv.encode(),
        )
    else:
        cipher = AES.new(
            key.encode(),
            getattr(AES, f"MODE_{mode}"),
        )
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return b64encode(ct_bytes).decode()


def aes_decrypt(
    data: str,
    key: str,
    iv: str | None = None,
    mode: str = "ECB",
) -> str:
    """
    AES 解密, ECB 模式下 iv 无效

    - data: 数据
    - key: 密钥
    - iv: 向量
    - mode: 模式, 支持 "ECB", "CBC", "CFB", "OFB", "CTR"
    """
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    from base64 import b64decode

    if iv:
        cipher = AES.new(
            key.encode(),
            getattr(AES, f"MODE_{mode}"),
            iv=iv.encode(),
        )
    else:
        cipher = AES.new(
            key.encode(),
            getattr(AES, f"MODE_{mode}"),
        )
    pt = unpad(cipher.decrypt(b64decode(data)), AES.block_size)
    return pt.decode()


def aes_keygen(key_size: int = 16, upper: bool = False, type: str = "hex") -> str:
    """
    AES 密钥生成, 返回密钥

    - key_size: 密钥长度, 默认为 16
    - upper: 是否大写, 默认为 False
    - type: 密钥类型, 支持 "hex", "base64"
    """
    from Crypto.Random import get_random_bytes
    from base64 import b64encode

    key = get_random_bytes(key_size)
    if type == "hex":
        new_key = key.hex()
    elif type == "base64":
        new_key = b64encode(key).decode()
    else:
        raise Exception("密钥类型错误")
    if upper:
        return new_key.upper()
    return new_key


def rsa_encrypt(data: str, key: str) -> str:
    """
    RSA 公钥加密

    - data: 数据
    - key: 公钥
    """
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    from base64 import b64encode

    RsaKey = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(RsaKey)
    cipher_text = b64encode(cipher.encrypt(data.encode())).decode()
    return cipher_text


def rsa_decrypt(data: str, key: str) -> str:
    """
    RSA 私钥解密

    - data: 数据
    - key: 私钥
    """
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    import base64

    key = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(key)
    text = cipher.decrypt(base64.b64decode(data), None)
    return text.decode()


def rsa_keygen(key_size: int = 1024) -> list[str, str]:
    """
    RSA 密钥生成, 返回公钥和私钥

    - key_size: 密钥长度, 默认为 1024
    """
    from Crypto.PublicKey import RSA

    key = RSA.generate(key_size)
    private_key = key.exportKey()
    public_key = key.publickey().exportKey()
    return [public_key.decode(), private_key.decode()]


def iter_cycle(iterable):
    """
    循坏迭代列表

    - iterable: 可迭代对象
    >>> c = iter_cycle([1, 2, 3])
    >>> next(c) # 1
    """
    from itertools import cycle

    return cycle(iterable)


def iter_product(*iterables, repeat=1):
    """
    笛卡尔积迭代器

    - iterables: 可迭代对象
    >>> c = iter_product([1, 2, 3], repeat=2)
    >>> next(c) # (1, 1)
    >>> d = iter_product([1, 2], [3, 4])
    >>> list(d) # [(1, 3), (1, 4), (2, 3), (2, 4)]
    """
    from itertools import product

    return product(*iterables, repeat=repeat)


def iter_permutations(iterable, r=None):
    """
    根据 iterable 返回连续的 r 长度 元素的排列。

    - iterable: 可迭代对象
    - r: 如果 r 未指定或为 None ，r 默认设置为 iterable 的长度，这种情况下，生成所有全长排列。

    >>> c = iter_permutations([1, 2, 3])
    >>> next(c) # (1, 2, 3)
    """
    from itertools import permutations

    return permutations(iterable, r)


def iter_flatten(iterable):
    """
    展开列表, 支持嵌套列表

    - iterable: 可迭代对象
    """
    from itertools import chain

    return chain.from_iterable(iterable)


def func_kv(func, key, default=None):
    """
    函数属性字典, 只能设置一次, 之后通过 func.key 获取和修改

    - func: 函数
    - key: 键
    - default: 默认值
    >>> def hello_world():
    ...    kv = func_kv(hello_world, "kv", {})
    ...    print(kv) # {}
    ...    kv["hello"] = "world"
    ...    print(kv) # {"hello": "world"}
    >>> hello_world()
    """
    if hasattr(func, key):
        done_dict = getattr(func, key)
    else:
        setattr(func, key, default)
        done_dict = getattr(func, key)
    return done_dict


def random_str(length: int = 16, prefix="", suffix="") -> str:
    """
    随机生成字符串
    - length: 长度
    - prefix: 前缀
    - suffix: 后缀
    """
    import random

    chars = "".join(
        random.sample(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            length,
        )
    )
    return prefix + chars + suffix


def set_title(title: str):
    """
    设置控制台标题

    - title: 标题
    """
    from builtins import print

    print(f"\x1b]0;{title}\x07")


def re_first(pattern, string, default="", flags=0):
    """
    正则匹配第一个

    - pattern: 正则表达式
    - string: 字符串
    - default: 默认值
    - flags: 正则表达式标志, 也支持字符串格式, 如 "I", "A", "S", "M" 等。
    """
    import re

    if flags and isinstance(flags, str):
        flags = getattr(re, flags)
    return next(iter(re.findall(pattern, string, flags)), default)


def jsonpath_first(obj, expr, default=""):
    """
    尝试获取字典数据, 失败返回默认值, 基于 jsonpath 实现。

    obj: 目标对象
    expr: 表达式
    default: 默认值
    """
    try:
        result = jsonpath(obj, expr)
        return result[0] if result and (result[0] or result[0] == 0) else default
    except Exception:
        return default


try_get = jsonpath_first


def moviepy_video(filepath):
    """
    通过 MoviePy 处理视频文件

    - filepath: 文件路径
    """
    from moviepy import VideoFileClip

    return VideoFileClip(filepath)


def moviepy_audio(filepath):
    """
    通过 MoviePy 处理音频文件

    - filepath: 文件路径
    """
    from moviepy import AudioFileClip

    return AudioFileClip(filepath)


def open_url(url, browser=None):
    """
    打开 URL

    - url: URL链接
    - browser: 浏览器名称或路径, 名称支持 chrome、firefox、edge.
        - chrome默认路径为 'C:/Program Files/Google/Chrome/Application/chrome.exe'，
        - firefox 浏览器默认路径为 'C:/Program Files/Mozilla Firefox/firefox.exe'
        - edge 浏览器默认路径为 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
    """
    import webbrowser
    import os

    if browser:
        if browser == "chrome":
            browser_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        elif browser == "firefox":
            browser_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
        elif browser == "edge":
            browser_path = (
                "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
            )
        else:
            browser_path = browser
        if not os.path.exists(browser_path):
            raise Exception("浏览器路径不存在，请检查路径是否正确")
        webbrowser.register(
            "custom_browser", None, webbrowser.BackgroundBrowser(browser_path)
        )
        webbrowser.get("custom_browser").open(url)
    else:
        webbrowser.open(url)


def copy_text(text):
    """
    复制文本到剪贴板

    - text: 文本
    """
    import pyperclip

    pyperclip.copy(text)


def paste_text():
    """
    从剪贴板获取文本
    """
    import pyperclip

    return pyperclip.paste()


def zip_file(filepath, zipname):
    """
    将文件或文件夹压缩为 zip 格式
    - filepath: 文件路径, 可以是文件路径或文件夹路径
    - zipname: 压缩文件名
    """
    import zipfile

    with zipfile.ZipFile(zipname, "w") as f:
        if os.path.isfile(filepath):
            f.write(filepath)
        else:
            for root, dirs, files in os.walk(filepath):
                for file in files:
                    f.write(os.path.join(root, file))


def unzip_file(zipname, path=None):
    """
    解压 zip 文件
    - zipname: 压缩文件名
    - path: 解压路径, 默认为当前路径
    """
    import zipfile

    with zipfile.ZipFile(zipname, "r") as f:
        f.extractall(path=path)


def time_fmt(timestring, fmt="%Y-%m-%d %H:%M:%S", out_fmt="%Y-%m-%d %H:%M:%S"):
    """
    时间格式化
    - timestring: 时间字符串 或 datetime 对象
    - fmt: 输入时间字符串的格式, strptime 驱动
    - out_fmt: 输出时间字符串的格式, strftime 驱动
    """
    import datetime

    if isinstance(timestring, str):
        timestring = datetime.datetime.strptime(timestring, fmt)
        return timestring.strftime(out_fmt)
    elif isinstance(timestring, (datetime.datetime, datetime.date)):
        return timestring.strftime(out_fmt)
    else:
        raise timestring


def which(cmd):
    """
    查找命令的路径
    - cmd: 命令
    """
    import shutil

    return shutil.which(cmd)


def move_file(src, dst):
    """
    移动文件, 支持文件和文件夹
    - src: 源文件路径
    - dst: 目标文件路径
    """
    import shutil

    shutil.move(src, dst)


def copy_file(src, dst):
    """
    复制文件, 支持文件和文件夹

    - src: 源文件路径
    - dst: 目标文件路径
    """
    import shutil
    import os

    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy(src, dst)


def remove_file(filepath):
    """
    删除文件, 支持文件和文件夹

    - filepath: 文件路径
    """
    import shutil
    import os

    if os.path.isfile(filepath):
        os.remove(filepath)
    else:
        shutil.rmtree(filepath)


def unpack_archive(
    filepath: str,
    dst: str | None = None,
    format: str | None = None,
    filter=None,
):
    """
    解压文件, 支持 zip、tar、gz、bz2、xz 格式

    - filepath: 文件路径, 可以是文件路径或文件夹路径
    - dst: 目标路径, 可以是文件夹路径, 默认为当前路径
    - format: 压缩格式, 默认为 None, 自动识别, 支持 zip、tar、gz、bz2、xz 格式
    """
    import shutil

    shutil.unpack_archive(filepath, dst, format, filter=filter)


def make_archive(base_name, format, root_dir, **kwargs):
    """
    压缩文件, 支持 zip、tar、gz、bz2、xz 格式

    - base_name: 压缩文件名
    - format: 压缩格式
    - root_dir: 压缩文件路径
    - kwargs: 其他参数, 如 base_dir、verbose、exclude、dry_run、owner、group、logger
    """
    import shutil

    shutil.make_archive(base_name, format, root_dir, **kwargs)
