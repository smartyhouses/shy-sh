from shy_sh.agents.tools.shell import shell
from shy_sh.agents.tools.shell_expert import shell_expert
from shy_sh.agents.tools.python_expert import python_expert

tools = [shell, shell_expert, python_expert]
tools_by_name = {tool.name: tool for tool in tools}
