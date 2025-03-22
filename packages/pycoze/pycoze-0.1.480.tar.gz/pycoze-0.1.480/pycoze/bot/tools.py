import os
import re
import subprocess
import fnmatch
from typing import Dict, Tuple
from .message import info
from .lib import get_formatted_filelist_str, read_local_file, resolve_relative_path
from pycoze import ai
from pycoze.api import window, web
import traceback
import json


class InvalidToolError(Exception):
    """无效工具错误"""

    pass


class Tool:
    """工具基类"""

    def __init__(self, params: Dict[str, str], cwd: str):
        self.params = params
        self.cwd = cwd

    def validate(self) -> bool:
        """验证参数是否有效"""
        raise NotImplementedError

    def execute(self) -> str:
        """执行工具并返回结果"""
        raise NotImplementedError


class ExecuteCommandTool(Tool):
    """执行命令工具"""

    def validate(self) -> bool:
        return "command" in self.params and "requires_approval" in self.params

    def execute(self) -> str:
        try:
            if self.params["requires_approval"]:
                approve = window.confirm(
                    "confirm",
                    f"Do you want to execute the command{self.params['command']}? ",
                )
                if not approve:
                    return "User does not wish to run the command."
            result = subprocess.run(
                self.params["command"],
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.cwd,
            )
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    self.params["command"],
                    result.stdout,
                    result.stderr,
                )
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"命令执行失败: {e.stderr}"
        except Exception as e:
            return f"执行命令时发生错误: {str(e)}"


class ReadFileTool(Tool):
    """读取文件工具"""

    def validate(self) -> bool:
        return "path" in self.params and os.path.exists(
            resolve_relative_path(self.cwd, self.params["path"])
        )

    def execute(self) -> str:
        path = resolve_relative_path(self.cwd, self.params["path"])
        content = read_local_file(path)
        return f"Successfully read the file, the content of the file [[{path}]] is:\n{content}\n\n\n"


class ReadMultipleFilesTool(Tool):
    """读取多个文件工具"""

    def validate(self) -> bool:
        return "paths_list" in self.params

    def execute(self) -> str:
        return_str = ""
        for path in self.params["paths_list"]:
            path = resolve_relative_path(self.cwd, path)
            if os.path.exists(path):
                content = read_local_file(path)
                return_str += f"The content of the file [[{path}]] is:\n{content}\n\n\n"
            else:
                return_str += f"File {path}  does not exist.\n\n\n"
        if return_str == "":
            return_str = "No files were read"
        return "Result of reading multiple files:" + return_str


class WriteFileTool(Tool):
    """写入或覆盖文件工具"""

    def validate(self) -> bool:
        return "path" in self.params and "content" in self.params

    def execute(self) -> str:
        path = resolve_relative_path(self.cwd, self.params["path"])
        # 确保路径是绝对路径
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        # 创建目录并写入或覆盖文件
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.params["content"].replace("@`@`@`@", "```"))
        return f"File [[{path}]] written successfully."


class ReplaceInFileTool(Tool):
    """替换文件部分内容工具"""

    def validate(self) -> bool:
        return "path" in self.params and "diff" in self.params

    def execute(self) -> str:
        path = resolve_relative_path(self.cwd, self.params["path"])
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 初始化成功和失败的计数器
        success_count = 0
        failure_count = 0
        failure_details = []  # 用于记录匹配失败的详细信息

        # 处理差异内容
        diff_content = self.params["diff"]
        for diff_block in diff_content.split("<<<<<<< SEARCH")[1:]:
            search, replace = diff_block.split("=======")
            search = search.strip()
            replace = replace.split(">>>>>>> REPLACE")[0].strip().replace("@`@`@`@", "```")
            if search in content:
                content = content.replace(search, replace, 1)
                success_count += 1
            else:
                failure_count += 1
                # 记录匹配失败的前20个字符
                failure_details.append(f"Failed to match: '{search[:20]}...'")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # 构建返回结果
        result = (
            f"The content of the file {path} has been replaced successfully. "
            f"Successfully replaced {success_count} occurrences. "
            f"Failed to replace {failure_count} occurrences."
        )
        if failure_details:
            result += "\nFailure details:\n" + "\n".join(failure_details)

        return result


