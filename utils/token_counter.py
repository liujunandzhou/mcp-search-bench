"""
Token 计数工具
使用 tiktoken 计算工具定义的 token 消耗
"""

import json
from typing import Union

try:
    import tiktoken
    _encoder = tiktoken.get_encoding("cl100k_base")
except Exception:
    _encoder = None


def count_tokens(text: str) -> int:
    """计算文本的 token 数量（使用 cl100k_base 编码）"""
    if _encoder:
        return len(_encoder.encode(text))
    # 简单的中英文 token 估算（备用方案）
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    en_words = len(text.encode('ascii', errors='ignore').split())
    return cn_chars * 2 + en_words + len(text) // 4


def tool_definition_to_json(tool) -> dict:
    """将工具定义转为类 OpenAI function calling 的 JSON 格式"""
    params = {}
    required = []
    for p in tool.params:
        params[p.name] = {"type": p.type, "description": p.description}
        if p.required:
            required.append(p.name)

    return {
        "type": "function",
        "function": {
            "name": tool.tool_id,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": params,
                "required": required,
            }
        }
    }


def count_tool_tokens(tools: list) -> int:
    """计算一组工具定义的 token 消耗"""
    tool_defs = [tool_definition_to_json(t) for t in tools]
    text = json.dumps(tool_defs, ensure_ascii=False)
    return count_tokens(text)


def count_text_tokens(text: str) -> int:
    """计算纯文本的 token 数量"""
    return count_tokens(text)


def estimate_meta_tool_tokens(meta_tools: list[dict]) -> int:
    """估算元工具（search/execute 等）的 token 消耗"""
    text = json.dumps(meta_tools, ensure_ascii=False)
    return count_tokens(text)
