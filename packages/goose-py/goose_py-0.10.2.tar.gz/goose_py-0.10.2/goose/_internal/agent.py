import logging
from datetime import datetime
from typing import Any, Literal, Protocol, overload

from litellm import acompletion
from pydantic import ValidationError

from goose._internal.result import FindReplaceResponse, Result, TextResult
from goose._internal.types.agent import AIModel, AssistantMessage, SystemMessage, UserMessage
from goose._internal.types.telemetry import AgentResponse
from goose.errors import Honk


class IAgentLogger(Protocol):
    async def __call__(self, *, response: AgentResponse[Any]) -> None: ...


class Agent:
    def __init__(
        self,
        *,
        flow_name: str,
        run_id: str,
        logger: IAgentLogger | None = None,
    ) -> None:
        self.flow_name = flow_name
        self.run_id = run_id
        self.logger = logger

    async def generate[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        response_model: type[R] = TextResult,
        system: SystemMessage | None = None,
    ) -> R:
        rendered_messages = [message.render() for message in messages]
        rendered_system = system.render() if system is not None else None

        completion_messages = (
            [rendered_system] + rendered_messages if rendered_system is not None else rendered_messages
        )

        start_time = datetime.now()
        if response_model is TextResult:
            response = await acompletion(model=model.value, messages=completion_messages)
            parsed_response = response_model.model_validate({"text": response.choices[0].message.content})
        else:
            response = await acompletion(
                model=model.value,
                messages=completion_messages,
                response_format=response_model,
            )
            parsed_response = response_model.model_validate_json(response.choices[0].message.content)

        end_time = datetime.now()
        agent_response = AgentResponse(
            response=parsed_response,
            run_id=self.run_id,
            flow_name=self.flow_name,
            task_name=task_name,
            model=model,
            system=rendered_system,
            input_messages=rendered_messages,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            start_time=start_time,
            end_time=end_time,
        )

        if self.logger is not None:
            await self.logger(response=agent_response)
        else:
            logging.info(agent_response.model_dump())

        return parsed_response

    async def ask(
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        system: SystemMessage | None = None,
    ) -> str:
        rendered_messages = [message.render() for message in messages]
        rendered_system = system.render() if system is not None else None

        completion_messages = (
            [rendered_system] + rendered_messages if rendered_system is not None else rendered_messages
        )

        start_time = datetime.now()
        response = await acompletion(model=model.value, messages=completion_messages)

        end_time = datetime.now()
        agent_response = AgentResponse(
            response=response.choices[0].message.content,
            run_id=self.run_id,
            flow_name=self.flow_name,
            task_name=task_name,
            model=model,
            system=rendered_system,
            input_messages=rendered_messages,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            start_time=start_time,
            end_time=end_time,
        )

        if self.logger is not None:
            await self.logger(response=agent_response)
        else:
            logging.info(agent_response.model_dump())

        return response.choices[0].message.content

    async def refine[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        response_model: type[R],
        system: SystemMessage | None = None,
    ) -> R:
        start_time = datetime.now()

        rendered_messages = [message.render() for message in messages]
        rendered_system = system.render() if system is not None else None

        completion_messages = (
            [rendered_system] + rendered_messages if rendered_system is not None else rendered_messages
        )

        find_replace_response = await acompletion(
            model=model.value, messages=completion_messages, response_format=FindReplaceResponse
        )
        parsed_find_replace_response = FindReplaceResponse.model_validate_json(
            find_replace_response.choices[0].message.content
        )

        end_time = datetime.now()
        agent_response = AgentResponse(
            response=parsed_find_replace_response,
            run_id=self.run_id,
            flow_name=self.flow_name,
            task_name=task_name,
            model=model,
            system=rendered_system,
            input_messages=rendered_messages,
            input_tokens=find_replace_response.usage.prompt_tokens,
            output_tokens=find_replace_response.usage.completion_tokens,
            start_time=start_time,
            end_time=end_time,
        )

        if self.logger is not None:
            await self.logger(response=agent_response)
        else:
            logging.info(agent_response.model_dump())

        refined_response = self.__apply_find_replace(
            result=self.__find_last_result(messages=messages, response_model=response_model),
            find_replace_response=parsed_find_replace_response,
            response_model=response_model,
        )

        return refined_response

    @overload
    async def __call__[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        mode: Literal["generate"],
        response_model: type[R],
        system: SystemMessage | None = None,
    ) -> R: ...

    @overload
    async def __call__[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        mode: Literal["ask"],
        response_model: type[R] = TextResult,
        system: SystemMessage | None = None,
    ) -> str: ...

    @overload
    async def __call__[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        response_model: type[R],
        mode: Literal["refine"],
        system: SystemMessage | None = None,
    ) -> R: ...

    @overload
    async def __call__[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        response_model: type[R],
        system: SystemMessage | None = None,
    ) -> R: ...

    async def __call__[R: Result](
        self,
        *,
        messages: list[UserMessage | AssistantMessage],
        model: AIModel,
        task_name: str,
        response_model: type[R] = TextResult,
        mode: Literal["generate", "ask", "refine"] = "generate",
        system: SystemMessage | None = None,
    ) -> R | str:
        match mode:
            case "generate":
                return await self.generate(
                    messages=messages, model=model, task_name=task_name, response_model=response_model, system=system
                )
            case "ask":
                return await self.ask(messages=messages, model=model, task_name=task_name, system=system)
            case "refine":
                return await self.refine(
                    messages=messages, model=model, task_name=task_name, response_model=response_model, system=system
                )

    def __apply_find_replace[R: Result](
        self, *, result: R, find_replace_response: FindReplaceResponse, response_model: type[R]
    ) -> R:
        dumped_result = result.model_dump_json()
        for replacement in find_replace_response.replacements:
            dumped_result = dumped_result.replace(replacement.find, replacement.replace)

        return response_model.model_validate_json(dumped_result)

    def __find_last_result[R: Result](
        self, *, messages: list[UserMessage | AssistantMessage], response_model: type[R]
    ) -> R:
        for message in reversed(messages):
            if isinstance(message, AssistantMessage):
                try:
                    return response_model.model_validate_json(message.text)
                except ValidationError:
                    continue

        raise Honk("No last result found, failed to refine")
