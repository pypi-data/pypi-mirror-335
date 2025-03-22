import os
import re
import json
import base64
import asyncio
import random
import nonebot
import traceback
import aiohttp
import filetype
import ssl
import qrcode
import socket
import time

from urllib.parse import urlparse
from aiohttp import TCPConnector
from nonebot import logger
from ..config import config, PLUGIN_DIR, BACKEND_URL_LIST
from ..exceptions import ComfyuiExceptions
from ..parser import comfyui_parser

from io import BytesIO
from PIL import Image
from asyncio import get_running_loop
from nonebot_plugin_alconna import UniMessage
from jinja2 import Environment, FileSystemLoader

cd = {}
daily_calls = {}
PLUGIN_VERSION = '0.8'


async def run_later(func, delay=1):
    loop = get_running_loop()
    loop.call_later(
        delay,
        lambda: loop.create_task(
            func
        )
    )


async def set_res(new_img: Image) -> str:
    if config.comfyui_audit_comp:
        max_res = 640
        old_res = new_img.width * new_img.height
        width = new_img.width
        height = new_img.height

        if old_res > pow(max_res, 2):
            if width <= height:
                ratio = height / width
                width: float = max_res / pow(ratio, 0.5)
                height: float = width * ratio
            else:
                ratio = width / height
                height: float = max_res / pow(ratio, 0.5)
                width: float = height * ratio
            logger.info(f"审核图片尺寸已调整至{round(width)}x{round(height)}")
            new_img.resize((round(width), round(height)))

    img_bytes = BytesIO()
    new_img.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64


async def pic_audit_standalone(
        img_base64,
        is_return_tags=False,
        audit=False,
        return_bool=False
):

    byte_img = (
        img_base64 if isinstance(img_base64, bytes)
        else base64.b64decode(img_base64)
    )
    img = Image.open(BytesIO(byte_img)).convert("RGB")
    img_base64 = await set_res(img)

    async def get_caption(payload):

        if config.comfyui_audit_local:
            from .wd_audit import tagger_main
            from .. import wd_instance
            resp_dict = {}
            caption = await asyncio.get_event_loop().run_in_executor(
                None,
                tagger_main,
                payload['image'],
                payload['threshold'],
                wd_instance
            )
            resp_dict["caption"] = caption
            return resp_dict

        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=f"{config.comfyui_audit_site}/tagger/v1/interrogate",
                        json=payload
                ) as resp:

                    if resp.status not in [200, 201]:
                        resp_text = await resp.text()
                        logger.error(f"API失败，错误信息:{resp.status, resp_text}")
                        return None
                    resp_dict = await resp.json()
                    return resp_dict

    payload = {"image": img_base64, "model": "wd14-vit-v2-git", "threshold": 0.35}
    resp_dict = await get_caption(payload)

    tags = resp_dict["caption"]
    replace_list = ["general", "sensitive", "questionable", "explicit"]
    to_user_list = ["这张图很安全!", "较为安全", "色情", "泰色辣!"]
    possibilities = {}
    to_user_dict = {}
    message = "这是审核结果:\n"

    for i, to_user in zip(replace_list, to_user_list):
        possibilities[i] = tags[i]
        percent = f":{tags[i] * 100:.2f}".rjust(6)
        message += f"[{to_user}{percent}%]\n"
        to_user_dict[to_user] = tags[i]

    value = list(to_user_dict.values())
    value.sort(reverse=True)
    reverse_dict = {value: key for key, value in to_user_dict.items()}
    message += f"最终结果为:{reverse_dict[value[0]].rjust(5)}"

    if return_bool:
        value = list(possibilities.values())
        value.sort(reverse=True)
        reverse_dict = {value: key for key, value in possibilities.items()}
        logger.info(message)
        if config.comfyui_audit_level == 1:
            return True if reverse_dict[value[0]] == "explicit" else False
        elif config.comfyui_audit_level == 2:
            return True if reverse_dict[value[0]] == "questionable" or reverse_dict[value[0]] == "explicit" else False
        elif config.comfyui_audit_level == 3:
            return True if (
                    reverse_dict[value[0]] == "questionable" or
                    reverse_dict[value[0]] == "explicit" or
                    reverse_dict[value[0]] == "sensitive"
            ) else False
        elif config.comfyui_audit_level == 100:
            return True

    if is_return_tags:
        return message, tags
    if audit:
        return possibilities, message
    return message


