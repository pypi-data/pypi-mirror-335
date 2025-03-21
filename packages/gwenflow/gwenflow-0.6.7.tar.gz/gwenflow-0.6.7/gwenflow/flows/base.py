
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, model_validator, field_validator, Field

import yaml

from gwenflow.agents import Agent
from gwenflow.tools import Tool, BaseTool
from gwenflow.utils import logger


MAX_TRIALS=5


class Flow(BaseModel):

    agents: List[Agent] = []
    manager: Optional[Agent] = None
    llm: Any = None
    tools: List[BaseTool] = []

    flow_type: str = "sequence"

    @model_validator(mode="after")
    def model_valid(self) -> Any:
        if self.manager is None:
            self.manager = Agent(
                name="Team Manager",
                role="Manage the team to complete the task in the best way possible.",
                instructions= [
                    "You are the leader of a team of AI Agents.",
                    "Even though you don't perform tasks by yourself, you have a lot of experience in the field, which allows you to properly evaluate the work of your team members.",
                    "You must always validate the output of the other Agents and you can re-assign the task if you are not satisfied with the result.",
                ],
                tools=self.tools,
                llm=self.llm,
            )
        return self
        
    @classmethod
    def from_yaml(cls, file: str, tools: List[Tool], llm: Optional[Any] = None) -> "Flow":
        if cls == Flow:
            with open(file) as stream:
                try:
                    agents = []
                    content_yaml = yaml.safe_load(stream)
                    for name in content_yaml.get("agents").keys():

                        _values = content_yaml["agents"][name]

                        _tools = []
                        if _values.get("tools"):
                            _agent_tools = _values.get("tools").split(",")
                            for t in tools:
                                if t.name in _agent_tools:
                                    _tools.append(t)

                        context_vars = []
                        if _values.get("context"):
                            context_vars = _values.get("context")                            

                        agent = Agent(
                            name=name,
                            role=_values.get("role"),
                            description=_values.get("description"),
                            response_model=_values.get("response_model"),
                            tools=_tools,
                            context_vars=context_vars,
                            llm=llm,
                        )
                        agents.append(agent)
                    return Flow(agents=agents)
                except Exception as e:
                    logger.error(repr(e))
        raise NotImplementedError(f"from_yaml not implemented for {cls.__name__}")
    
    def describe(self):
        for agent in self.agents:
            print("---")
            print(f"Agent  : {agent.name}")
            if agent.role:
                print(f"Role   : {agent.role}")
            if agent.context_vars:
                print(f"Context:", ",".join(agent.context_vars))
            if agent.tools:
                available_tools = [ tool.name for tool in agent.tools ]
                print(f"Tools  :", ",".join(available_tools))


    def run(self, user_prompt: str, output_file: Optional[str] = None) -> str:

        outputs = {}

        while len(outputs) < len(self.agents):

            for agent in self.agents:

                # check if already run
                if agent.name in outputs.keys():
                    continue

                # check agent dependancies
                if any(outputs.get(var) is None for var in agent.context_vars):
                    continue

                # prepare context and run
                context = None
                if agent.context_vars:
                    context = { f"{var}": outputs[var].content for var in agent.context_vars }
                
                task = None
                if context is None:
                    task = user_prompt # always keep query if no context (first agents)

                outputs[agent.name] = agent.run(task=task, context=context, output_file=output_file)

                logger.debug(f"# {agent.name}\n{ outputs[agent.name].content }", extra={"markup": True})                

        return outputs
    