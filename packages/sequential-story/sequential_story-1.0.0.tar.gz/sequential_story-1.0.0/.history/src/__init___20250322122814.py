"""Sequential Story MCP Server package."""

__submodules__ = ["server", "story_processor"]

import lazy_loader


__getattr__, __dir__, __all__ = lazy_loader.attach_stub(__name__, __file__)

__all__ = ['ContentItem', 'ProcessResult', 'SequentialStoryProcessor',
           'SequentialStoryServer', 'StoryElementData', 'server',
           'story_processor']
