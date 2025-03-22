from mcp.server.fastmcp import FastMCP
from .fsprojclient import FSProjClient
from typing import Literal
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 检查必需的环境变量
required_env_vars = [
    "FS_PROJ_PROJECT_KEY",
    "FS_PROJ_USER_KEY",
    "FS_PROJ_PLUGIN_ID",
    "FS_PROJ_PLUGIN_SECRET"
]

missing_vars = []
for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"错误: 缺少以下必需的环境变量: {', '.join(missing_vars)}")
    print("请确保这些环境变量已在.env文件中设置或已在系统环境中定义")
    sys.exit(1)

mcp = FastMCP("feishuproj-mcp-server")

client = FSProjClient(
    os.getenv("FS_PROJ_BASE_URL", "https://project.feishu.cn/"),
    project_key=os.getenv("FS_PROJ_PROJECT_KEY"),
    user_key=os.getenv("FS_PROJ_USER_KEY"),
    plugin_id=os.getenv("FS_PROJ_PLUGIN_ID"),
    plugin_secret=os.getenv("FS_PROJ_PLUGIN_SECRET"),
)

@mcp.tool("get_view_list")
def get_view_list(work_item_type_key: Literal["story","version","issue"]):
    """获取飞书项目视图列表
    Args:
        work_item_type_key: 工作项类型"
    """    
    client.get_plugin_token()
    return client.get_view_list(work_item_type_key)

def test():
    view_list = get_view_list("story")
    print(view_list)

if __name__ == "__main__":
    test()
