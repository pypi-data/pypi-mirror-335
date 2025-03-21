import os
from collections import defaultdict
import platform
from jinja2 import Template
from pathlib import Path
from pycoze.reference.bot import ref_bot
from pycoze.reference.tool import ref_tools
from pycoze.reference.workflow import ref_workflow
import inspect


def function_to_string(func):
    # 获取函数签名
    signature = inspect.signature(func)

    # 获取函数名
    func_name = func.__name__

    # 获取函数的文档字符串
    docstring = func.__doc__

    # 格式化函数签名
    func_signature = f"def {func_name}{signature}:"

    # 构建最终的字符串
    result = f"#### {func_name.capitalize().replace('_', ' ')}\n"
    result += "**Function Signature:**\n"
    result += f"```python\n{func_signature}\n    \"\"\"{docstring}\n    \"\"\"\n    pass\n```\n\n"
    result += "**Usage:**\n"
    result += "```json\n"
    result += f"{{\n  \"{func_name}\": {{\n"

    # 添加参数
    for name, param in signature.parameters.items():
        result += f"    \"{name}\": \"{param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'value'}\"\n"

    result += "  }\n"
    result += "}\n"
    result += "```"

    return "\n\n" + result + "\n\n"

def get_abilities(bot_setting):
    abilities = []
    for bot_id in bot_setting["bots"]:
        bot = ref_bot(bot_id)
        if bot:
            abilities.append(bot)
    for tool_id in bot_setting["tools"]:
        abilities.extend(ref_tools(tool_id))
    for workflow_id in bot_setting["workflows"]:
        workflow = ref_workflow(workflow_id)
        if workflow:
            abilities.append(workflow)
    return abilities


def get_system_prompt(abilities, bot_setting):
    md_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.md")
    with open(md_file, encoding="utf-8") as f:
        template = Template(f.read())

    if platform.system() == "Windows":
        cd_prompt = "When executing outside the working directory, include the CD command, such as cd /path/to/directory ; ls."
    else:
        cd_prompt = "When executing outside the working directory, include the CD command, such as cd /path/to/directory && ls."
    system = platform.system()


    abilities_str = "\n".join([function_to_string(a) for a in abilities])

    context = {
        "prompt": bot_setting["prompt"],
        "system": system,
        "cd_prompt": cd_prompt,
        "abilities_str": abilities_str,
        "no_exit_if_incomplete": False,
        "allow_read_multiple_files": False,
        "allow_execute_command": False,
        "allow_write_or_overwrite_file": False,
        "allow_replace_part_of_a_file": False,
        "allow_search_files": False,
        "allow_list_files": False,
        "allow_access_webpage": False,
        "folder_context": bot_setting["folderContext"],
        "use_draft": bot_setting["useDraft"]
    }

    context.update(bot_setting["systemAbility"])
    
    has_any_tool = False
    if len(abilities) > 0:
        has_any_tool = True
    for key in bot_setting["systemAbility"]:
        if key != "folder_context" and bot_setting["systemAbility"][key] == True:
            has_any_tool = True
            break
            
    context["has_any_tool"] = has_any_tool
    system_prompt = template.render(context)

    return system_prompt, has_any_tool


def resolve_relative_path(cwd:str, path_str: str) -> str:
    """返回基于CWD的规范化绝对路径"""
    path = Path(path_str)
    if path.is_absolute():
        return str(path.resolve())
    else:
        return str((Path(cwd) / path_str).resolve())


def read_local_file(file_path: str) -> str:
    """读取本地文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        import chardet

        with open(file_path, "rb") as f:
            rawdata = f.read()
            encoding = chardet.detect(rawdata)["encoding"]
            return rawdata.decode(encoding)


# 全局忽略列表
IGNORE_LIST = [
  'node_modules',
  '.git',
  '.vscode',
  '.idea',
  'gitServer',
  '.DS_Store',
  '$RECYCLE.BIN',
  '.Trash-1000',
  '.Spotlight-V100',
  '.Trashes',
  '.TemporaryItems',
  '.fseventsd',
  'System Volume Information',
  'pycache',
  'env',
  'venv',
  'target/dependency',
  'build/dependencies',
  'dist',
  'out',
  'bundle',
  'vendor',
  'tmp',
  'temp',
  'deps',
  'pkg',
  'Pods',
  'build',
  '.egg-info',
  '.venv',
  '__pycache__',
  '.vs',
  '.next',
  '.nuxt',
  '.cache',
  '.sass-cache',
  '.gradle',
  '.ipynb_checkpoints',
  '.pytest_cache',
  '.mypy_cache',
  '.tox',
  '.hg',
  '.svn',
  '.bzr',
  '.lock-wscript',
  '.wafpickle-[0-9]*',
  '.lock-waf_[0-9]*',
  '.Python',
  '.jupyter',
  '.vscode-test',
  '.history',
  '.yarn',
  '.yarn-cache',
  '.eslintcache',
  '.parcel-cache',
  '.cache-loader',
  '.nyc_output',
  '.node_repl_history',
  '.pnp.js',
  '.pnp',
  '.obsidian',
  ".husky",
  '.github',
  ".changeset"
]


def should_ignore(path):
    """检查路径是否在忽略列表中"""
    parts = path.split(os.sep)
    return any(part in IGNORE_LIST for part in parts)


def get_files_and_folders(root, recursive: bool):
    """递归获取所有文件和文件夹，并记录属性"""
    items = []

    # 使用 os.walk 遍历目录
    for dirpath, dirnames, filenames in os.walk(root):
        # 排除忽略列表中的路径
        if should_ignore(dirpath):
            continue

        # 记录文件夹
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not should_ignore(full_path):
                relative_path = os.path.relpath(full_path, root)
                is_empty = not os.listdir(full_path)
                depth = relative_path.count(os.sep)
                items.append(
                    (relative_path, "empty_folder" if is_empty else "folder", depth)
                )

        # 记录文件
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not should_ignore(full_path):
                relative_path = os.path.relpath(full_path, root)
                depth = relative_path.count(os.sep)
                items.append((relative_path, "file", depth))

        # 如果 recursive 为 False，则只遍历当前目录，不进入子目录
        if not recursive:
            break

    return items


def format_filelist_str(items, limit):
    """根据limit格式化输出"""
    depth_groups = defaultdict(list)
    for item in items:
        depth_groups[item[2]].append(item)

    max_depth = max(depth_groups.keys(), default=0)
    show_list = []
    last_depth = 0

    # 浅层
    current_items = sorted(depth_groups[0], key=lambda x: x[0])
    overflow = len(current_items) > limit
    for item in current_items[:limit]:
        show_list.append(item)

    for depth in range(1, max_depth + 1):
        current_items = depth_groups[depth]
        if len(show_list) + len(current_items) <= limit:
            last_depth = depth
            for item in current_items:
                show_list.append(item)
        else:
            break

    result_str_list = []
    show_list.sort(key=lambda x: x[0])
    for item in show_list:
        if item[1] == "file":
            result_str_list.append(f"{item[0]}")
        elif item[1] == "folder" and item[2] == last_depth:
            result_str_list.append(f"{item[0]}/...more...")
        else:
            result_str_list.append(f"{item[0]}/")
    if overflow:
        result_str_list.append("...more...")

    return "\n".join(result_str_list)


def get_formatted_filelist_str(root: str, recursive: bool, limit=200):
    items = get_files_and_folders(root, recursive)
    return format_filelist_str(items, limit=limit)