async def send_msg_and_revoke(message: UniMessage | str, reply_to=False, r=None):
    if isinstance(message, str):
        message = UniMessage(message)

    async def main(message, reply_to, r):
        if r:
            await revoke_msg(r)
        else:
            r = await message.send(reply_to=reply_to)
            await revoke_msg(r)
        return

    await run_later(main(message, reply_to, r), 2)


async def revoke_msg(r, time=None, bot=None):
    if isinstance(r, str):
        if bot is None:
            bot = nonebot.get_bot()
        await bot.delete_msg(message_id=r)
    else:
        await r.recall(delay=time or random.randint(60, 100), index=0)


async def get_message_at(data: str) -> int | None:
    '''
    获取at列表
    :param data: event.json()
    '''
    data = json.loads(data)
    try:
        msg = data['original_message'][1]
        if msg['type'] == 'at':
            return int(msg['data']['qq'])
    except Exception:
        return None


def extract_first_frame_from_gif(gif_bytes):
    gif_image = Image.open(BytesIO(gif_bytes))

    gif_image.seek(0)
    first_frame = gif_image.copy()

    byte_array = BytesIO()
    first_frame.save(byte_array, format="PNG")
    return byte_array.getvalue()


async def get_image(event, gif) -> list[bytes]:
    img_url = []
    reply = event.reply
    at_id = await get_message_at(event.json())
    # 获取图片url
    if at_id and not reply:
        img_url = [f"https://q1.qlogo.cn/g?b=qq&nk={at_id}&s=640"]
    for seg in event.message['image']:
        img_url.append(seg.data["url"])
    if reply:
        for seg in reply.message['image']:
            img_url.append(seg.data["url"])

    image_byte = []
    if img_url:
        for url in img_url:
            url = url.replace("gchat.qpic.cn", "multimedia.nt.qq.com.cn")
            logger.info(f"检测到图片，自动切换到以图生图，正在获取图片")

            byte_image = await http_request("GET", url, format=False)

            kind = filetype.guess(byte_image)
            file_format = kind.extension if kind else "unknown"

            if not gif:
                if 'gif' in file_format:
                    byte_image = extract_first_frame_from_gif(byte_image)
                else:
                    pass
            else:
                pass

            image_byte.append(byte_image)

    return image_byte


async def get_file_url(comfyui_instance, outputs, backend_url, task_id):
    images_url = []
    video_url = []
    audio_url = []

    for imgs in list(outputs.values()):
        if 'images' in imgs:
            for img in imgs['images']:

                filename = img['filename']
                _, file_format = os.path.splitext(filename)

                if img['subfolder'] == "":
                    url = f"{backend_url}/view?filename={filename}"
                else:
                    url = f"{backend_url}/view?filename={filename}&subfolder={img['subfolder']}"

                if img['type'] == "temp":
                    url = f"{backend_url}/view?filename={filename}&subfolder=&type=temp"

                images_url.append({"url": url, "file_format": file_format})

        if 'gifs' in imgs:
            for img in imgs['gifs']:
                filename = img['filename']
                _, file_format = os.path.splitext(filename)

                if img['subfolder'] == "":
                    url = f"{backend_url}/view?filename={filename}"
                else:
                    url = f"{backend_url}/view?filename={filename}&subfolder={img['subfolder']}"

                if img['type'] == "temp":
                    url = f"{backend_url}/view?filename={filename}&subfolder=&type=temp"

                video_url.append({"url": url, "file_format": file_format})

        if "audio" in imgs:
            for img in imgs['audio']:
                filename = img['filename']
                _, file_format = os.path.splitext(filename)

                if img['subfolder'] == "":
                    url = f"{backend_url}/view?filename={filename}"
                else:
                    url = f"{backend_url}/view?filename={filename}&subfolder={img['subfolder']}"

                if img['type'] == "temp":
                    url = f"{backend_url}/view?filename={filename}&subfolder=&type=temp"

                audio_url.append({"url": url, "file_format": file_format})

        if 'text' in imgs:

            for img in imgs['text']:
                comfyui_instance.unimessage += img

    comfyui_instance.resp_msg.media_url['image'] = images_url
    comfyui_instance.resp_msg.media_url['video'] = video_url
    comfyui_instance.resp_msg.media_url['audio'] = audio_url
    comfyui_instance.resp_msg.backend_index = config.comfyui_url_list.index(backend_url)
    comfyui_instance.resp_msg.task_id = task_id

    comfyui_instance.resp_msg_list.append(comfyui_instance.resp_msg)

    return comfyui_instance


