import os
import uuid
import json
import random
import ddddocr
import matplotlib
from PIL import Image
from io import BytesIO
from jinja2 import Template
import matplotlib.pyplot as plt
from importlib import resources
from typing import Optional, Tuple, TypeVar, List, Any, Literal, Union

from spiderpy3.utils.image import base64_to_file_ext, base64_to_bytes
from spiderpy3.utils.verify.sdk.cBezier import bezierTrajectory
from spiderpy3.utils.execute.js import execute_js_code_by_execjs
from spiderpy3.utils.tools import get_random_pick


def get_double_image_slide_distance(
        image1_base64: str,
        image2_base64: str,
        image1_render_width: int,
        image_dir_path: Optional[str] = None
) -> int:
    """
    获取双图滑动距离

    :param image1_base64: 背景图片 base64 字符串
    :param image2_base64: 滑块图片 base64 字符串
    :param image1_render_width: 背景图片 (渲染宽度)
    :param image_dir_path: 图片保存目录
    :return: 滑块图片 在 背景图片 上需要滑动的距离 (计算渲染后滑动的距离)
    """
    name = str(uuid.uuid1()).replace("-", "")

    image1_file_name = f"image1-{name}.{base64_to_file_ext(image1_base64, default='png')}"
    image2_file_name = f"image2-{name}.{base64_to_file_ext(image2_base64, default='png')}"

    image1_file_path = os.path.join(image_dir_path, image1_file_name) if image_dir_path else None
    image2_file_path = os.path.join(image_dir_path, image2_file_name) if image_dir_path else None

    image1_bytes = base64_to_bytes(image1_base64, image1_file_path)
    image2_bytes = base64_to_bytes(image2_base64, image2_file_path)

    det = ddddocr.DdddOcr(ocr=False, det=False, show_ad=False)
    res = det.slide_match(image2_bytes, image1_bytes, simple_target=True)
    x = res["target"][0]

    image1_origin_width = Image.open(BytesIO(image1_bytes)).size[0]
    x *= (image1_render_width / image1_origin_width)
    slide_distance = round(x)

    return slide_distance


X = TypeVar("X", bound=int)
Y = TypeVar("Y", bound=int)

SlidePoint = Tuple[X, Y]
SlidePoints = List[SlidePoint]
SlideMode = Literal["bezier_curve", "ghost_cursor"]


def get_slide_points_by_bessel_function(slide_distance: int, **kwargs: Any) -> SlidePoints:
    bt = bezierTrajectory()
    kw = {
        "numberList": random.randint(25, 45),
        "le": 4,
        "deviation": 10,
        "bias": 0.5,
        "type": 2,
        "cbb": 1,
        "yhh": 5
    }
    """
    numberList: 返回的数组的轨迹点的数量 numberList = 150
    le: 几阶贝塞尔曲线，越大越复杂 如 le = 4
    deviation: 轨迹上下波动的范围 如 deviation = 10
    bias: 波动范围的分布位置 如 bias = 0.5
    type: 0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type = 1
    cbb: 在终点来回摆动的次数
    yhh: 在终点来回摆动的范围
    """
    kw.update(kwargs)
    result = bt.trackArray([0, 0], [slide_distance, 0], **kw)
    result = result["trackArray"].tolist()
    slide_points = [(round(i[0]), round(i[1])) for i in result]
    return slide_points


def get_slide_points_by_ghost_cursor(slide_distance: int, **_kwargs: Any) -> SlidePoints:
    """
    npm install -g ghost-cursor

    :param slide_distance:
    :param _kwargs:
    :return:
    """
    js_code = '''function sdk(from,to){const{path}=require("ghost-cursor");return path(from,to,{useTimestamps:false})}'''  # noqa
    result = execute_js_code_by_execjs(
        js_code=js_code, func_name="sdk",
        func_args=({"x": 0, "y": 0}, {"x": slide_distance, "y": 0})
    )
    slide_points = [(round(i["x"]), round(i["y"])) for i in result]
    return slide_points


def get_slide_points(slide_distance: int, slide_mode: SlideMode = "bezier_curve", **kwargs: Any) -> SlidePoints:
    if slide_mode == "bezier_curve":
        slide_points = get_slide_points_by_bessel_function(slide_distance, **kwargs)
    elif slide_mode == "ghost_cursor":
        slide_points = get_slide_points_by_ghost_cursor(slide_distance, **kwargs)
    else:
        raise ValueError(f"不支持的 slide_mode：{slide_mode}！")
    return slide_points


T = TypeVar("T", bound=int)

TimeInterval = Union[int, Tuple[int, int]]
SlideTrajectory = Tuple[X, Y, T]
SlideTrajectories = List[SlideTrajectory]


def get_format_slide_trajectories(
        slide_trajectories: SlideTrajectories,
        x_offset: bool,
        y_offset: bool,
        t_offset: bool,
        t_divide_by_1000: bool
) -> SlideTrajectories:
    format_slide_trajectories = []
    current_x, current_y, current_t = 0, 0, 0
    for slide_trajectory in slide_trajectories:
        x, y, t = slide_trajectory
        if x_offset is True:
            offset_x = x - current_x
            current_x = x
            x = offset_x
        if y_offset is True:
            offset_y = y - current_y
            current_y = y
            y = offset_y
        if t_offset is True:
            offset_t = t - current_t
            current_t = t
            t = offset_t
        format_slide_trajectory = (x, y, t)
        format_slide_trajectories.append(format_slide_trajectory)

    if t_divide_by_1000 is True:
        format_slide_trajectories = list(
            map(lambda _: (_[0], _[1], float(f"{_[2] / 1e3:.2f}")), format_slide_trajectories)
        )

    return format_slide_trajectories


