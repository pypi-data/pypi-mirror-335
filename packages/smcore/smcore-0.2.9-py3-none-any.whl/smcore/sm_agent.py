from .agent import Agent
import uuid
import datetime


# Define a base class that will give us some base behavior we can inherit from
# I'm envisioning that you'll want to do something like this for the FlexAgent
# type to grant some default behaviors
class SMAgent(Agent):
    def __init__(self, blackboard, name, attributes):
        super(SMAgent, self).__init__(blackboard)
        self.name = name
        self.instance = uuid.uuid4().hex
        self.attributes = attributes

    def log_local(self, msg):
        print(f"{datetime.datetime.now().time()} {self.name} => {msg}")

    # async means we need to utilize the concurrent version of things (this is
    # kind of like __del__) But otherwise these are very normal python
    # constructs
    async def __aexit__(self):
        await self.sm_post(
            None, None, "agent-signal", "simple-mind-controller", "agent-shutdown"
        )

    # Auto inject some additional tags when calling this
    # special derived type
    async def sm_post(self, metadata, data, *tags):
        instance_tag = f"instance: {self.instance}"
        name_tag = f"name: {self.name}"
        await self.post(metadata, data, instance_tag, name_tag, *tags)
