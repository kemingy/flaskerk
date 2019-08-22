from pydantic import BaseModel, Schema
from pydantic.dataclasses import dataclass
from werkzeug.exceptions import _aborter
from werkzeug.exceptions import HTTPException as WerkzeugException
from werkzeug.http import HTTP_STATUS_CODES


class HTTPValidationError(BaseModel):
    code: int = Schema(
        422,
        description='HTTP response status code',
    )
    description: str = 'Unprocessable Entity'


@dataclass
class HTTPException:
    code: int = Schema(
        ...,
        gt=100,
        lt=1000,
        description='HTTP response status code',
    )
    msg: str = Schema(
        ...,
    )

    def __post_init_post_parse__(self):
        if self.code not in _aborter.mapping:
            _aborter.mapping[self.code] = type(
                f'NewHttpException_{self.code}',
                (WerkzeugException, ),
                {'code': self.code, 'description': self.msg}
            )
            HTTP_STATUS_CODES[self.code] = self.msg
            print('[=] register exception: ', self.code)
