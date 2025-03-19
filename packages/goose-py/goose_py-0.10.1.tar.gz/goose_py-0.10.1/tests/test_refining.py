import random
import string

import pytest

from goose import Agent, FlowArguments, Result, flow, task
from goose._internal.types.agent import MessagePart
from goose.agent import SystemMessage, UserMessage
from goose.errors import Honk


class MyFlowArguments(FlowArguments):
    pass


class GeneratedWord(Result):
    word: str


class GeneratedSentence(Result):
    sentence: str


@task
async def generate_random_word(*, n_characters: int) -> GeneratedWord:
    return GeneratedWord(word="".join(random.sample(string.ascii_lowercase, n_characters)))


@task
async def make_sentence(*, words: list[GeneratedWord]) -> GeneratedSentence:
    return GeneratedSentence(sentence=" ".join([word.word for word in words]))


@flow
async def sentence(*, flow_arguments: MyFlowArguments, agent: Agent) -> None:
    words = [await generate_random_word(n_characters=10) for _ in range(3)]
    await make_sentence(words=words)


@pytest.mark.asyncio
async def test_refining() -> None:
    async with sentence.start_run(run_id="1") as first_run:
        await sentence.generate(MyFlowArguments())

    initial_random_words = first_run.get_all(task=generate_random_word)
    assert len(initial_random_words) == 3

    # imagine this is a new process
    async with sentence.start_run(run_id="1") as second_run:
        result = await generate_random_word.refine(
            user_message=UserMessage(parts=[MessagePart(content="Change it")]),
            context=SystemMessage(parts=[MessagePart(content="Extra info")]),
        )
        # Since refine now directly returns the result from the agent call
        assert isinstance(result, GeneratedWord)

    random_words = second_run.get_all(task=generate_random_word)
    assert len(random_words) == 3
    # Remove the __ADAPTED__ check since that was specific to the old __adapt method
    assert isinstance(random_words[0].result, GeneratedWord)
    assert isinstance(random_words[1].result, GeneratedWord)
    assert isinstance(random_words[2].result, GeneratedWord)


@pytest.mark.asyncio
async def test_refining_before_generate_fails() -> None:
    with pytest.raises(Honk):
        async with sentence.start_run(run_id="2"):
            await generate_random_word.refine(
                user_message=UserMessage(parts=[MessagePart(content="Change it")]),
                context=SystemMessage(parts=[MessagePart(content="Extra info")]),
            )
