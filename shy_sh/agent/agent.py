from langchain_core.messages import HumanMessage
from rich import print
from shy_sh.agent.graph import graph
from shy_sh.agent.nodes.utils import get_graph_inputs, run_few_shot_examples
from shy_sh.agent.chains.screenshot import screenshot_chain


class ShyAgent:
    def __init__(
        self,
        interactive=False,
        ask_before_execute=False,
        screenshot=False,
    ):
        self.interactive = interactive
        self.ask_before_execute = ask_before_execute
        self.screenshot = screenshot
        self.history = []
        self.examples = run_few_shot_examples()

    def _update_task_with_image(self, task: str):
        result = screenshot_chain(task)
        return f"\nContext informations - This is what I'm seeing in my screen right now:\n{result}\n\nTask: {task}"

    def _run(self, task: str):
        if self.screenshot:
            task = self._update_task_with_image(task)
            self.screenshot = False
        inputs = get_graph_inputs(
            task=task,
            history=self.history,
            examples=self.examples,
            ask_before_execute=self.ask_before_execute,
        )

        res = graph.invoke(inputs)
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