async def build_help_text(reg_command):

    argument_list = []

    for action in comfyui_parser._actions:
        if action.dest != 'help':
            argument_info = {}
            options = action.option_strings

            if options:
                argument_info["flag"] = options[0]
            else:
                argument_info["flag"] = action.dest

            argument_info["description"] = action.help.split("example:")[0].strip() if "example:" in action.help else action.help

            if options:
                if "example:" in action.help:
                    argument_info["example"] = action.help.split("example:")[1].strip()

            argument_list.append(argument_info)

    template_data = {
        "reg_commands": reg_command,
        "parameters": argument_list,
        "shape_presets": [
            {"name": k, "width": v[0], "height": v[1]} 
            for k, v in config.comfyui_shape_preset.items()
        ],
        "queue_params": [
            {
                "flag": "-be",
                "description": "需要查看队列的后端索引或者URL(不添加默认0)",
                "example": "queue -get bedadef6-269c-43f4-9be4-0e5b07061233 -be 0"
            },
            {
                "flag": "-t",
                "description": "追踪后端当前所有的任务id",
                "example": "queue -t -be 'http://127.0.0.1:8288'"
            },
            {
                "flag": "-d",
                "description": "需要删除的任务id",
                "example": "queue -d bedadef6-269c-43f4-9be4-0e5b07061233 -be 0"
            },
            {
                "flag": "-c",
                "description": "清除后端上的所有任务",
                "example": "queue -c -be 0"
            },
            {
                "flag": "-i",
                "description": "需要查询的任务id",
                "example": "queue -i bedadef6-269c-43f4-9be4-0e5b07061233 -be 0"
            },
            {
                "flag": "-v",
                "description": "查看历史任务, 配合-index使用",
                "example": "queue -v -index 0-20 -be 0"
            },
            {
                "flag": "-get",
                "description": "后接任务的id",
                "example": "queue -get bedadef6-269c-43f4-9be4-0e5b07061233 -be 0"
            },
            {
                "flag": "-stop",
                "description": "停止当前生成",
                "example": "queue -stop"
            }
        ],
        "capi_params": [
            {
                "flag": "-be",
                "description": "需要查看节点的后端索引或者URL(不添加默认0)",
                "example": "capi -be 0 -get all"
            },
            {
                "flag": "-get",
                "description": "需需要查看的节点信息, 例如 capi -get all -be 0 (获取所有节点名称)",
                "example": "capi -get KSampler -be 0 \n(获取KSampler节点的信息)"
            }
        ],
        "other_commands": [
            {
                "command": "查看工作流",
                "description": "查看插件加载的所有工作流, 可以使用序号或者名称进行匹配",
                "example": "查看工作流 1 \n 查看工作流 flux"
            },
            {
                "command": "comfyui后端",
                "description": "查看插件加载的后端的状态",
                "example": "comfyui后端"
            },
            {
                "command": "二次元的我",
                "description": "随机拼凑prompt来生成图片",
                "example": "二次元的我, 二次元的鸡"
            },
            {
                "command": "dan",
                "description": "从Danbooru上查询tag, 用来查找tag或者角色",
                "example": "dan 原神 10 (查看10个结果)\ndan 'blue archive' \n 查看符合输入的tag"
            },
            {
                "command": "llm-tag",
                "description": "使用llm生成prompt",
                "example": "llm-tag 海边的少女"
            },
            {
                "command": "get-ckpt",
                "description": "获取指定后端索引的模型",
                "example": "get-ckpt 0 / get-ckpt 1 "
            },
            {
                "command": "get-loras",
                "description": "获取指定后端索引的lora模型",
                "example": "get-loras 0 / get-loras 1 "
            },
            {
                "command": "get-task",
                "description": "获取自己生成过的任务id, 默认显示前10",
                "example": "get-task 10-20 (获取10-20个任务的id) "
            }
            
        ],
        "version": PLUGIN_VERSION
    }

    env = Environment(loader=FileSystemLoader(str(PLUGIN_DIR / 'template')))
    template = env.get_template('help.html')
    return template.render(**template_data)


def get_and_filter_work_flows(search=None, index=None) -> list:

    index = int(index) if index else None

    if not isinstance(search, str):
        search = None

    wf_files = []
    for root, dirs, files in os.walk(config.comfyui_workflows_dir):
        for file in files:
            if file.endswith('.json') and not file.endswith('_reflex.json'):
                if search and search in file:
                    wf_files.append(file.replace('.json', ''))
                elif not search:
                    wf_files.append(file.replace('.json', ''))

    if index is not None:
        if 1 <= index < len(wf_files) + 1:
            return [wf_files[index-1]]
        else:
            return []

    return wf_files


