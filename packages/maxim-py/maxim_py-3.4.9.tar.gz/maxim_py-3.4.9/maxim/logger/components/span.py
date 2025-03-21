from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..writer import LogWriter
from .base import EventEmittingBaseContainer
from .generation import Generation, GenerationConfig
from .retrieval import Retrieval, RetrievalConfig
from .tool_call import ToolCall, ToolCallConfig
from .trace import Trace
from .types import Entity


@dataclass
class SpanConfig:
    id: str
    name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class Span(EventEmittingBaseContainer):
    ENTITY = Entity.SPAN

    def __init__(self, config: SpanConfig, writer: LogWriter):
        super().__init__(self.ENTITY, config.__dict__, writer)
        self.traces: List[Trace] = []

    def span(self, config: SpanConfig):
        span = Span(config, self.writer)
        span.span_id = self.id
        self._commit(
            "add-span",
            {
                "id": config.id,
                **span.data(),
            },
        )
        return span

    def input(self, input: str):
        self._commit("update", {input: {"type": "text", "value": input}})

    @staticmethod
    def input_(writer: LogWriter, span_id: str, input: str):
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "update",
            {"input": {"type": "text", "value": input}},
        )

    def output(self, output: str):
        self._commit("update", {output: {"type": "text", "value": output}})

    @staticmethod
    def output_(writer: LogWriter, span_id: str, output: str):
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "update",
            {"output": {"type": "text", "value": output}},
        )

    @staticmethod
    def span_(writer: LogWriter, span_id: str, config: SpanConfig):
        span = Span(config, writer)
        span.span_id = span_id
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "add-span",
            {
                "id": config.id,
                **span.data(),
            },
        )
        return span

    def generation(self, config: GenerationConfig) -> Generation:
        generation = Generation(config, self.writer)
        payload = generation.data()
        payload["id"] = config.id
        payload["spanId"] = self.id
        self._commit(
            "add-generation",
            {
                **payload,
            },
        )
        return generation

    def tool_call(self, config: ToolCallConfig) -> ToolCall:
        tool_call = ToolCall(config, self.writer)
        self._commit(
            "add-tool-call",
            {
                **tool_call.data(),
                "id": tool_call.id,
            },
        )
        return tool_call

    @staticmethod
    def tool_call_(writer: LogWriter, span_id: str, config: ToolCallConfig) -> ToolCall:
        tool_call = ToolCall(config, writer)
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "add-tool-call",
            {
                **tool_call.data(),
                "id": tool_call.id,
            },
        )
        return tool_call

    @staticmethod
    def generation_(
        writer: LogWriter, span_id: str, config: GenerationConfig
    ) -> Generation:
        generation = Generation(config, writer)
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "add-generation",
            {
                **generation.data(),
                "id": config.id,
            },
        )
        return generation

    def retrieval(self, config: RetrievalConfig):
        retrieval = Retrieval(config, self.writer)
        self._commit(
            "add-retrieval",
            {
                "id": config.id,
                **retrieval.data(),
            },
        )
        return retrieval

    @staticmethod
    def retrieval_(writer: LogWriter, span_id: str, config: RetrievalConfig):
        retrieval = Retrieval(config, writer)
        Span._commit_(
            writer,
            Entity.SPAN,
            span_id,
            "add-retrieval",
            {
                "id": config.id,
                **retrieval.data(),
            },
        )
        return retrieval

    @staticmethod
    def end_(writer: LogWriter, span_id: str, data: Optional[Dict[str, str]] = None):
        if data is None:
            data = {}
        return EventEmittingBaseContainer._end_(
            writer,
            Entity.SPAN,
            span_id,
            {"endTimestamp": datetime.now(timezone.utc), **data},
        )

    @staticmethod
    def add_tag_(writer: LogWriter, span_id: str, key: str, value: str):
        return EventEmittingBaseContainer._add_tag_(
            writer, Entity.SPAN, span_id, key, value
        )

    @staticmethod
    def event_(
        writer: LogWriter,
        span_id: str,
        id: str,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        return EventEmittingBaseContainer._event_(
            writer, Entity.SPAN, span_id, id, name, tags, metadata
        )
