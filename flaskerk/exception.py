from pydantic import BaseModel, Field, validator
from werkzeug.exceptions import _aborter, default_exceptions
from werkzeug.exceptions import HTTPException as WerkzeugException
from werkzeug.http import HTTP_STATUS_CODES

from flaskerk.utils import abort_json


class HTTPValidationError(BaseModel):
    code: int = Field(
        422,
        description='HTTP response status code',
    )
    description: str = 'Unprocessable Entity'


class HTTPException(BaseModel):
    """
    HTTP Exceptions.

    :param int code: HTTP status code
    :param str msg: description

    .. _code: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    If you are using default code_ like 403, 404, 500 ..., you can ignore the
    ``msg`` parameter and this module will use default description.

    If you want to define your own code and description, you must offer ``msg``.

    examples:

    .. code-block:: python

       from flaskerk import HTTPException
       code404 = HTTPException(code=404)
       # with customized discription
       code403 = HTTPException(code=403, msg='IP is blocked.')
       # customized code
       code777 = HTTPException(code=777, msg='bad luck')

       # abort
       code777.abort()
    """
    code: int = Field(
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

    def abort(self, msg=None):
        """
        abort as a JSON response
        """
        abort_json(self.code, msg or self.msg)
