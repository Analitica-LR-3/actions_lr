import datetime

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1iizPemP8CqAELa-PAhc7jDmTy1yLAX0Yq_fjStUpqYQ'

DAILY_ACTIONS_SHEET_DICT = {
    'Acciones Diarias PPLR Depurada': 'PPLR',
    'Acciones Diarias Cooperación Depurada': 'Cooperación',
    'Acciones Diarias Comités LR Depurada': 'Comités LR',
    'Acciones Diarias POT Depurada': 'POT',
    'Acciones Diarias Enlaces Depurada': 'Enlaces',
    'Acciones Diarias PD Depurada': 'Plan Desarrollo',
    'Acciones Diarias Participación Política Depurada': 'Participación Política',
    'Acciones Diarias PP Depurada': 'Presupuesto Participativo'
}
# DAILY_ACTIONS_SHEET_DICT = {
#     'Acciones Diarias PPLR Depurada': 'PPLR',
#     'Acciones Diarias Cooperación Depurada': 'Cooperación'
# }

DAILY_ACTIONS_DTYPES_DICT = {
    'Usuario': object, 
    'Tipo Usuario': object,
    'Departamento': object,
    'Municipio': object,
    'Actividades rutinarias': object,
    'Fecha': object
}