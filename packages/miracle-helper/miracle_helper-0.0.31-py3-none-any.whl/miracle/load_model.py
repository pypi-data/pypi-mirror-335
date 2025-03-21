import os
from typing import Optional, Literal, Dict, Any

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings, VoyageAIRerank

from miracle.Custom.EnhancedVoyageAIEmbeddings import EnhancedVoyageAIEmbeddings


class MIRACLEModelFactory:
    @staticmethod
    def get_anthropic_model(
        model_name: Literal["sonnet", "haiku", "sonnet-legacy", "opus"] = "sonnet",
        temperature: float = 0.1,
        max_tokens: int = 8192,
        max_retries: int = 3,
        model_kwargs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        streaming: bool = False,
        api_key: Optional[str] = None,
        thinking: Optional[Dict[str, Any]] = None,
        enabled_output_128k: bool = False,
        token_efficient_tool_use: bool = False,
    ) -> ChatAnthropic:
        """Load the Anthropic model easily. You can freely revise it to make it easier to use."""

        if model_kwargs is None:
            model_kwargs = {}

        extra_headers = {}
        beta_features = []

        if enabled_output_128k and model_name == "sonnet":
            beta_features.append("output-128k-2025-02-19")

        if token_efficient_tool_use and model_name == "sonnet":
            beta_features.append("token-efficient-tools-2025-02-19")

        if beta_features and model_name == "sonnet":
            extra_headers["anthropic-beta"] = ",".join(beta_features)

        model_mapping = {
            "sonnet": "claude-3-7-sonnet-20250219",
            "sonnet-legacy": "claude-3-5-sonnet-20241022",
            "haiku": "claude-3-5-haiku-20241022",
            "opus": "claude-3-opus-latest"
        }

        anthropic_api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not anthropic_api_key:
            raise ValueError("Anthropic API key not found. Please provide it either through the api_key parameter or set it as an environment variable 'ANTHROPIC_API_KEY'")

        return ChatAnthropic(
            model_name=model_mapping[model_name],
            temperature=temperature,
            max_tokens_to_sample=max_tokens,
            api_key=anthropic_api_key,
            timeout=timeout,
            max_retries=max_retries,
            streaming=streaming,
            model_kwargs=model_kwargs,
            thinking=thinking,
            extra_headers=extra_headers
        )

    @staticmethod
    def get_openai_model(
        model_name: Literal['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest'] = "gpt-4o",
        temperature: float = 0.1,
        max_tokens: int = 8192,
        max_retries: int = 3,
        streaming: bool = False,
        api_key: Optional[str] = None,
    ) -> ChatOpenAI:
        model_mapping = {
            "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
            "gpt-4o": "gpt-4o-2024-08-06",
            "chatgpt-4o-latest": "chatgpt-4o-latest"
        }

        openai_api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("OpenAI API key not found. Please provide it either through the api_key parameter or set it as an environment variable 'OPENAI_API_KEY'")

        return ChatOpenAI(
            model_name=model_mapping[model_name],
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            openai_api_key=openai_api_key,
            streaming=streaming
        )

    @staticmethod
    def get_openai_embedding_model(
        model_name: Literal['small', 'large'] = 'small',
        api_key: Optional[str] = None,
    ) -> OpenAIEmbeddings:
        """Load the OpenAI embedding model easily. You can freely revise it to make it easier to use."""
        model_mapping = {
            "small": "text-embedding-3-small",
            "large": "text-embedding-3-large"
        }

        openai_api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not openai_api_key:
            raise ValueError("OpenAI API key not found. Please provide it either through the api_key parameter or set it as an environment variable 'OPENAI_API_KEY'")

        return OpenAIEmbeddings(
            model=model_mapping[model_name],
            openai_api_key=openai_api_key
        )

    @staticmethod
    def get_voyage_embedding_model(
        model_name: Literal[
            "voyage-3-large",
            "voyage-3",
            "voyage-3-lite",
            "voyage-code-3",
            "voyage-multimodal-3",
            "voyage-finance-2",
            "voyage-multilingual-2",
        ] = "voyage-3",
        api_key: Optional[str] = None,
    ) -> VoyageAIEmbeddings:

        voyage_api_key = api_key or os.getenv('VOYAGE_API_KEY')
        if not voyage_api_key:
            raise ValueError("Voyage API key not found. Please provide it either through the api_key parameter or set it as an environment variable 'VOYAGE_API_KEY'")

        return EnhancedVoyageAIEmbeddings(
            model=model_name,
            voyage_api_key=voyage_api_key
        )


    @staticmethod
    def get_voyage_rerank_model(
        model_name: Literal[
            "rerank-2",
            "rerank-2-lite",
            "rerank-1",
            "rerank-1-lite"
        ] = "rerank-2",
        api_key: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> VoyageAIRerank:

        voyage_api_key = api_key or os.getenv('VOYAGE_API_KEY')
        if not voyage_api_key:
            raise ValueError("Voyage API key not found. Please provide it either through the api_key parameter or set it as an environment variable 'VOYAGE_API_KEY'")

        return VoyageAIRerank(
            model=model_name,
            voyage_api_key=voyage_api_key,
            top_k=top_k
        )

