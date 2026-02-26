from typing import Optional, Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client, streamable_http_client
from mcp.types import CallToolResult, TextContent, GetPromptResult, ReadResourceResult, Resource, TextResourceContents, BlobResourceContents, Prompt, ListResourcesResult, ListPromptsResult
from pydantic import AnyUrl
import json

class MCPClient:
    """Handles MCP server connection and tool execution"""

    def __init__(self, mcp_server_url: str) -> None:
        self.mcp_server_url = mcp_server_url
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

    async def __aenter__(self):
        #TODO:
        # 1. Call `streamablehttp_client` method with `mcp_server_url` and assign to `self._streams_context`
        # 2. Call `await self._streams_context.__aenter__()` and assign to `read_stream, write_stream, _`
        # 3. Create `ClientSession(read_stream, write_stream)` and assign to `self._session_context`
        # 4. Call `await self._session_context.__aenter__()` and assign it to `self.session`
        # 5. Call `self.session.initialize()`, and print its result (to check capabilities of MCP server later)
        # 6. return self
        self._streams_context = streamable_http_client(self.mcp_server_url)
        read_stream, write_stream, _ = await self._streams_context.__aenter__()
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()
        capabilities = await self.session.initialize()
        print(f"Connected to MCP server with capabilities: {capabilities.model_dump_json(indent=2)}")
        return self
        

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        #TODO:
        # This is shutdown method.
        # If session is present and session context is present as well then shutdown the session context (__aexit__ method with params)
        # If streams context is present then shutdown the streams context (__aexit__ method with params)
        if (self.session and self._session_context):
            await self._session_context.__aexit__(exc_type, exc_val, exc_tb)
        if self._streams_context:
            await self._streams_context.__aexit__(exc_type, exc_val, exc_tb)

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get available tools from MCP server"""
        if not self.session:
            raise RuntimeError("MCP client not connected. Call connect() first.")
        #TODO:
        # 1. Call `await self.session.list_tools()` and assign to `tools`
        # 2. Return list with dicts with tool schemas. It should be provided according to DIAL specification
        #    https://dialx.ai/dial_api#operation/sendChatCompletionRequest (request -> tools)
       
        tools_list = await self.session.list_tools()
        tools = [{
            "type": "function",
            "function":{
                "name": tool.name,
                "description": tool.description if tool.description else None,
                "parameters": tool.inputSchema if tool.inputSchema else None
            }
        } for tool in tools_list.tools]

        return tools
    
    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server"""
        if not self.session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        #TODO:
        # 1. Call `await self.session.call_tool(tool_name, tool_args)` and assign to `tool_result: CallToolResult` variable
        # 2. Get `content` with index `0` from `tool_result` and assign to `content` variable
        # 3. print(f"    ⚙️: {content}\n")
        # 4. If `isinstance(content, TextContent)` -> return content.text
        #    else -> return content
        tool_result: CallToolResult = await self.session.call_tool(tool_name, tool_args)
        content = tool_result.content[0]
        print(f"    ⚙️: {content}\n")

        if isinstance(content, TextContent):
            return content.text
        return content

    async def get_resources(self) -> list[Resource]:
        """Get available resources from MCP server"""
        if not self.session:
            raise RuntimeError("MCP client not connected.")
        #TODO:
        # Wrap into try/except (not all MCP servers have resources), get `list_resources` (it is async) and resources
        # from it. In case of error print error and return an empty array
        try:
            resources_result: ListResourcesResult = await self.session.list_resources()
            return resources_result.resources
        except Exception as e:
            print(f"Error fetching resources: {e}")
            return []

    async def get_resource(self, uri: AnyUrl) -> str:
        """Get specific resource content"""
        if not self.session:
            raise RuntimeError("MCP client not connected.")

        #TODO:
        # 1. Get resource by uri (uri is that we provided on the Server side "users-management://flow-diagram")
        # 2. Get contents of [0] resource
        # 3. ResourceContents has 2 types TextResourceContents and BlobResourceContents, in case if content is instance
        #    of TextResourceContents return it is `text`, in case of BlobResourceContents return it is `blob`
        # ---
        # Optional: Later on in app.py you can try to fetch resource and print it (in our case it is image/png provided
        # as bytes, but you can return on the server side some dict just to check how resources are looks like).
        resource = await self.session.read_resource(uri)
        resource_content = resource.contents[0]
        
        if (isinstance(resource_content, TextResourceContents)):
            return resource_content.text
        elif (isinstance(resource_content, BlobResourceContents)):
            return resource_content.blob
        
        raise ValueError("Unknown resource content type")

    async def get_prompts(self) -> list[Prompt]:
        """Get available prompts from MCP server"""
        if not self.session:
            raise RuntimeError("MCP client not connected.")
        #TODO:
        # Wrap into try/except (not all MCP servers have prompts), get `list_prompts` (it is async) and prompts
        # from it. In case of error print error and return an empty array
        try:
            prompts_result: ListPromptsResult = await self.session.list_prompts()
            return prompts_result.prompts
        except Exception as e:
            print(f"Error fetching prompts: {e}")
            return []

    async def get_prompt(self, name: str) -> str:
        """Get specific prompt content"""
        if not self.session:
            raise RuntimeError("MCP client not connected.")
        #TODO:
        # 1. Get prompt by name
        # 2. Create variable `combined_content` with empty string
        # 3. Iterate through prompt result `messages` and:
        #       - if `message` has attribute 'content' and is instance of TextContent then concat `combined_content`
        #          with `message.content.text + "\n"`
        #       - if `message` has attribute 'content' and is instance of `str` then concat `combined_content` with
        #          with `message.content + "\n"`
        # 4. Return `combined_content`
        prompt = await self.session.get_prompt(name)
        combined_content = ""
        for message in prompt.messages:
            if hasattr(message, "content"):
                if isinstance(message.content, TextContent):
                    combined_content += message.content.text + "\n"
                elif isinstance(message.content, str):
                    combined_content += message.content + "\n"
        return combined_content