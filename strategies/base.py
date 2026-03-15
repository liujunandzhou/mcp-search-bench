"""
搜索策略基类
定义所有策略需要实现的统一接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from data.tools_registry import ToolDefinition


@dataclass
class SearchResult:
    """搜索结果"""
    tool_ids: list[str]                    # 返回的工具 ID 列表
    tool_definitions: list[ToolDefinition] # 返回的完整工具定义
    token_cost: int                        # 本次搜索的 token 消耗
    search_rounds: int = 1                 # 搜索轮次（多轮对话场景）
    meta_tool_tokens: int = 0             # 元工具定义的 token 消耗
    result_tokens: int = 0                # 搜索结果返回的 token 消耗
    failure_mode: str = ""                # 失败模式描述
    details: dict = field(default_factory=dict)  # 额外调试信息


class SearchStrategy(ABC):
    """搜索策略基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """策略名称"""
        pass

    @property
    @abstractmethod
    def name_cn(self) -> str:
        """策略中文名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """策略描述"""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> SearchResult:
        """
        根据用户意图搜索相关工具

        Args:
            query: 用户的自然语言查询
            top_k: 最多返回的工具数量

        Returns:
            SearchResult 对象
        """
        pass

    @abstractmethod
    def get_initial_token_cost(self) -> int:
        """
        获取策略的初始注入 token 消耗
        （即元工具定义所占的 token 数）
        """
        pass