class SearchFilesTool(Tool):
    """搜索文件工具"""

    def validate(self) -> bool:
        return "path" in self.params and "regex" in self.params

    def execute(self) -> str:
        path = resolve_relative_path(self.cwd, self.params["path"])
        results = []
        for root, _, files in os.walk(path):
            for file in files:
                if "file_pattern" in self.params:
                    if not fnmatch.fnmatch(file, self.params["file_pattern"]):
                        continue

                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = re.finditer(self.params["regex"], content)
                    for match in matches:
                        results.append(f"{file_path}: {match.group()}")

        return "\n".join(results) if results else "No matching content found."


class ListFilesTool(Tool):
    """列出文件工具"""

    def validate(self) -> bool:
        return "path" in self.params

    def execute(self) -> str:
        recursive = str(self.params.get("recursive", "false")).lower() == "true"
        path = resolve_relative_path(self.cwd, self.params["path"])
        return (
            "Listing files completed successfully, result is:\n"
            + get_formatted_filelist_str(path, recursive, 200)
            + "\n\n\n"
        )


class WebAccessTool(Tool):
    """访问网页工具"""

    def validate(self) -> bool:
        return "url" in self.params and "question" in self.params

    def execute(self) -> str:
        url = self.params["url"]
        question = self.params["question"]
        try:
            content = web.get_simplified_webpage(url)[: 32 * 1024]
            result = ai.chat(
                [
                    {
                        "role": "user",
                        "content": f"""Please answer user question based on web page content. The user's question is:
{question}
Web page content is:
{content}""",
                    }
                ],
            )
            return f"Web page access completed, result is: {result}"
        except Exception as e:
            print("WebAccessTool Exception", e)
            return f"Failed to access web page: {str(e)}"


class AskFollowUpQuestionTool(Tool):
    """询问后续问题工具"""

    def validate(self) -> bool:
        return "question" in self.params

    def execute(self) -> str:
        info("assistant", self.params["question"])
        return f"Asked user: {self.params['question']}, Waiting for user replied.\n\n"


class AttemptTaskCompletionTool(Tool):
    """完成所有任务工具"""

    def validate(self) -> bool:
        return "result" in self.params

    def execute(self) -> str:
        result = self.params["result"]
        if (
            "command" in self.params
            and self.params["command"] is not None
            and type(self.params["command"]) == str
            and len(self.params["command"]) > 0
        ):
            result = subprocess.run(
                self.params["command"],
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.cwd,
            )
            return f"Task completed: {result}, executed command: {self.params['command']}, execution result: {result.stdout + result.stderr}"
        else:
            return f"Task completed!"


class ToolExecutor:
    """工具执行器"""

    TOOL_MAP = {
        "execute_command": ExecuteCommandTool,
        "read_multiple_files": ReadMultipleFilesTool,
        "write_or_overwrite_file": WriteFileTool,
        "replace_part_of_a_file": ReplaceInFileTool,
        "search_files": SearchFilesTool,
        "list_files": ListFilesTool,
        "access_webpage": WebAccessTool,
        "ask_follow_up_question": AskFollowUpQuestionTool,
        "complete_all_tasks": AttemptTaskCompletionTool,
    }

    @classmethod
    def execute_tool(cls, cwd: str, tool_request, abilities) -> Tuple[bool, bool, any]:
        """执行工具"""
        try:
            tool_name = list(tool_request.keys())[0]
            params = tool_request[tool_name]
            if not tool_name:
                return False, False, "Error: Tool type is empty"
            if tool_name in cls.TOOL_MAP:
                tool_class = cls.TOOL_MAP[tool_name]
            elif tool_name in [a.__name__ for a in abilities]:
                func = [a for a in abilities if a.__name__ == tool_name][0]
                try:
                    result = func(**params)
                except Exception as e:
                    print("Execute tool error:", traceback.format_exc())
                    return False, False, traceback.format_exc()
                if isinstance(result, str):
                    return True, False, result
                try:
                    result = json.dumps(result, indent=4, ensure_ascii=False)
                except:
                    return True, False, str(result)
                return True, True, str(result)
            else:
                return (
                    False,
                    False,
                    f"Unknown tool: {tool_name}, the first key of output json ({tool_name}) will be recognized as a tool, so do not output other json except for executing tools.",
                )
            tool = tool_class(params, cwd)
            if not tool.validate():
                return False, False, "Tool parameter validation failed."
            return True, False, tool.execute()
        except Exception as e:
            return False, False, f"Tool execution failed:  {str(e)}"
