import asyncio
from .agent import Agent


# a runner is just an agent that surface create agent messages
# rather than posts.
class Runner(Agent):
    async def _message_thread(self):
        poll_interval_ms = 100

        if self.blackboard_start_idx == -1:
            bb_length = await self._len()
            self.log_local(f"skipping {bb_length} messages on blackboard")
            self.blackboard_start_idx = bb_length
            self.last_msg_idx = self.blackboard_start_idx - 1

        while not self._stopped() and not self.graceful_exit_mgr.exit_now:
            await asyncio.sleep(poll_interval_ms / 1000)
            # msgs = await self._get_messages(self.last_msg_idx + 1)  # list of messages
            msgs = await self._slice(self.last_msg_idx + 1, 0)  # list of messages

            if len(msgs) > 0:
                for msg in msgs:
                    msg_type = msg.WhichOneof("contents")

                    # NOTE: it would be easy to implement a runner that also
                    # listens for post types, but then your filter chain would need to be adapted
                    # in this case, I'm going to be a little permissive since
                    # if msg_type == "post":
                    #     await self.incoming.put(msg)
                    if msg_type == "createAgent":
                        await self.incoming.put(msg.createAgent)
                    elif msg_type == "halt":
                        return

                    self.last_msg_idx = msg.index

        self.log_local(f"runner {self.name} message thread exited")
