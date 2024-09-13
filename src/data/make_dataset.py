# -*- coding: utf-8 -*-
import pandas as pd
import re
from src.utils import DAILY_ACTIONS_DTYPES_DICT, DAILY_ACTIONS_SHEET_DICT
from src.data.collect_data import read_google_spreadsheet

# PENDING: Add a datatype formating funtion

class DataExploring:

    def unique_values(self, df, max_valores=None):
        # Crear listas para almacenar los resultados
        columnas = []
        conteos = []
        valores = []

        for columna in df.columns:
            valores_unicos = df[columna].unique()
            total_valores_unicos = len(valores_unicos)
            
            if max_valores is not None:
                valores_a_mostrar = valores_unicos[:max_valores]
                if total_valores_unicos > max_valores:
                    valores_a_mostrar = list(valores_a_mostrar) + ['...']
            else:
                valores_a_mostrar = valores_unicos
            
            # Convertir los valores a string con comillas para las cadenas
            valores_str = ', '.join(f'"{v}"' if isinstance(v, str) and v != '...' else str(v) for v in valores_a_mostrar)
            
            # Añadir los resultados a las listas
            columnas.append(columna)
            conteos.append(f"{total_valores_unicos} valores únicos")
            valores.append(f"[{valores_str}]")

        # Calcular el ancho máximo para cada columna
        max_columna_len = max(len(col) for col in columnas)
        max_conteo_len = max(len(conteo) for conteo in conteos)
        max_valores_len = max(len(valor) for valor in valores)

        # Formato para cada fila
        formato_fila = f"{{:<{max_columna_len}}}    {{:<{max_conteo_len}}}    {{:<{max_valores_len}}}"

        # Imprimir encabezado
        print(formato_fila.format("Columna", "Conteo de Valores Únicos", "Valores"))
        print('-' * (max_columna_len + max_conteo_len + max_valores_len + 8))

        # Imprimir resultados
        for col, conteo, valor in zip(columnas, conteos, valores):
            print(formato_fila.format(col, conteo, valor))

class DailyActionsWrangling:

    def rename_columns(df):

        # df.rename({}, axis=1, inplace=True)
        
        return df

    def format_columns(df):
        '''
        Convert the columns in the DataFrame using the dtypes_dict
        '''
        df = df.astype(DAILY_ACTIONS_DTYPES_DICT)
        return df

    def concat_columns(sheet_dict):
        # Create a mapping from sheet names to their order
        sheet_names = list(sheet_dict.keys())
        sheet_order = {sheet: i for i, sheet in enumerate(sheet_names)}
        
        df = pd.DataFrame()
        
        for sheet in sheet_names:
            df_new = read_google_spreadsheet(sheet_name=sheet)
            df_new = DailyActionsWrangling.format_columns(df_new)
            
            # Assign a rank based on the sheet name
            df_new['SheetOrder'] = sheet_order.get(sheet, float('inf'))  # Default to inf if sheet not found
            
            df = pd.concat([df, df_new], axis=0)
        
        # Sort by SheetOrder, Departamento, and Municipio
        df.sort_values(['SheetOrder', 'Departamento', 'Municipio'], inplace=True)
        
        # Add 'Acción' column based on the sheet name
        # Map sheet names to their replacement values
        df['Acción'] = df['SheetOrder'].map({v: k for k, v in sheet_order.items()})
        df['Acción'] = df['Acción'].replace(sheet_dict)
        
        # Drop the 'SheetOrder' column if it's no longer needed
        df.drop(columns=['SheetOrder'], inplace=True)

        return df
    
    def clean_column(x):
        x = str(x)
        # Define patterns for standardizing columns
        patterns = {
            r'%20': ' '
        }
        # Replace street types using regular expressions
        for pattern, replacement in patterns.items():
            x = re.sub(pattern, replacement, x, flags=re.IGNORECASE)
        # Remove special characters
        # x = re.sub('#|°|\.|\,', ' ', x)
        return x.strip()        

    def clean_all_columns(df):
        # Remove duplicated rows
        df.drop_duplicates(keep='last', inplace=True)
        df.reset_index(drop=True, inplace=True)
        # Clean each column
        for c in df.columns:
            df[c] = df[c].apply(DailyActionsWrangling.clean_column)
        df = df[['Acción', 'Fecha', 'Departamento', 'Municipio', 
                 'Usuario', 'Tipo Usuario', 'Actividades rutinarias']]
        return df

    def make_daily_actions_dataset(self):
        # df = df.sample(3, random_state=123) # Temporal
        # df = df.head(10) # Temporal
        df = DailyActionsWrangling.concat_columns(DAILY_ACTIONS_SHEET_DICT)
        df = DailyActionsWrangling.clean_all_columns(df)
        return df

if __name__ == '__main__':
    print(DailyActionsWrangling.make_daily_actions_dataset())
