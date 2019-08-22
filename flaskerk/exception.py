from pydantic import BaseModel, Schema, validator
from pydantic.dataclasses import dataclass
from werkzeug.exceptions import _aborter, default_exceptions
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
    """
    HTTP Exceptions.

    :param int code: HTTP status code
    :param str msg: description

    If you are using default code like 403, 404, 500 ..., you can ignore the
    ``msg`` parameter and this module will use default description.

    If you want to define your own code and description, you must offer ``msg``.
    """
    code: int = Schema(
        ...,
        gt=100,
        lt=1000,
        description='HTTP response status code',
    )
    msg: str = None

    @validator('msg', pre=True, always=True)
    def set_as_default(cls, v, values, **kwargs):
        if v is None:
            if 'code' not in values or values['code'] not in default_exceptions:
                raise ValueError('Invalid default HTTP status code.')
            v = default_exceptions[values['code']].description
        return v

    def __post_init_post_parse__(self):
        if self.code not in _aborter.mapping:
            _aborter.mapping[self.code] = type(
                f'NewHTTPException_{self.code}',
                (WerkzeugException, ),
                {'code': self.code, 'description': self.msg}
            )
            HTTP_STATUS_CODES[self.code] = self.msg
