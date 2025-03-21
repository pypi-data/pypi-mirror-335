import fastapi
from fastapi import APIRouter

from arpakitlib.ar_datetime_util import now_utc_dt
from project.api.schema.out.common.datetime_ import DatetimeCommonSO
from project.api.schema.out.common.error import ErrorCommonSO

api_router = APIRouter()


@api_router.get(
    "",
    name="Now UTC datetime",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=DatetimeCommonSO | ErrorCommonSO,
)
async def _(
        *,
        request: fastapi.requests.Request,
        response: fastapi.responses.Response,
):
    return DatetimeCommonSO.from_datetime(datetime_=now_utc_dt())