async def http_request(
        method,
        target_url,
        headers=None,
        params=None,
        content=None,
        format=True,
        timeout=5000,
        verify=True,
        proxy=False,
        text=False
) -> dict| bytes | str:

    global_ssl_context = ssl.create_default_context()
    global_ssl_context.set_ciphers('DEFAULT')
    global_ssl_context.options |= ssl.OP_NO_SSLv2
    global_ssl_context.options |= ssl.OP_NO_SSLv3
    global_ssl_context.options |= ssl.OP_NO_TLSv1
    global_ssl_context.options |= ssl.OP_NO_TLSv1_1
    global_ssl_context.options |= ssl.OP_NO_COMPRESSION

    connector = TCPConnector(ssl=global_ssl_context)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=timeout),
        proxy=config.comfyui_http_proxy if proxy else None
    ) as session:
        try:
            async with session.request(
                method,
                target_url,
                headers=headers,
                params=params,
                data=content,
                ssl=verify,
            ) as response:
                if text:
                    return await response.text()
                if format:
                    return await response.json()
                else:
                    return await response.read()
        except Exception as e:
            raise ComfyuiExceptions.ComfyuiBackendConnectionError(f"请求后端时出现错误: {e}")


def obfuscate_url(url):

    prefix_length = 8
    suffix_length = 8

    if len(url) <= prefix_length + suffix_length:
        return url

    prefix = url[:prefix_length]
    suffix = url[-suffix_length:]

    obfuscated_part = '*' * (len(url) - prefix_length - suffix_length)

    return prefix + obfuscated_part + suffix


async def get_backend_status():
    backend_status_task_list = []
    backend_queue_task_list = []

    timeout = config.comfyui_timeout

    for url in config.comfyui_url_list:
        backend_status_task_list.append(http_request("GET", target_url=f"{url}/system_stats", timeout=timeout))
        backend_queue_task_list.append(http_request("GET", target_url=f"{url}/queue", timeout=timeout))

    status_responses = await asyncio.gather(*backend_status_task_list, return_exceptions=True)
    queue_responses = await asyncio.gather(*backend_queue_task_list, return_exceptions=True)

    results = []
    for idx, url in enumerate(config.comfyui_url_list):
        node_status = {
            "url": obfuscate_url(url),
            "system": {},
            "queue": {},
            "error": None,
            "index": config.comfyui_url_list.index(url)
        }

        status_resp = status_responses[idx]
        if isinstance(status_resp, Exception):
            node_status["error"] = f"System stats request failed: {str(status_resp)}"
        elif not isinstance(status_resp, dict):
            node_status["error"] = f"Invalid system stats response format: {type(status_resp)}"
        else:
            system_data = status_resp.get("system", {})
            node_status["system"].update({
                "comfyui_version": system_data.get("comfyui_version"),
                "python_version": system_data.get("python_version"),
                "pytorch_version": system_data.get("pytorch_version"),
                "startup_args": system_data.get("argv", [])
            })

            devices = status_resp.get("devices", [])
            if devices:
                device = devices[0]
                node_status["system"].update({
                    "device_name": device.get("name"),
                    "vram_free": device.get("vram_free"),
                    "vram_total": device.get("vram_total")
                })

        queue_resp = queue_responses[idx]
        if isinstance(queue_resp, Exception):
            node_status["error"] = f"Queue request failed: {str(queue_resp)}"
        elif not isinstance(queue_resp, dict):
            node_status["error"] = f"Invalid queue response format: {type(queue_resp)}"
        else:
            running_tasks = queue_resp.get("queue_running", [])
            pending_tasks = queue_resp.get("queue_pending", [])

            node_status["queue"].update({
                "running_count": len(running_tasks),
                "pending_count": len(pending_tasks),
                "running_ids": [task[1] for task in running_tasks],
                "pending_ids": [task[1] for task in pending_tasks]
            })

        results.append(node_status)
    return results


