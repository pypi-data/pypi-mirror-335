import json
import os
from .lib import get_formatted_filelist_str, read_local_file, resolve_relative_path
from .message import info
from pycoze.ai import chat_stream_async, extract
from .tools import ToolExecutor
from typing import List
import re

def guess_files_in_message(cwd: str, user_message: str) -> List[str]:
    try:
        value = extract(
            {"includedFiles": ["relative path format", "relative path format", "..."]},
            'Please find the files mentioned in the text. If none, return {"includedFiles": []}:\n'
            + user_message,
        )
        return [resolve_relative_path(cwd, p) for p in value["includedFiles"]]
    except:
        print("Failed to guess files in message")
        return []


def format_content(cwd, potential_paths, conversation_history):
    content = []
    for file_path in potential_paths:
        file_path = resolve_relative_path(cwd, file_path)
        if os.path.isfile(file_path):
            file_marker = f"[[{file_path}]]'"
            file_content = read_local_file(file_path)
            if not any(
                file_marker in msg["content"] for msg in conversation_history
            ):
                content.append(f"{file_marker}\n{file_content}")
    return (
        "Partial contents of files are as follows:" + "\n".join(content)
        if content
        else ""
    )

def generate_user_task_prompt(conversation_history, cwd, user_input: str, bot_setting_file:str):
    # 需要重新读取openedFiles和activeFile
    with open(bot_setting_file, encoding="utf-8") as f: 
        bot_setting = json.load(f)
    folder_context = bot_setting["folderContext"]
    opened_files = bot_setting["openedFiles"]
    active_file = bot_setting["activeFile"]

    if folder_context:
        potential_paths = guess_files_in_message(cwd, user_input)

        existing_files = get_formatted_filelist_str(cwd, True, 200)

        active_file_str = f"Currently viewing: {active_file}" if active_file else ""
        
        opened_files_str = '\n'.join(opened_files)
        opened_files_str =  f"Open tabs:\n{opened_files_str}" if opened_files else ""
        
        existing_files_str = f"Files in directory:\n{existing_files}" if existing_files else ""
        return f"""<task>
{user_input}
</task>

<environment_details>
Current working directory: {cwd}

{active_file_str}

{opened_files_str}

{existing_files_str}

{format_content(cwd, potential_paths, conversation_history)}

</environment_details>
    """

    else:
        return f"""<task>
{user_input}
</task>
"""


def dumps_markdown_json(data):
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    return f"\n```json\n{json_str}\n```\n"



class BufferProcessor:
    def __init__(self):
        self.buffer = ""
        self.in_json_block = False
        self.json_block_content = ""
        self.text_content = ""

    def can_process(self):
        if not self.in_json_block:
            return re.search(r"```json", self.buffer, re.IGNORECASE)
        else:
            return re.search(r"```", self.buffer)

    def process_buffer(self):
        """
        处理 buffer 中的内容，并返回生成的内容类型和内容。
        返回格式为 (type, content)，其中 type 可以是 "text" 或 "json"。
        """
        if not self.in_json_block:
            # 查找 JSON 代码块的起始标记
            json_start_match = re.search(r"```json", self.buffer, re.IGNORECASE)
            if json_start_match:
                # 提取 JSON 代码块之前的文本
                self.text_content += self.buffer[:json_start_match.start()]
                # 进入 JSON 代码块模式
                self.in_json_block = True
                self.buffer = self.buffer[json_start_match.end():]
                # 如果 text_content 不为空，先 yield 文本
                if self.text_content.strip():
                    # results.append(("text", self.text_content.strip()))
                    self.text_content = ""
                    return ("text", self.text_content.strip())

            else:
                # 如果没有找到 JSON 代码块，继续累积到 text_content
                self.text_content += self.buffer
                self.buffer = ""
        else:
            # 查找 JSON 代码块的结束标记
            json_end_match = re.search(r"```", self.buffer)
            if json_end_match:
                # 提取 JSON 代码块内容
                self.json_block_content += self.buffer[:json_end_match.start()]
                # yield JSON 代码块
                self.in_json_block = False
                self.buffer = self.buffer[json_end_match.end():]
                json_block_content = self.json_block_content
                self.json_block_content = ""
                return ("json", json_block_content)

            else:
                # 如果没有找到结束标记，继续累积 JSON 内容
                self.json_block_content += self.buffer
                self.buffer = ""
        return None

    def finalize(self):
        """
        处理流结束后的剩余内容。
        返回格式为 (type, content)，其中 type 可以是 "text" 或 "json"。
        """
        results = []
        if self.in_json_block:
            # 如果仍在 JSON 代码块模式，处理剩余的 JSON 内容
            if self.json_block_content.strip():
                results.append(("json", self.json_block_content.strip()))
        else:
            # 如果不在 JSON 代码块模式，处理剩余的文本内容
            if self.text_content.strip():
                results.append(("text", self.text_content.strip()))
        return results

    def reset(self):
        """
        重置 buffer 处理器的状态。
        """
        self.buffer = ""
        self.in_json_block = False
        self.json_block_content = ""
        self.text_content = ""


