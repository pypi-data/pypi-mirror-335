# server.py
from mcp.server.fastmcp import FastMCP
import requests
import json

# Create an MCP server
mcp = FastMCP("SlicerMCP")

SLICER_WEB_SERVER_URL = "http://localhost:2016/slicer"

# Add list_nodes tool
@mcp.tool()
def list_nodes(filter_type: str = "names", class_name: str = None, 
              name: str = None, id: str = None) -> dict:
    """
    通过 Slicer Web Server API 列出 MRML 节点。

    filter_type 参数指定要检索的节点信息的类型。
    可选值包括 "names" (节点名称), "ids" (节点 ID), 和 "properties" (节点属性)。
    默认值为 "names"。

    class_name, name, 和 id 参数是可选的，可用于进一步过滤节点。
    class_name 参数允许按类名筛选节点。
    name 参数允许按名称筛选节点。
    id 参数允许按 ID 筛选节点。

    例如：
    - 列出所有节点的名称：{"tool": "list_nodes", "arguments": {"filter_type": "names"}}
    - 列出特定类别的节点的 ID：{"tool": "list_nodes", "arguments": {"filter_type": "ids", "class_name": "vtkMRMLModelNode"}}
    - 列出具有特定名称的节点的属性：{"tool": "list_nodes", "arguments": {"filter_type": "properties", "name": "MyModel"}}
    - 列出具有特定 ID 的节点：{"tool": "list_nodes", "arguments": {"filter_type": "ids", "id": "vtkMRMLModelNode123"}}

    返回一个包含节点信息的字典。
    如果 filter_type 是 "names" 或 "ids"，则返回的字典包含一个 "nodes" 键，其值为包含节点名称或 ID 的列表。
    例如：{"nodes": ["node1", "node2", ...]} 或 {"nodes": ["id1", "id2", ...]}
    如果 filter_type 是 "properties"，则返回的字典包含一个 "nodes" 键，其值为包含节点属性的字典。
    例如：{"nodes": {"node1": {"property1": "value1", "property2": "value2"}, ...}}
    如果发生错误，则返回一个包含 "error" 键的字典，其值为描述错误的字符串。
    """
    try:
        # Build API endpoint based on filter type
        endpoint_map = {
            "names": "/mrml/names",
            "ids": "/mrml/ids",
            "properties": "/mrml/properties"
        }
        
        if filter_type not in endpoint_map:
            return {"error": "Invalid filter_type specified"}
            
        api_url = f"{SLICER_WEB_SERVER_URL}{endpoint_map[filter_type]}"
        
        # Build query parameters
        params = {}
        if class_name:
            params["class"] = class_name
        if name:
            params["name"] = name
        if id:
            params["id"] = id

        # Send GET request to Slicer Web Server
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        # Process response based on filter type
        if filter_type == "properties":
            return {"nodes": response.json()}
            
        return {"nodes": response.json()}

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Node listing failed: {str(e)}"}


# Add execute_python_code tool
@mcp.tool()
def execute_python_code(code: str) -> dict:
    """
    在 3D Slicer 中执行 Python 代码。
    
    Parameters:
    code (str): The Python code to execute.

    code 参数是要执行的 Python 代码字符串。
    该代码将在 3D Slicer 的 Python 环境中执行。

    例如：
    - 创建一个球体模型：{"tool": "execute_python_code", "arguments": {"code": "import slicer; sphere = slicer.vtkMRMLModelNode(); slicer.mrmlScene.AddNode(sphere); sphere.SetName('MySphere');"}}
    - 获取当前场景中的节点数：{"tool": "execute_python_code", "arguments": {"code": "len(slicer.mrmlScene.GetNodes())"}}

    返回一个包含执行结果的字典。
    如果代码执行成功，字典将包含一个 "result" 键，其值为执行结果。
    例如：{"result": 5}
    如果代码执行失败，字典将包含一个 "error" 键，其值为包含错误消息的字符串。
    例如：{"error": "NameError: name 'slicer' is not defined"}
    """
    api_url = f"{SLICER_WEB_SERVER_URL}/exec"
    headers = {'Content-Type': 'text/plain'}
    try:
        response = requests.post(api_url, data=code.encode('utf-8'), headers=headers)
        result_data = response.json()
        
        if not result_data.get("success", True):
            # 直接返回服务器提供的错误信息
            return {"error": result_data.get("message", "Unknown Python execution error")}
            
        return {"result": result_data.get("__execResult", result_data)}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
