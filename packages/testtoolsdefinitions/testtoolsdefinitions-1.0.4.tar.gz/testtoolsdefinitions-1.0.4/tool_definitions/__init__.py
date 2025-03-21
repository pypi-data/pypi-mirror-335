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

# Add tool functions to the module's namespace
globals().update({tool.name: tool.func for tool in tools})

# Define the public interface of the module
__all__ = ["tools", "tools_dict","list_job_executions"] + [tool.name for tool in tools]
