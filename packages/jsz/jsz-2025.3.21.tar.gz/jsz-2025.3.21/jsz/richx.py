from rich import print_json, inspect, print


__all__ = [
    "inspect",
    "pprint",
    "print",
    "printx",
    "print_json",
    "rich_columns",
    "rich_markdown",
    "rich_panel",
    "rich_padding",
    "rich_rule",
    "status",
    "track",
]

ANSI_COLOR_NAMES = [
    # "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
    # "grey0",
    # "gray0",
    # "navy_blue",
    # "dark_blue",
    "blue3",
    "blue1",
    "dark_green",
    "deep_sky_blue4",
    "dodger_blue3",
    "dodger_blue2",
    "green4",
    "spring_green4",
    "turquoise4",
    "deep_sky_blue3",
    "dodger_blue1",
    "green3",
    "spring_green3",
    "dark_cyan",
    "light_sea_green",
    "deep_sky_blue2",
    "deep_sky_blue1",
    "spring_green2",
    "cyan3",
    "dark_turquoise",
    "turquoise2",
    "green1",
    "spring_green1",
    "medium_spring_green",
    "cyan2",
    "cyan1",
    "dark_red",
    "deep_pink4",
    "purple4",
    "purple3",
    "blue_violet",
    "orange4",
    "grey37",
    "gray37",
    "medium_purple4",
    "slate_blue3",
    "royal_blue1",
    "chartreuse4",
    "dark_sea_green4",
    "pale_turquoise4",
    "steel_blue",
    "steel_blue3",
    "cornflower_blue",
    "chartreuse3",
    "cadet_blue",
    "sky_blue3",
    "steel_blue1",
    "pale_green3",
    "sea_green3",
    "aquamarine3",
    "medium_turquoise",
    "chartreuse2",
    "sea_green2",
    "sea_green1",
    "aquamarine1",
    "dark_slate_gray2",
    "dark_magenta",
    "dark_violet",
    "purple",
    "light_pink4",
    "plum4",
    "medium_purple3",
    "slate_blue1",
    "yellow4",
    "wheat4",
    "grey53",
    "gray53",
    "light_slate_grey",
    "light_slate_gray",
    "medium_purple",
    "light_slate_blue",
    "dark_olive_green3",
    "dark_sea_green",
    "light_sky_blue3",
    "sky_blue2",
    "dark_sea_green3",
    "dark_slate_gray3",
    "sky_blue1",
    "chartreuse1",
    "light_green",
    "pale_green1",
    "dark_slate_gray1",
    "red3",
    "medium_violet_red",
    "magenta3",
    "dark_orange3",
    "indian_red",
    "hot_pink3",
    "medium_orchid3",
    "medium_orchid",
    "medium_purple2",
    "dark_goldenrod",
    "light_salmon3",
    "rosy_brown",
    "grey63",
    "gray63",
    "medium_purple1",
    "gold3",
    "dark_khaki",
    "navajo_white3",
    "grey69",
    "gray69",
    "light_steel_blue3",
    "light_steel_blue",
    "yellow3",
    "dark_sea_green2",
    "light_cyan3",
    "light_sky_blue1",
    "green_yellow",
    "dark_olive_green2",
    "dark_sea_green1",
    "pale_turquoise1",
    "deep_pink3",
    "magenta2",
    "hot_pink2",
    "orchid",
    "medium_orchid1",
    "orange3",
    "light_pink3",
    "pink3",
    "plum3",
    "violet",
    "light_goldenrod3",
    "tan",
    "misty_rose3",
    "thistle3",
    "plum2",
    "khaki3",
    "light_goldenrod2",
    "light_yellow3",
    "grey84",
    "gray84",
    "light_steel_blue1",
    "yellow2",
    "dark_olive_green1",
    "honeydew2",
    "light_cyan1",
    "red1",
    "deep_pink2",
    "deep_pink1",
    "magenta1",
    "orange_red1",
    "indian_red1",
    "hot_pink",
    "dark_orange",
    "salmon1",
    "light_coral",
    "pale_violet_red1",
    "orchid2",
    "orchid1",
    "orange1",
    "sandy_brown",
    "light_salmon1",
    "light_pink1",
    "pink1",
    "plum1",
    "gold1",
    "navajo_white1",
    "misty_rose1",
    "thistle1",
    "yellow1",
    "light_goldenrod1",
    "khaki1",
    "wheat1",
    "cornsilk1",
    "grey100",
    "gray100",
    # "grey3",
    # "gray3",
    # "grey7",
    # "gray7",
    # "grey11",
    # "gray11",
    # "grey15",
    # "gray15",
    # "grey19",
    # "gray19",
    # "grey23",
    # "gray23",
    # "grey27",
    # "gray27",
    # "grey30",
    # "gray30",
    # "grey35",
    # "gray35",
    "grey39",
    "gray39",
    "grey42",
    "gray42",
    "grey46",
    "gray46",
    "grey50",
    "gray50",
    "grey54",
    "gray54",
    "grey58",
    "gray58",
    "grey62",
    "gray62",
    "grey66",
    "gray66",
    "grey70",
    "gray70",
    "grey74",
    "gray74",
    "grey78",
    "gray78",
    "grey82",
    "gray82",
    "grey85",
    "gray85",
    "grey89",
    "gray89",
    "grey93",
    "gray93",
]