async def stream_openai_response(conversation_history, start_new_stream):
    """
    异步流式传输 OpenAI 聊天完成响应并处理结构化输出
    """
    stream = None
    buffer_processor = BufferProcessor()

    while True:
        # 检查是否需要重新创建流
        if stream is None or start_new_stream["value"]:
            if stream is not None:
                await stream.aclose()  # 关闭之前的流
            stream = chat_stream_async(conversation_history)  # 获取新的异步生成器
            start_new_stream["value"] = False  # 重置标志
            buffer_processor.reset()

        # 使用 async for 迭代异步生成器
        try:
            async for chunk in stream:
                # 检查是否需要重新创建流
                if start_new_stream["value"]:
                    break  # 退出当前的 async for 循环，进入下一次 while 循环
                info("assistant", chunk)
                buffer_processor.buffer += chunk
                
                if buffer_processor.can_process():
                    result = buffer_processor.process_buffer()
                    if result:
                        yield result

            # 如果流正常结束，退出 while 循环
            break

        except Exception as e:
            # 捕获其他异常（如网络错误）
            print(f"Error: {e}", style="bold red")
            break
    
    while buffer_processor.buffer:
        result = buffer_processor.process_buffer()
        if result:
            yield result
        else:
            break

    # 处理流结束后的剩余内容
    for result in buffer_processor.finalize():
        yield result



async def handle_user_inputs(
    conversation_history, user_input, cwd, abilities, has_any_tool, bot_setting, bot_setting_file:str
):
    no_exit_if_incomplete = bot_setting["systemAbility"]["no_exit_if_incomplete"]
    show_tool_results = bot_setting["showToolResults"]
    
    start_new_stream = {
        "value": False
    }  # 当遇到AI准备执行JSON，即需要新信息的时候，用于强制停止当前stream，减少后续无效的tokens

    print("Processing user command", user_input)
    if user_input.lower() in ["exit", "quit"]:
        exit(0)
    # 将用户消息添加到对话历史
    conversation_history.append(
        {
            "role": "user",
            "content": generate_user_task_prompt(
                conversation_history, cwd, user_input, bot_setting_file
            ),
        }
    )
    need_break = False

    if no_exit_if_incomplete:
        okay_str = 'Okay, please continue. If the tasks within <task>...task content...</task> have been completed, execute the tool "complete_all_tasks". If you have a question, use "ask_follow_up_question".'
    else:
        okay_str = "Okay"
    while True:
        async for response in stream_openai_response(
            conversation_history, start_new_stream
        ):
            if len(response) == 2:
                if (
                    response[0] == "text"
                    and response[1].strip() != ""
                    or (response[0] == "json" and not has_any_tool)
                ):
                    if response[0] == 'text':
                        conversation_history.append(
                            {"role": "assistant", "content": response[1]}
                        )
                    else:
                        conversation_history.append(
                            {"role": "assistant", "content": "\n```" + response[0] + "\n" + response[1] + "\n```\n"}
                        )

                    conversation_history.append(
                        {
                            "role": "user",
                            "content": okay_str,
                        }
                    )
                    continue
                elif response[0] == "json":
                    info("assistant", "\n")
                    cleaned_content = response[1]
                    try:
                        tool_request = json.loads(cleaned_content)
                        tool_name = list(tool_request.keys())[0]
                    except json.JSONDecodeError as e:
                        conversation_history.append(
                            {
                                "role": "assistant",
                                "content": f"\n```json\n{cleaned_content}\n```\n",
                            }
                        )
                        conversation_history.append(
                            {
                                "role": "user",
                                "content": "Invalid JSON content:" + str(e),
                            }
                        )
                        continue

                    ok, is_json_dumps, result = ToolExecutor.execute_tool(
                        cwd, tool_request, abilities
                    )
                    
                    assistant_content = (
                        dumps_markdown_json(tool_request)
                        + "\n\n[Tool Result Begin]\n"
                        + result
                        + "\n[Tool Result End]\n"
                    )
                    lang = "json" if is_json_dumps else "text"
                    
                    if show_tool_results:
                        status_str = "✅\n" if ok else "❌\n"
                        info("assistant", status_str + f"\n```{lang}\n" + result + "\n```\n\n")

                    conversation_history.append(
                        {"role": "assistant", "content": assistant_content}
                    )
                    if tool_name in ["complete_all_tasks", "ask_follow_up_question"]:
                        need_break = True
                        break
                    else:
                        conversation_history.append(
                            {
                                "role": "user",
                                "content": okay_str,
                            }
                        )
                        start_new_stream["value"] = True

        if need_break:
            break
        if not no_exit_if_incomplete and not start_new_stream["value"]:
            break
    last_conversation = conversation_history[-1]
    if last_conversation["role"] == 'user' and last_conversation["content"] == okay_str:
        conversation_history.pop()

# 示例调用
# user_input_list = [
#     "访问https://api-docs.deepseek.com/zh-cn/guides/chat_prefix_completion，并结合它编写一段代码，并保存"
# ]

# asyncio.run(handle_user_inputs(user_input_list))
