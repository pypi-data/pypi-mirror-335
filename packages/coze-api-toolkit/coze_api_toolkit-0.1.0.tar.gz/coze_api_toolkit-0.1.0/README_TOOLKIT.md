# Coze API 简化工具包

## 项目简介

这是一个用于调用 Coze 工作流 API 的简化 Python 工具包，专注于提供纯粹的 API 封装，让您只需关注业务逻辑而不必处理复杂的 API 调用细节。

## 设计理念

该工具包采用了极简的设计理念：

1. **API 客户端层**：负责与 Coze API 通信，处理认证和基础调用
2. **函数式 API 层**：提供简单直接的函数调用，无需实例化对象

这种设计带来以下优势：

- **极简接口**：每个 API 就是一个函数，调用直观明了
- **纯数据输出**：API 只负责获取数据，不进行额外处理
- **业务分离**：下载、保存、格式化等功能由业务层自行处理

## 核心功能

- 关键词生成图片：输入关键词，输出图片 URL 列表

## 使用方法

### API 令牌配置

在使用 API 前，您需要配置有效的 Coze API 令牌。工具包支持以下几种方式：

1. **直接传入令牌**：在调用函数时直接提供令牌
   ```python
   image_urls = get_imgs_by_key(prompt="一只猫", token="您的API令牌")
   ```

2. **环境变量**：设置 `COZE_API_TOKEN` 环境变量
   ```bash
   # Linux/Mac
   export COZE_API_TOKEN="您的API令牌"
   
   # Windows
   set COZE_API_TOKEN=您的API令牌
   ```

3. **配置文件**：创建配置文件 `~/.coze/config.json`
   ```json
   {
     "token": "您的API令牌"
   }
   ```

工具包会按照以下顺序查找令牌：
1. 函数参数 `token`
2. 环境变量 `COZE_API_TOKEN`
3. 配置文件 `~/.coze/config.json`

### 关键词生成图片

```python
from api.get_imgs_by_key import get_imgs_by_key

# 方式1：使用函数参数传入令牌
image_urls = get_imgs_by_key(prompt="一只可爱的猫", token="您的API令牌")

# 方式2：从环境变量或配置文件加载令牌
image_urls = get_imgs_by_key(prompt="一只可爱的猫")

# 处理结果
for url in image_urls:
    print(url)
    # 在这里处理 URL，如下载图片
```

## 目录结构

```
coze_api_toolkit/
├── config/               # 配置文件
│   └── api_catalog.json    # API 接口配置
├── core/                 # 核心实现
│   └── api_client.py       # API 客户端
├── api/                  # API 实现
│   └── get_imgs_by_key.py  # 图片生成API函数
└── examples/             # 使用示例
    ├── simple_example.py   # 命令行示例
    └── gui_example.py      # GUI示例
```

## 扩展开发

### 添加新的 API

只需创建一个新的 API 函数：

```python
from typing import Dict, Any
from core.api_client import CozeAPIClient

# API客户端实例将在首次调用时创建
_api_client = None

def new_api_function(param1: str, param2: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    新API函数的描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
        token: 可选的API令牌
        
    Returns:
        Dict[str, Any]: 返回结果描述
    """
    global _api_client
    
    # 如果提供了新令牌或客户端未初始化，则创建新客户端
    if _api_client is None or token is not None:
        _api_client = CozeAPIClient(token=token)
    
    # 调用API
    response = _api_client.call_workflow(
        workflow_id="YOUR_WORKFLOW_ID",
        parameters={"input1": param1, "input2": param2}
    )
    
    # 提取结果
    result = _api_client.extract_data(response, "data.output")
    return result
```

## 与业务系统集成

该工具包专注于 API 调用，可以轻松与您的业务系统集成：

```python
# 在您的业务代码中
from api.get_imgs_by_key import get_imgs_by_key
import requests
from PIL import Image
from io import BytesIO

def download_and_process_images(prompt, token=None):
    # 1. 调用 API 获取图片 URL
    image_urls = get_imgs_by_key(prompt, token=token)
    
    # 2. 下载图片（业务逻辑）
    images = []
    for url in image_urls:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        images.append(img)
    
    # 3. 处理图片（业务逻辑）
    for img in images:
        # 进行图片处理...
        img.thumbnail((200, 200))
        img.save(f"thumbnail_{len(images)}.png")
    
    return images
```

## 注意事项

- 请妥善保管您的 API 令牌，不要将其硬编码在源代码中或提交到公共仓库
- 工作流 ID 已在 API 函数中固定
- 遵循 Coze API 的使用限制和政策 