def printx(
    *objects,
    sep: str = " ",
    end: str = "\n",
    file=None,
    flush=True,
    style: str | None = None,
    justify: str | None = None,
    overflow: str | None = None,
    no_wrap: bool | None = None,
    emoji: bool | None = None,
    markup: bool | None = None,
    highlight: bool | None = None,
    width: int | None = None,
    height: int | None = None,
    crop: bool = True,
    soft_wrap: bool | None = None,
    new_line_start: bool = False,
):
    """
    增加随机颜色的print, 支持富文本


    - sep: 分隔符
    - end: 结尾
    - file: 文件
    - flush: 是否刷新, 默认是,不支持修改
    - style: 样式
    - justify: 对齐方式, 支持 "left", "center", "right", 默认是 None
    - overflow: 溢出方式, 支持 "fold", "crop", "ellipsis", 默认是 None
    - no_wrap: 是否不换行
    - emoji: 是否支持 emoji
    - markup: 是否支持 markup
    - highlight: 是否支持 highlight
    - width: 宽度
    - height: 高度
    - crop: 是否裁剪
    - soft_wrap: 是否软换行
    - new_line_start: 是否换行开始
    """
    import random
    from rich.console import Console

    console = Console(file=file) if file else Console()
    console.print(
        *(
            [
                (
                    f"[{random.choice(ANSI_COLOR_NAMES)}]{i}[/]"
                    if isinstance(i, str)
                    else i
                )
                for i in objects
            ]
            if not style
            else objects
        ),
        sep=sep,
        end=end,
        style=style,
        justify=justify,
        overflow=overflow,
        no_wrap=no_wrap,
        emoji=emoji,
        markup=markup,
        highlight=highlight,
        width=width,
        height=height,
        crop=crop,
        soft_wrap=soft_wrap,
        new_line_start=new_line_start,
    )


def rich_panel(
    renderable,
    title=None,
    title_align="center",
    subtitle=None,
    subtitle_align="center",
    safe_box=None,
    expand=False,
    style="none",
    border_style="none",
    width=None,
    height=None,
    padding=(0, 1),
    highlight=False,
):
    """
    rich panel 封装

    - renderable: 渲染对象
    - title: 标题
    - title_align: 标题对齐方式
    - subtitle: 副标题
    - safe_box: 安全盒子
    - expand: 是否展开, 默认不展开
    - style: 样式
    - border_style: 边框样式
    - width: 宽度
    - height: 高度
    - padding: 内边距
    - highlight: 是否高亮
    """
    from rich.panel import Panel

    return Panel(
        renderable=renderable,
        title=title,
        title_align=title_align,
        subtitle=subtitle,
        subtitle_align=subtitle_align,
        safe_box=safe_box,
        expand=expand,
        style=style,
        border_style=border_style,
        width=width,
        height=height,
        padding=padding,
        highlight=highlight,
    )


def rich_rule(
    title="",
    *,
    characters: str = "─",
    style: str = "rule.line",
    end: str = "\n",
    align: str = "center",
) -> None:
    """
    绘制一条线，可选择带有居中文本的标题。

    - title (str, 可选): 在线条上方渲染的文本。默认为 ""。
    - characters (str, 可选): 用于组成线条的字符。默认为 "─"。
    - style (str, 可选): 线条样式。默认为 "rule.line"。
    - align (str, 可选): 标题的对齐方式，可为 "left"、"center" 或 "right"。默认为 "center"。
    """
    from rich.rule import Rule
    from rich import print

    print(
        Rule(
            title=title,
            characters=characters,
            style=style,
            end=end,
            align=align,
        )
    )


