from rich import print
from rich.live import Live
from shy_sh.agents.shy_agent.graph import shy_agent_graph
from shy_sh.agents.misc import get_graph_inputs, run_few_shot_examples
from shy_sh.agents.chains.screenshot import screenshot_chain
from langchain_core.messages import HumanMessage


class ShyAgent:
    def __init__(
        self,
        interactive=False,
        ask_before_execute=True,
        screenshot=False,
    ):
        self.interactive = interactive
        self.ask_before_execute = ask_before_execute
        self.screenshot = screenshot
        self.history = []
        self.examples = run_few_shot_examples()

    def _update_task_with_image(self, task: str):
        print(f"📸 [bold yellow]Taking a screenshot...[/bold yellow]\n")
        result = ""
        with Live() as live:
            for chunk in screenshot_chain.stream(
                {"input": task, "history": self.history}
            ):
                result += chunk
                live.update(f"[grey42]👀 {result}[/]", refresh=True)
        print()
        return f"\nContext informations - This is what I'm seeing in my screen right now:\n{result}\n\nTask: {task}"

    def _run(self, task: str):
        self.history.append(HumanMessage(content=task))
        if self.screenshot:
            task = self._update_task_with_image(task)
            self.screenshot = False
        inputs = get_graph_inputs(
            history=self.history,
            examples=self.examples,
            ask_before_execute=self.ask_before_execute,
        )

        res = shy_agent_graph.invoke(inputs)
        self.history += res["tool_history"]

    def start(self, task: str):
        if task:
            self._run(task)
        if self.interactive:
            new_task = input("\n✨: ")
            if new_task == "exit":
                print("\n🤖: 👋 Bye!\n")
                return

            if new_task.startswith("/screen"):
                new_task = new_task.replace("/screen", "", 1).strip()
                self.screenshot = True

            self.start(new_task)
