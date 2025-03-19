# Coze API 工具包设计文档

## 总体架构

该工具包采用三层架构设计：

```
+-------------------+
| 业务应用层（用户） |
+--------+----------+
         |
         | 调用
         v
+--------+----------+
|   函数式 API 层   |  <- 我们提供的简化接口
+--------+----------+
         |
         | 调用
         v
+--------+----------+
|   API 客户端层    |  <- 底层通信
+--------+----------+
         |
         | 请求/响应
         v
+--------+----------+
|    Coze API      |
+-------------------+
```

## 数据流程

```
用户 -> 调用函数 -> 参数传递 -> API客户端 -> Coze API -> 
       返回结果 -> 数据提取 -> 返回到用户 -> 用户处理数据
```

## API 令牌管理策略

工具包采用了灵活的令牌管理策略，按照以下优先级查找有效的 API 令牌：

1. **函数参数传入**：优先级最高，适用于临时令牌
   ```python
   get_imgs_by_key(prompt="...", token="临时令牌")
   ```

2. **环境变量**：次优先级，适用于开发环境
   ```
   环境变量名: COZE_API_TOKEN
   ```

3. **配置文件**：最低优先级，适用于个人使用环境
   ```
   路径: ~/.coze/config.json
   格式: {"token": "您的令牌"}
   ```

这种多层级的令牌管理策略具有以下优势：
- **灵活性**：用户可根据需要选择合适的配置方式
- **安全性**：避免令牌硬编码在源代码中
- **易用性**：支持持久化配置，减少重复输入

## 关键词生成图片流程

```
+---------------------+     +---------------------+     +---------------------+
|                     |     |                     |     |                     |
| 1. 调用函数接口      | --> | 2. API客户端发送请求 | --> | 3. Coze执行工作流   |
|                     |     |                     |     |                     |
+---------------------+     +---------------------+     +---------------------+
                                                               |
+---------------------+     +---------------------+            |
|                     |     |                     |            |
| 5. 处理图片URL       | <-- | 4. 提取图片URL列表   | <----------+
|                     |     |                     |
+---------------------+     +---------------------+
```

## API 客户端实现

```python
# API令牌获取逻辑
def _get_token(self) -> Optional[str]:
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
        except Exception:
            pass
            
    return None

# 初始化客户端
def __init__(self, token=None, base_url=COZE_CN_BASE_URL):
    self.token = token or self._get_token()
    if not self.token:
        raise ValueError("未找到有效的API令牌")
        
    self.client = Coze(auth=TokenAuth(token=self.token), base_url=base_url)
```

## 函数式API实现

```python
# API客户端实例将在首次调用时创建
_api_client = None

def get_imgs_by_key(prompt: str, token: Optional[str] = None) -> List[str]:
    """根据关键词生成图片"""
    global _api_client
    
    # 如果提供了新令牌或客户端未初始化，则创建新客户端
    if _api_client is None or token is not None:
        _api_client = CozeAPIClient(token=token)
    
    # 调用API
    response = _api_client.call_workflow(
        workflow_id="7471274403935059983",
        parameters={"input": prompt}
    )
    
    # 提取结果
    return _api_client.extract_data(response, "data.output")
```

## 用户调用流程

```python
# 1. 导入函数
from api.get_imgs_by_key import get_imgs_by_key

# 2. 直接调用函数
image_urls = get_imgs_by_key("一只可爱的猫")  # 自动从环境变量或配置文件获取令牌
# 或者：
image_urls = get_imgs_by_key("一只可爱的猫", token="指定令牌")  # 直接传入令牌

# 3. 处理结果
for url in image_urls:
    # 下载或处理图片
    download_image(url)
```

## 错误处理流程

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| 函数调用出错      | --> | API客户端抛出异常 | --> | 用户捕获并处理    |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

## 依赖管理

工具包的核心依赖：
- `cozepy`: Coze Python SDK
- `requests`: HTTP请求库

用户只需安装这些依赖即可使用工具包：
```
pip install cozepy requests
```

## 扩展新API的流程

1. 在 `api/` 目录下创建新的 API 函数文件
2. 使用 `_api_client` 调用相应的工作流
3. 在 `config/api_catalog.json` 中注册新API
4. 更新文档和示例 