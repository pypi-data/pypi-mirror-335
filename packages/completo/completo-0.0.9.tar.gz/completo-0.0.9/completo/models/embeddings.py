from pydantic import BaseModel


class Embedding(BaseModel):
    input_text: str
    embedding: list[float]
