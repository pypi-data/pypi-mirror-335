from typing import Sequence

from moxn import base_models
from moxn.models.prompt import Prompt
from pydantic import Field


class Task(base_models._Task):
    prompts: Sequence[Prompt] = Field(default_factory=list)

    def get_prompt_by_name(self, name: str) -> Prompt:
        """Get a prompt by its name"""
        matching = [r for r in self.prompts if r.name == name]
        if not matching:
            raise ValueError(f"No prompt found with name: {name}")
        if len(matching) > 1:
            raise ValueError(f"Multiple prompts found with name: {name}")
        return matching[0]

    def get_prompt_by_id(self, prompt_id: str) -> Prompt:
        """Get a prompt by its ID"""
        matching = [r for r in self.prompts if r.id == prompt_id]
        if not matching:
            raise ValueError(f"No prompt found with ID: {prompt_id}")
        if len(matching) > 1:
            raise ValueError(f"Multiple prompts found with ID: {prompt_id}")
        return matching[0]
