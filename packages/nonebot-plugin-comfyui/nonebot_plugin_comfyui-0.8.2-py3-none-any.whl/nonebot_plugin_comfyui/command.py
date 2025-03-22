import asyncio

from nonebot.plugin.on import on_shell_command, on_command

from nonebot_plugin_htmlrender import html_to_pic, md_to_pic
from nonebot_plugin_alconna import on_alconna, Args, Alconna

from jinja2 import Environment, FileSystemLoader
from .backend.help import ComfyuiHelp
from .handler import *
from .parser import comfyui_parser, api_parser, queue_parser, rebuild_parser
from .backend.utils import build_help_text, get_backend_status
from .config import PLUGIN_DIR

comfyui = on_shell_command(
    "prompt",
    parser=comfyui_parser,
    priority=5,
    block=True,
    handlers=[comfyui_handler]
)

queue = on_shell_command(
    "queue",
    parser=queue_parser,
    priority=5,
    block=True,
    handlers=[queue_handler]
)

api = on_shell_command(
    "capi",
    parser=api_parser,
    priority=5,
    block=True,
    handlers=[api_handler]
)


help_ = on_command(
    "comfyui帮助", 
    aliases={"帮助", "菜单", "help", "指令"},
    priority=1, 
    block=False
)

view_workflow = on_alconna(
    Alconna("查看工作流", Args["search?", str]),
    priority=5,
    block=True,
    use_cmd_start=True
)

backend = on_command(
    "后端",
    aliases={"comfyui后端"},
    priority=1,
    block=False
)

today_girl = on_shell_command(
    "二次元的",
    parser=comfyui_parser,
    priority=5,
    block=True,
    handlers=[today_girl_handler]
)

on_alconna(
    Alconna("dan", Args["tag", str]["limit?", int]),
    handlers=[danbooru_handler],
    block=True,
    use_cmd_start=True
)

llm = on_shell_command(
    "llm-tag",
    priority=1,
    block=True,
    handlers=[llm_handler],
    parser=comfyui_parser,
)

on_alconna(
    Alconna("get-ckpt", Args["index", int]),
    priority=5,
    block=True,
    handlers=[get_checkpoints],
    use_cmd_start=True
)

on_alconna(
    Alconna("get-loras", Args["index", int]),
    priority=5,
    block=True,
    handlers=[get_loras],
    use_cmd_start=True,
    aliases={"get-lora"}
)

on_alconna(
    Alconna("get-task", Args["index?", str]),
    priority=5,
    block=True,
    handlers=[get_task],
    use_cmd_start=True
)


async def start_up_func():

    async def set_command():
        reg_command = []

        _, content, wf_name = await ComfyuiHelp().get_reflex_json()

        for wf, wf_name in zip(content, wf_name):
            if "command" in wf:
                reg_args = None

                if "reg_args" in wf:
                    reg_args = wf["reg_args"]

                comfyui_parser = await rebuild_parser(wf_name, reg_args)
                command = wf["command"]
                command_list = command if isinstance(command, list) else [command]

                build_dict = {
                    "cmd": command_list[0],
                    "parser": comfyui_parser,
                    "priority": 5,
                    "block": True,
                    "handlers": [comfyui_handler]
                }

                if len(command_list) > 1:
                    build_dict.update({"aliases": set(command_list[1:])})

                on_shell_command(
                    **build_dict
                )

                logger.info(f"成功注册命令: {wf['command']}")
                reg_command.append((wf["command"], wf.get("note", "")))

        return reg_command

    return await set_command()


@help_.handle()
async def _():
    img = await html_to_pic(html=await build_help_text(reg_command))
    
    ug_str = '⚠️⚠️⚠️基础使用教程⚠️⚠️⚠️'

    source_template = PLUGIN_DIR / "template/example.md"

    with open(source_template, 'r', encoding='utf-8') as f:
        source_template = f.read()
    
    user_guidance = await md_to_pic(md=source_template)
    ug_str += UniMessage.image(raw=user_guidance)
    ug_str += '⚠️⚠️⚠️重要⚠️⚠️⚠️'

    msg = UniMessage.text('项目地址: github.com/DiaoDaiaChan/nonebot-plugin-comfyui')
    img = UniMessage.image(raw=img)
    msg = msg + img

    await msg.send()
    await asyncio.sleep(1)
    await ug_str.finish()


@view_workflow.handle()
async def _(search):

    html_, msg = await ComfyuiHelp().get_html(search)
    img = await html_to_pic(html=html_)

    msg = UniMessage.image(raw=img) + msg
    await msg.finish()


@backend.handle()
async def _():
    data = await get_backend_status()

    env = Environment(loader=FileSystemLoader(str(PLUGIN_DIR / 'template')))
    template = env.get_template('backend_status.html')

    html_output = template.render(data=data)
    img = await html_to_pic(html=html_output)

    msg = UniMessage.image(raw=img)
    await msg.finish()

reg_command = asyncio.run(start_up_func())