def status(
    status="正在处理...",
    *,
    spinner: str = "dots",
    spinner_style="status.spinner",
    speed: float = 1.0,
    refresh_per_second: float = 12.5,
):
    """
    ## 显示进度，动画效果，基于 rich status 封装

    - status: 标题
    - spinner: 动画类型, random 为随机选择, 其他好看的样式有 "aesthetic", "weather", "moon", "earth", "clock", "bouncingBar", "line", "growHorizontal", "arrow2" 等。
    - spinner_style: 动画样式
    - speed: 动画速度
    - refresh_per_second: 每秒刷新次数, 默认为 12.5

    ```py
    import jsz

    with jsz.status():
        jsz.sleep(3)
        jsz.print("下载完成")
    ```
    """
    from rich.status import Status

    if spinner == "random":
        import random
        from rich.spinner import SPINNERS

        spinner = random.choice(list(SPINNERS))

    status_renderable = Status(
        status,
        spinner=spinner,
        spinner_style=spinner_style,
        speed=speed,
        refresh_per_second=refresh_per_second,
    )
    return status_renderable


def rich_padding(
    renderable,
    pad=(0, 0, 0, 0),
    style="none",
    expand=True,
):
    """
    给renderable对象添加padding

    - renderable: 渲染对象
    - pad: padding 大小
    - style: padding 样式
    - expand: 是否展开
    """
    from rich.padding import Padding

    return Padding(
        renderable,
        pad=pad,
        style=style,
        expand=expand,
    )


def rich_columns(
    renderables=None,
    padding=(0, 1),
    width=None,
    expand=False,
    equal=False,
    column_first=False,
    right_to_left=False,
    align=None,
    title=None,
):
    """
    rich 自定义列

    - renderables: 渲染对象
    - padding: padding 大小
    - width: 列宽
    - expand: 是否展开
    - equal: 是否相等
    - column_first: 列优先
    - right_to_left: 从右到左
    - align: 对齐方式
    - title: 标题
    """
    from rich.columns import Columns

    return Columns(
        renderables=renderables,
        padding=padding,
        width=width,
        expand=expand,
        equal=equal,
        column_first=column_first,
        right_to_left=right_to_left,
        align=align,
        title=title,
    )


def rich_markdown(
    markup,
    code_theme="monokai",
    justify=None,
    style="none",
    hyperlinks=True,
    inline_code_lexer=None,
    inline_code_theme=None,
):
    """
    显示 Markdown 文本

    - markup: Markdown 文本
    - code_theme: 代码块主题
    - justify: 文本对齐方式
    - style: 样式
    - hyperlinks: 是否启用超链接
    - inline_code_lexer: 内联代码词法分析器
    - inline_code_theme: 内联代码主题
    """
    from rich.markdown import Markdown

    return Markdown(
        markup=markup,
        code_theme=code_theme,
        justify=justify,
        style=style,
        hyperlinks=hyperlinks,
        inline_code_lexer=inline_code_lexer,
        inline_code_theme=inline_code_theme,
    )


def pprint(
    obj,
    console=None,
    indent_guides: bool = True,
    max_length: int | None = None,
    max_string: int | None = None,
    max_depth: int | None = None,
    expand_all: bool = False,
):
    """
    rich 美化打印对象

    - obj: 打印对象
    - console: 控制台
    - indent_guides: 是否启用缩进指南
    - max_length: 最大长度
    - max_string: 最大字符串
    - max_depth: 最大深度
    - expand_all: 是否展开所有对象
    """
    from rich.pretty import pprint

    pprint(
        obj,
        console=console,
        indent_guides=indent_guides,
        max_length=max_length,
        max_string=max_string,
        max_depth=max_depth,
        expand_all=expand_all,
    )


def track(
    sequence,
    description="正在处理...",
    total=None,
    auto_refresh=True,
    console=None,
    transient=False,
    get_time=None,
    refresh_per_second=10,
    style="bar.back",
    complete_style="bar.complete",
    finished_style="bar.finished",
    pulse_style="bar.pulse",
    update_period=0.1,
    disable=False,
    show_speed=True,
):
    """
    进度条, 封装 rich 的 track

    - sequence: 序列
    - description: 描述
    - total: 总数
    - auto_refresh: 是否自动刷新
    - console: 控制台
    - transient: 是否瞬态
    - get_time: 获取时间
    - refresh_per_second: 每秒刷新次数
    - style: 样式
    - complete_style: 完成样式
    - finished_style: 完成样式
    - pulse_style: 脉冲样式
    - update_period: 更新周期
    - disable: 是否禁用
    - show_speed: 是否显示速度

    >>> import jsz
    >>> for i in jsz.track(range(10)):
    >>>     jsz.print(i)
    >>>     jsz.sleep(0.2)
    """
    from rich.progress import track

    return track(
        sequence=sequence,
        description=description,
        total=total,
        auto_refresh=auto_refresh,
        console=console,
        transient=transient,
        get_time=get_time,
        refresh_per_second=refresh_per_second,
        style=style,
        complete_style=complete_style,
        finished_style=finished_style,
        pulse_style=pulse_style,
        update_period=update_period,
        disable=disable,
        show_speed=show_speed,
    )
