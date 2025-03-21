from project.sqladmin_.model_view.common import SimpleMV
from project.sqlalchemy_db_.sqlalchemy_model import OperationDBM


class OperationMV(SimpleMV, model=OperationDBM):
    name = "Operation"
    name_plural = "Operations"
    column_list = [
        OperationDBM.id,
        OperationDBM.long_id,
        OperationDBM.slug,
        OperationDBM.creation_dt,
        OperationDBM.status,
        OperationDBM.type,
        OperationDBM.title,
        OperationDBM.execution_start_dt,
        OperationDBM.execution_finish_dt,
        OperationDBM.input_data,
        OperationDBM.output_data,
        OperationDBM.error_data
    ]
    form_columns = [
        OperationDBM.slug,
        OperationDBM.status,
        OperationDBM.type,
        OperationDBM.title,
        OperationDBM.execution_start_dt,
        OperationDBM.execution_finish_dt,
        OperationDBM.input_data,
        OperationDBM.output_data,
        OperationDBM.error_data
    ]
    column_default_sort = [
        (OperationDBM.creation_dt, True)
    ]
    column_searchable_list = [
        OperationDBM.id,
        OperationDBM.long_id,
        OperationDBM.slug,
        OperationDBM.status,
        OperationDBM.type,
        OperationDBM.title
    ]
