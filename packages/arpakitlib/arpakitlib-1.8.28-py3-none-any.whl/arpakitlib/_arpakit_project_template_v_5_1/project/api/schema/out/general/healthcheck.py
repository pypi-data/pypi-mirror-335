from project.api.schema.common import BaseSO


class HealthcheckGeneralSO(BaseSO):
    is_ok: bool = True
