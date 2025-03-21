from abc import ABC, abstractmethod
from itertools import chain
import concurrent
from typing import Any
from httpx import NetworkError
import tiktoken


class AbstractEntryPoint(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self) -> Any:
        pass

    @abstractmethod
    def get_response(self, sentence: str) -> str:
        pass

    @abstractmethod
    def get_response_by_payload(self, payload: list[dict[str, str]]) -> str:
        pass

    @abstractmethod
    def get_embedding(self, sentence: str) -> list[float]:
        pass

    @abstractmethod
    def get_embeddings(self, sentences: list[str], request_limit: int = 50) -> list[list[float]]:
        pass

    def get_more_embeddings(self, sentences: list[str], batch_size: int = 2, max_workers: int = 4) -> list[list[float]]:
        batches: list[list[str]] = self.make_batches(sentences, size=batch_size)
        if max_workers == 1:
            emb_batches = [self.get_embeddings(batch) for batch in batches]
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.get_embeddings, batch) for batch in batches]
                emb_batches = [future.result() for future in futures]
        return list(chain.from_iterable(emb_batches))

    def count_tokens(self, sentences: list[str]) -> list[int]:
        encoding = tiktoken.get_encoding("cl100k_base")
        return [len(encoding.encode(sentence)) for sentence in sentences]

    @staticmethod
    def make_batches(items: list, size: int = 500) -> list[list[str]]:
        slices = [(i * size, (i + 1) * size) for i in range(len(items) // size + 1)]
        return [items[st:ed] for st, ed in slices]

    def warmup(self) -> None:
        if not self.get_response("Прогрев") or not sum(self.get_embedding("Прогрев")):
            raise NetworkError("Нет доступа к ллм!")

    @staticmethod
    def create_payload(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def create_image_payload(system_prompt: str, user_prompt: str, image_encoded: str, mimetype='image/jpeg'):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                 {"type": "text", "text": user_prompt},
                 {"type": "image_url", "image_url": {
                     "url": f"data:{mimetype};base64,{image_encoded}"
                 }}
             ]}
        ]