async def txt_audit(
        msg,
        prompt='''
        接下来请你对一些聊天内容进行审核,
        如果内容出现政治/暴力/恐怖袭击/血腥/内容（特别是我国的政治人物/或者和我国相关的政治）则请你输出<yes>, 
        如果没有则输出<no>,
        请注意， 和这几项(政治/暴力/恐怖袭击/血腥)无关的内容不需要你的判断， 最后， 只输出<yes>或者<no>不需要你输出其他内容
        '''
):
    try:

        if config.comfyui_text_audit is False:
            return 'no'

        system = [
            {"role": "system",
             "content": prompt}
        ]
        prompt = [{"role": "user", "content": msg}]

        response_data = await http_request(
            "POST", config.comfyui_openai['endpoint'] + "/chat/completions",
            headers={"Authorization": config.comfyui_openai["token"]},
            content=json.dumps({
                    "model": config.comfyui_openai.get("params")['model'],
                    "messages": system + prompt,
                    "max_tokens": 4000,
            }),
            proxy=True

        )

        res: str = remove_punctuation(response_data['choices'][0]['message']['content'].strip())
        logger.info(f'进行文字审核审核,输入{msg}, 输出{res}')
        return res

    except:
        traceback.print_exc()
        return "yes"


def remove_punctuation(text):
    import string
    for i in range(len(text)):
        if text[i] not in string.punctuation:
            return text[i:]
    return ""


async def download_img(url):
    url = url.replace("gchat.qpic.cn", "multimedia.nt.qq.com.cn")
    img_bytes = await http_request("GET", url, format=False)
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    return img_base64, img_bytes


async def translate_api(tags, to):

    async def _api(input: str, to: str):
        try:
            url = f"http://{config.trans_api}/translate"
            headers = {"Content-Type": "application/json"}
            payload = {"text": input, "to": to}
            async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=3)
            ) as session:
                async with session.post(url=url, data=json.dumps(payload)) as resp:
                    if resp.status != 200:
                        logger.error(f"自建翻译接口错误, 错误代码{resp.status},{await resp.text()}")
                        return None
                    else:
                        logger.info("自建api翻译成功")
                        json_ = await resp.json()
                        result = json_["translated_text"]
                        return result
        except:
            logger.warning(traceback.print_exc())
            return None

    return tags


async def get_qr(msg, bot):
    retry_count = 0
    max_retries = 4

    while retry_count < max_retries:
        try:
            message_data = await bot.send_private_msg(
                user_id=bot.self_id,
                message=await UniMessage.image(raw=msg).export()
            )
        except:
            retry_count += 1
            logger.warning(f'私聊图片发送给自身失败 (第 {retry_count} 次重试), 重试中')
            await asyncio.sleep(1)
        else:
            break

    if retry_count >= max_retries:
        raise ComfyuiExceptions.SendImageToBotException

    message_id = message_data["message_id"]
    message_all = await bot.get_msg(message_id=message_id)
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    img_url = re.findall(url_regex, str(message_all["message"]))[0]
    img_url = img_url.replace("multimedia.nt.qq.com.cn", "gchat.qpic.cn")
    img_id = time.time()
    img = qrcode.make(img_url)
    
    file_name = f"qr_code_{img_id}.png"
    img.save(file_name)
    with open(file_name, 'rb') as f:
        bytes_img = f.read()
        
    os.remove(file_name)
        
    return bytes_img, img_url


async def is_port_open(host: str, port: int, timeout=config.comfyui_timeout) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return False


async def get_backend_work_status(url: str) -> dict:
    
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or (80 if parsed_url.scheme == "http" else 443)

    if not await is_port_open(host, port):
        raise ComfyuiExceptions.ComfyuiBackendConnectionError
    else:
        resp = await http_request("GET", target_url=f"{url}/prompt", timeout=config.comfyui_timeout)
        return resp


async def get_ava_backends():
    
    backend_dict = {}
    available_backends = set({})

    task_list = []
    for task in BACKEND_URL_LIST:
        task_list.append(get_backend_work_status(task))

    resp = await asyncio.gather(*task_list, return_exceptions=True)

    for i, backend_url in zip(resp, BACKEND_URL_LIST):
        backend_index = BACKEND_URL_LIST.index(backend_url)
        if isinstance(i, Exception):
            logger.warning(f"后端 {backend_url} 掉线")
            if backend_index in available_backends:
                available_backends.remove(backend_index)
        else:
            backend_dict[backend_url] = i
            available_backends.add(backend_index)
            
    return available_backends, backend_dict


def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    cumulative_weight = 0
    for c, w in choices:
        cumulative_weight += w
        if r < cumulative_weight:
            return c


async def get_all_loras(backend_url):
    resp = await http_request("GET", f"{backend_url}/object_info/LoraLoader")
    return resp['LoraLoader']['input']['required']['lora_name'][0]
