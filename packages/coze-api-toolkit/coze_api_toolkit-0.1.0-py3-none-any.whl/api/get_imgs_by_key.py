"""
关键词生成图片API

提供通过关键词生成图片的API功能。
"""
from typing import List, Optional

from core.api_client import CozeAPIClient

# API客户端实例将在首次调用函数时创建
_api_client = None

def get_imgs_by_key(prompt: str, bot_id: Optional[str] = None, token: Optional[str] = None) -> List[str]:
    """
    根据关键词生成图片
    
    Args:
        prompt: 图片描述或关键词
        bot_id: 可选的机器人ID
        token: 可选的API令牌，如果未提供，将尝试从环境变量或配置文件获取
        
    Returns:
        List[str]: 生成的图片URL列表
    """
    global _api_client
    
    # 如果提供了新令牌或客户端未初始化，则创建新客户端
    if _api_client is None or token is not None:
        _api_client = CozeAPIClient(token=token)
    
    # 调用API
    response = _api_client.call_workflow(
        workflow_id="7471274403935059983",
        parameters={"input": prompt},
        bot_id=bot_id
    )
    
    # 提取结果
    result = _api_client.extract_data(response, "data.output")
    
    if not isinstance(result, list):
        raise ValueError(f"生成图片失败：返回结果格式不正确，期望列表，实际为 {type(result)}")
        
    return result 