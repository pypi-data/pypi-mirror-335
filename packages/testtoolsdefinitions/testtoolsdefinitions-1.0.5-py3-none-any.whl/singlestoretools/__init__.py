from .definitions import tools_definitions

class Tool:
    def __init__(self, name, description, func, inputSchema):
        self.name = name
        self.description = description
        self.func = func
        self.inputSchema = inputSchema

# Export the tools
tools = [
    Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["func"],
        inputSchema=tool["inputSchema"]
    )
    for tool in tools_definitions
]

# Create a dictionary for easy access to individual tools by name
tools_dict = {tool.name: tool for tool in tools}

# Create instances and add to module namespace
for tool in tools_definitions:
    tool_instance = Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["func"],
        input_schema=tool["inputSchema"]
    )
    # Make the tool available at module level
    globals()[tool["name"]] = tool_instance


# Export all tool names
__all__ = ["tools", "tools_dict"] + [tool["name"] for tool in tools_definitions]
