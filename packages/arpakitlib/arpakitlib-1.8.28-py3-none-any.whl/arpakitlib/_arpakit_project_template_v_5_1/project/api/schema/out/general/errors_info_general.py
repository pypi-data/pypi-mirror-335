from project.api.schema.common import BaseSO


class ErrorsInfoGeneralSO(BaseSO):
    api_error_codes: list[str] = []
    api_error_specification_codes: list[str] = []
