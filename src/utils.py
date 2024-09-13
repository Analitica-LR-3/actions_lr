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

SPANISH_MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def format_date():
    now = datetime.datetime.now() - datetime.timedelta(hours=5)
    day = now.strftime("%d")
    month = now.month
    year = now.strftime("%Y")
    hour_24 = now.hour
    minute = now.strftime("%M")
    if hour_24 == 0:
        hour_12 = 12
        period = 'AM'
    elif hour_24 < 12:
        hour_12 = hour_24
        period = 'AM'
    elif hour_24 == 12:
        hour_12 = 12
        period = 'PM'
    else:
        hour_12 = hour_24 - 12
        period = 'PM'
    spanish_month = SPANISH_MONTHS[month - 1]
    formatted_date = f"{day} de {spanish_month} de {year} {hour_12}:{minute} {period}"

    return formatted_date