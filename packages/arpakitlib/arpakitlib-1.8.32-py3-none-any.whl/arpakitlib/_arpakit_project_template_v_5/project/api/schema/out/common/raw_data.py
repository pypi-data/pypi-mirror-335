from typing import Any

from project.api.schema.common import BaseSO


class RawDataCommonSO(BaseSO):
    data: dict[str, Any] = {}
