"""
Coze API客户端基础层

负责与Coze API进行底层通信，提供基础的API调用能力。
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

class CozeAPIClient:
    """Coze API客户端"""
    
    # 默认配置文件路径
    DEFAULT_CONFIG_PATH = Path.home() / ".coze" / "config.json"
    
    # 环境变量名
    ENV_TOKEN_NAME = "COZE_API_TOKEN"
    
    def __init__(self, token: Optional[str] = None, base_url: str = COZE_CN_BASE_URL):
        """
        初始化API客户端
        
        Args:
            token: API令牌，如果为None，将尝试从环境变量或配置文件获取
            base_url: API基础URL，默认为COZE_CN_BASE_URL
        """
        # 获取令牌
        self.token = token or self._get_token()
        
        if not self.token:
            raise ValueError(
                "未找到有效的API令牌，请通过以下方式之一提供：\n"
                "1. 直接传入token参数\n"
                f"2. 设置环境变量 {self.ENV_TOKEN_NAME}\n"
                f"3. 创建配置文件 {self.DEFAULT_CONFIG_PATH}"
            )
            
        # 初始化客户端
        self.client = Coze(auth=TokenAuth(token=self.token), base_url=base_url)
        
    def _get_token(self) -> Optional[str]:
        """
        从环境变量或配置文件获取令牌
        
        Returns:
            Optional[str]: API令牌，如果未找到则返回None
        """
        # 1. 尝试从环境变量获取
        token = os.environ.get(self.ENV_TOKEN_NAME)
        if token:
            return token
            
        # 2. 尝试从配置文件获取
        if self.DEFAULT_CONFIG_PATH.exists():
            try:
                with open(self.DEFAULT_CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    return config.get("token")
            except (json.JSONDecodeError, IOError):
                pass
                
        return None
        
    def call_workflow(
        self, 
        workflow_id: str, 
        parameters: Dict[str, Any],
        bot_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用工作流API
        
        Args:
            workflow_id: 工作流ID
            parameters: 输入参数
            bot_id: 可选的机器人ID
            
        Returns:
            Dict[str, Any]: 原始API响应结果
        """
        # 准备API调用参数
        api_params = {
            "workflow_id": workflow_id,
            "parameters": parameters
        }
        
        if bot_id:
            api_params["bot_id"] = bot_id
            
        # 调用API
        response = self.client.workflows.runs.create(**api_params)
        
        # 验证响应
        if not response:
            raise ValueError("API响应为空")
        
        if not hasattr(response, 'data'):
            raise ValueError("API响应缺少data字段")
            
        # 返回响应
        return response.__dict__
        
    def extract_data(self, response: Dict[str, Any], path: str) -> Any:
        """
        从响应中提取数据
        
        Args:
            response: API响应结果
            path: 数据路径，格式如 "data.output"
            
        Returns:
            Any: 提取的数据
        """
        try:
            # 分割路径
            keys = path.split('.')
            current = response
            
            # 遍历路径
            for key in keys:
                if current is None:
                    return None
                    
                # 如果当前值是字符串，尝试解析为JSON
                if isinstance(current, str):
                    try:
                        current = json.loads(current)
                    except json.JSONDecodeError:
                        return None
                
                # 如果当前值是字典，获取指定的键
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return None
                    
            return current
        except Exception as e:
            raise ValueError(f"提取数据失败: {str(e)}") 