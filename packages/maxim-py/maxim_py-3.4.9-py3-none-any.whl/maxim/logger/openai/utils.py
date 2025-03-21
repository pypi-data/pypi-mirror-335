from typing import Any, Dict, Iterable, List, Optional, Union
import time

from openai.types.chat import ChatCompletion, ChatCompletionChunk

from ..logger import GenerationRequestMessage


class OpenAIUtils:
    @staticmethod
    def parse_message_param(
        messages: Iterable[Dict[str, Any]],
        override_role: Optional[str] = None,
    ) -> List[GenerationRequestMessage]:
        parsed_messages: List[GenerationRequestMessage] = []
        
        for msg in messages:
            role = override_role or msg.get("role", "user")
            content = msg.get("content", "")
            
            if isinstance(content, list):
                # Handle content blocks for multimodal
                text_content = ""
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_content += block.get("text", "")
                parsed_messages.append(
                    GenerationRequestMessage(
                        role=role,
                        content=text_content
                    )
                )
            else:
                parsed_messages.append(
                    GenerationRequestMessage(
                        role=role,
                        content=str(content)
                    )
                )
        
        return parsed_messages

    @staticmethod
    def get_model_params(
        max_tokens: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        model_params = {}
        
        if max_tokens is not None:
            model_params["max_tokens"] = max_tokens
            
        param_keys = ["temperature", "top_p", "presence_penalty", "frequency_penalty", "response_format"]
        for key in param_keys:
            if key in kwargs and kwargs[key] is not None:
                model_params[key] = kwargs[key]
                
        for key, value in kwargs.items():
            if key not in param_keys and value is not None:
                model_params[key] = value
                
        return model_params

    @staticmethod
    def parse_stream_response(
        chunk: ChatCompletionChunk,
    ) -> Dict[str, Any]:
        return {
            "id": chunk.id,
            "created": int(time.time()),
            "choices": [{
                "index": choice.index,
                "delta": {
                    "role": "assistant",
                    "content": choice.delta.content or "",
                },
                "finish_reason": choice.finish_reason
            } for choice in chunk.choices],
        }

    @staticmethod
    def parse_completion(
        completion: ChatCompletion,
    ) -> Dict[str, Any]:
        return {
            "id": completion.id,
            "created": int(time.time()),
            "choices": [{
                "index": choice.index,
                "message": {
                    "role": "assistant",
                    "content": choice.message.content,
                },
                "finish_reason": choice.finish_reason
            } for choice in completion.choices],
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                "total_tokens": completion.usage.total_tokens if completion.usage else 0
            }
        }