def get_slide_trajectories_by_slide_points(slide_points: SlidePoints, time_interval: TimeInterval) -> SlideTrajectories:
    slide_trajectories = []
    t = 0
    for slide_point in slide_points:
        x, y = slide_point

        if isinstance(time_interval, int):
            t += time_interval
        else:
            if isinstance(time_interval, tuple) and len(time_interval) == 2:
                if all(map(lambda _: isinstance(_, int), time_interval)):
                    t += random.randint(*time_interval)
                else:
                    raise ValueError(f"不支持的 time_interval：{time_interval}！")
            else:
                raise ValueError(f"不支持的 time_interval：{time_interval}！")

        slide_trajectory = (x, y, t)
        slide_trajectories.append(slide_trajectory)
    return slide_trajectories


def get_slide_trajectories_by_resources(slide_distance: int) -> SlideTrajectories:
    package = f"spiderpy3.resources.{__name__}"
    resources_list = resources.contents(package)

    if not hasattr(get_slide_trajectories_by_resources, "pick"):
        data = []
        for resource in resources_list:
            with resources.open_text(package, resource) as file:
                content = file.read()
                item = json.loads(content)
                data.append(item)
        setattr(get_slide_trajectories_by_resources, "pick", get_random_pick(data))

    pick = getattr(get_slide_trajectories_by_resources, "pick")

    item = pick()

    manual_slide_trajectories = []
    start_x, start_y, start_t = 0, 0, 0
    for idx, i in enumerate(item["slideTrajectories"]):
        if idx == 0:
            x = 0
            y = 0
            t = 0
            start_x = i["x"]
            start_y = i["y"]
            start_t = i["t"]
        else:
            x = i["x"] - start_x
            y = i["y"] - start_y
            t = i["t"] - start_t
        manual_slide_trajectories.append((x, y, t))

    rate = slide_distance / item["slideDistance"]

    # slide_trajectories = [(round(m[0] * rate), round(m[1]), round(m[2] * rate)) for m in manual_slide_trajectories]
    slide_trajectories = [(round(m[0] * rate), round(m[1]), m[2]) for m in manual_slide_trajectories]
    return slide_trajectories


def get_slide_js(selector: str, slide_trajectories: SlideTrajectories) -> str:
    template = Template("""function sdk (selector, slideTrajectories) {
  const element = document.querySelector(selector);

  let accumulatedTime = 0;

  for (let i = 0; i < slideTrajectories.length; i++) {
    const [x, y, t] = slideTrajectories[i];

    accumulatedTime += t;

    let type;
    if (i === 0) {
      type = "mousedown";
    } else if (i !== slideTrajectories.length - 1) {
      type = "mousemove";
    } else {
      type = "mouseup";
    }

    function triggerMouseEvent (element, type, x, y) {
      const event = new MouseEvent(type, {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: x,
        clientY: y,
      });
      element.dispatchEvent(event);
    }

    setTimeout(() => { triggerMouseEvent(element, type, x, y); }, accumulatedTime);
  }
}

sdk("{{ selector }}", {{ slideTrajectories }});""")
    slide_js = template.render(selector=selector, slideTrajectories=json.loads(json.dumps(slide_trajectories)))
    return slide_js


def plot_slide_trajectories(
        slide_trajectories: SlideTrajectories,
        show: bool = False,
        save: bool = False,
        save_file_path: Optional[str] = None
) -> None:
    matplotlib.use("TkAgg")

    xs = list(map(lambda _: _[0], slide_trajectories))
    ys = list(map(lambda _: _[1], slide_trajectories))
    ts = list(map(lambda _: _[2], slide_trajectories))

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.plot(xs, ys, color="red")
    plt.title("xy")
    plt.xlabel("x axis")
    plt.ylabel("y axis")

    plt.subplot(2, 2, 3)
    plt.plot(ts, xs, color="red")
    plt.title("tx")
    plt.xlabel("t axis")
    plt.ylabel("x axis")

    plt.subplot(2, 2, 4)
    plt.plot(ts, ys, color="red")
    plt.title("ty")
    plt.xlabel("t axis")
    plt.ylabel("y axis")

    if show is True:
        plt.show()

    if save is True and save_file_path is not None:
        plt.savefig(save_file_path)


if __name__ == '__main__':
    def run():
        slide_distance = get_double_image_slide_distance(
            'data:image/jpg;base64,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',
            'data:image/png;base64,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',
            290
        )
        print(slide_distance)

        slide_points1 = get_slide_points_by_bessel_function(slide_distance)
        slide_points2 = get_slide_points_by_ghost_cursor(slide_distance)
        print(slide_points1)
        print(slide_points2)

        slide_trajectories1 = get_slide_trajectories_by_slide_points(
            slide_points1,
            time_interval=(5, 10)
        )
        print(slide_trajectories1)

        # slide_trajectories2 = get_slide_trajectories_by_resources(slide_distance)
        # print(slide_trajectories2)

        format_slide_trajectories1 = get_format_slide_trajectories(slide_trajectories1, False, False, True, False)
        slide_js = get_slide_js("#captcha_modal > div > div.captcha_footer > div > img", format_slide_trajectories1)
        print(slide_js)

        plot_slide_trajectories(slide_trajectories1, show=True)


    run()
