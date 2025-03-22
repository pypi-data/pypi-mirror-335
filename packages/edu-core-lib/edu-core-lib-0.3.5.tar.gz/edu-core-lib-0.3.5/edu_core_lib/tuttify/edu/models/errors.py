from pydantic import BaseModel


class ErrorDetail(BaseModel):
    status_code: int
    detail: str
    error_code: str


class ErrorResponse(BaseModel):
    detail: str
    message: str
    errorCode: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Exception message",
                "message": "Exception message",
                "errorCode": "error_code",
            }
        }
