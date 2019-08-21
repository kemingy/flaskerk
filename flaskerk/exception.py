from pydantic import BaseModel, Schema


class HTTPValidationError(BaseModel):
    code: int = Schema(
        422,
        gt=100,
        lt=600,
        description='HTTP response status code',
    )
    description: str = 'Unprocessable Entity'


class HTTPException(BaseModel):
    code: int = Schema(
        ...,
        gt=100,
        lt=600,
        description='HTTP response status code',
    )
    msg: str

    class Config:
        schema_extra = {
            'examples': [
                {
                    'code': 422,
                    'msg': 'Unprocessable Entity',
                }
            ]
        }
