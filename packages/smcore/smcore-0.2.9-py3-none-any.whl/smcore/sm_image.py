import numpy as np
from typing import Iterable

from . import deserialize, serialize
from .agent import Agent
from .post import Post


class SMImage:
    """A permissive image container class for use with Simple Mind agents

    SMImage is intended to help standardize access patterns to common
    structured imaging data often found in medical imaging. It also
    provides convenience methods for transmitting SMImages over a
    core blackboard.

    SMImage is not intended to provide image manipulation functionality
    such as pre or postprocessing, which is intentionally delegated
    to the agents that will utilize SMImages.

    SMImage is also intentionally backed-by and shared using data types
    that are widely available, and do not require access to the SMImage
    class itself. For instance, metadata is posted as JSON and image data
    is provided using (de)serialized (smcore/serialize.py) numpy arrays.

    This design allows for simple agents to interact with only the portions
    of data they care about, using minimal standard tooling (e.g, import json)
    when possible.  At this stage, this is a design goal for this class.

    Finally, SMImage should be understood to be permissive.  We favor returning
    empty values or error values, rather than requiring strict adherence to
    specific metadata patterns.  Most medical imaging metadata is highly
    inconsistent and we want to favor running, functional pipelines over

    This implementation is experimental and evolving and is open to
    feedback.
    """

    sm_image_tag = "sm-image-data"

    @classmethod
    def from_post(cls, post: Post):
        """Create and return an SMImage instance from an smcore.Post"""
        # WARN: this is likely not necessary and serves to just block execution
        # that might otherwise be able to happen. Early on though, I think this
        # particular runtime error should help better guide users to get their
        # tags correctly matched during agent development, but eventually would
        # be good to remove.
        if cls.sm_image_tag not in post.tags():
            raise RuntimeError(
                f"required tag for SMImage from_post {cls.sm_image_tag} not found."
            )

        metadata = deserialize.dictionary(post.metadata)
        image = deserialize.numpy(post.data)

        return SMImage(metadata, image, None)  # image w/o label

    @classmethod
    def tag(cls) -> str:
        """Return the canonical tag for an SMImage post"""
        return cls.sm_image_tag

    @classmethod
    def _test_image(cls):
        metadata = {"origin": (0, 0, 0), "spacing": (0.5, 0.5, 0.5)}
        image = np.random.rand(1, 512, 512)
        label = None
        return cls(metadata, image, label)

    def _to_post(self) -> Post:
        """for testing. not stable."""
        p = Post()
        p.metadata = serialize.dictionary(self.metadata)
        p.data = serialize.numpy(self.image)
        p.labels = [self.tag()]

        return p

    def __init__(self, metadata: dict, image: np.ndarray, label: np.ndarray):
        # intended for image header information # specify degrees of compliance
        self.metadata = metadata
        self.image = image  # image array only (no mask)
        self.mask = None  # smae dimension as image, but a mask
        self.label = label  # Anything truthy

    async def post_with_agent(self, agent: Agent, *tags):
        """Utilize a user-provided agent to post an SMImage

        This is a convenience method to simplify posting SMImages
        to the blackboard, standardizing how we intend to serialize
        our data. Using this method also enforces consistent tagging.

        Utilizing this method is not required, however may prove useful
        for new users.
        """
        metadata = serialize.dictionary(self.metadata)
        data = serialize.numpy(self.image)

        # Generate the full list of tags

        await agent.post(
            metadata,
            data,
            SMImage.tag(),
            *tags,
        )

    async def reply_with_agent(self, posts: Iterable[Post], agent: Agent, *tags):
        metadata = serialize.dictionary(self.metadata)
        data = serialize.numpy(self.image)

        await agent.reply(
            posts,
            metadata,
            data,
            SMImage.tag(),
            *tags,
        )

    ###########################################################################
    # SMImage-like object API
    ###########################################################################

    def spacing(self) -> tuple:
        """Returns the spacing of the image with numpy ordering: (z, y, x)."""
        if "spacing" in self.metadata:
            return tuple(self.metadata["spacing"][::-1])
        return None

    def origin(self) -> tuple:
        """Returns the origin of the image with numpy ordering: (z, y, x)."""
        if "origin" in self.metadata:
            return tuple(self.metadata["origin"][::-1])
        return None
