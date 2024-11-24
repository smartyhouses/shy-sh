from shy_sh.agents.tools.shell import shell
from shy_sh.agents.tools.shell_expert import shell_expert
from shy_sh.agents.tools.python_expert import python_expert
from shy_sh.agents.tools.shell_history import shell_history

tools = [shell, shell_expert, python_expert, shell_history]
tools_by_name = {tool.name: tool for tool in tools}
