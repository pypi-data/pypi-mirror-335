import os
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.utils.pprint import pprint_run_response
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai.like import OpenAILike


class CmdAgent:
    """Terminal Command Assistant agent."""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model_id: str = "qwen-plus"):
        """Initialize the command agent with API configuration.
        
        Args:
            api_key: The API key to use. If None, uses the AGNO_API_KEY environment variable.
            api_base: The API base URL. If None, uses the AGNO_API_BASE environment variable.
            model_id: The model ID to use, defaults to "qwen-plus".
        """
        self.api_key = api_key or os.getenv("AGNO_API_KEY")
        self.api_base = api_base or os.getenv("AGNO_API_BASE")
        self.model_id = model_id
        
        if not self.api_key:
            raise ValueError("API key must be provided either through AGNO_API_KEY environment variable or --api-key parameter")
        
        if not self.api_base:
            raise ValueError("API base URL must be provided either through AGNO_API_BASE environment variable or --api-base parameter")
        
        self.instructions = self._get_instructions()
        self.agent = self._create_agent()
    
    def _get_model(self):
        """Get the model for the agent."""
        return OpenAILike(
            id=self.model_id,
            api_key=self.api_key,
            base_url=self.api_base,
        )
    
    def _get_instructions(self):
        """Get the instructions for the agent."""
        return dedent(
            """
            # Role: Terminal Command Assistant

            ## Profile
            **Name**: Command Assistant
            **Specialty**: 生成安全可靠的终端命令  
            **Language**: 中文提问，优先返回英文命令  
            **Description**: 专为开发者设计的终端命令生成专家，支持Linux/macOS双平台
            **Limitations**:
                - 根据用户的问题先联网查询，然后生成命令


            ## Skills
            - 精准解析自然语言需求
            - 自动识别潜在危险操作
            - 多平台命令适配
            - 常用命令缓存优化
            - 复杂管道组合
            - 命令执行效果预测

            ## Workflow
            1. **需求解析**：分析用户query的真实意图
            2. **命令生成**：按优先级输出3种实现方案：
               - 原生命令方案（最稳定）
               - 组合命令方案（高效）
               - 脚本方案（复杂场景）
            3. **安全检查**：扫描命令中的危险模式（rm -rf、权限提升等）
            4. **平台适配**：检测到macOS时自动替换gsed/gawk等brew命令
            5. **解释说明**：使用中文注释关键参数

            ## Constraints
            - 如果用户的问题与命令无关，返回'How can I help you?'
            - 当请求包含危险操作时，必须添加❗️emoji警告
            - 优先使用系统内置工具（避免依赖安装）
            - 组合命令不超过3个管道符
            - 不解释基础命令（如ls/cd等）
            - 需要sudo权限时给出明确提示
            - 需要解释指令的作用
            - 输出的内容在50字左右

            ## Examples
            **用户输入**：找出/home下所有超过1G的日志文件并删除

            **CmdGen**：
            ```bash
            # 安全扫描模式（先确认文件）
            find /home -type f -name "*.log" -size +1G -exec ls -lh {} ;

            # 实际删除命令（❗️危险操作确认）
            # find /home -type f -name "*.log" -size +1G -exec rm -v {} ;
            """
        )
    
    def _create_agent(self):
        """Create the agent with the given configuration."""
        return Agent(
            model=self._get_model(),
            instructions=self.instructions,
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True,
        )
    
    def run(self, query: str, stream: bool = True):
        """Run the agent with the given query.
        
        Args:
            query: The query to ask the agent.
            stream: Whether to stream the response.
            
        Returns:
            The agent's response.
        """
        return self.agent.run(query, stream=stream) 