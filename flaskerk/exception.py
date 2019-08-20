from pydantic import BaseModel, Schema


class HTTPValidationError(BaseModel):
    code: int = Schema(
        ...,
        gt=100,
        lt=600,
        description='HTTP response status code',
    )
    description: str
