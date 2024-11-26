import streamlit as st
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from src.data.make_dataset import DailyActionsWrangling

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


@st.cache_data
def get_data():
    daw = DailyActionsWrangling()
    return daw.make_daily_actions_dataset()


def generate_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                            leftMargin=5, rightMargin=5, topMargin=15, bottomMargin=15)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        fontName='Times-Bold',
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName='Times-Bold',
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    custom_paragraph_style = ParagraphStyle(
        'Custom',
        fontName='Times-Roman',
        fontSize=7,
        leading=9,
        alignment=TA_LEFT,
        wordWrap='CJK',
        maxLineLength=None,
    )

    data = [[Paragraph(str(col), custom_paragraph_style) for col in df.columns]]
    for i, row in df.iterrows():
        data.append([Paragraph(str(cell), custom_paragraph_style) for cell in row])

    col_widths = [40, 45, 55, 55, 120, 55, 180]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), 1),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ])
    table.setStyle(style)

    logo = Image("reports/figures/Logo_Partido.jpeg", width=60, height=35)

    title = Paragraph("Acciones de Libertad Religiosa, Consolidado Nacional", title_style)
    formatted_date = format_date()
    subtitle_text = f"Cohorte {formatted_date}"
    subtitle = Paragraph(subtitle_text, subtitle_style)

    empty_paragraph = Paragraph("<br/><br/>", custom_paragraph_style)

    header_layout = Table([[title, logo], [subtitle, '']], colWidths=[450, 90])

    header_layout.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')
    ]))

    elements = [header_layout, empty_paragraph, table]
    doc.build(elements)
    buffer.seek(0)
    return buffer


def main():
    st.title('Acciones Diarias')

    # Initialize filters in session state if not already set
    if 'departamento_filter' not in st.session_state:
        st.session_state.departamento_filter = 'Todos'
    if 'municipio_filter' not in st.session_state:
        st.session_state.municipio_filter = []
    if 'tipo_usuario_filter' not in st.session_state:
        st.session_state.tipo_usuario_filter = []
    if 'usuario_filter' not in st.session_state:
        st.session_state.usuario_filter = []
    if 'accion_filter' not in st.session_state:
        st.session_state.accion_filter = []
    if 'fecha_filter' not in st.session_state:
        st.session_state.fecha_filter = []

    # Clear Filters Button
    if st.button('Limpiar filtros', key="clear_filters"):
        st.session_state.departamento_filter = 'Todos'
        st.session_state.municipio_filter = []
        st.session_state.tipo_usuario_filter = []
        st.session_state.usuario_filter = []
        st.session_state.accion_filter = []
        st.session_state.fecha_filter = []

    # Refresh Button
    refresh = st.button('Refrescar datos')

    if 'data' not in st.session_state or refresh:
        st.session_state.data = get_data()

    df = st.session_state.data
    df = df[['Acción', 'Fecha', 'Departamento', 'Municipio', 'Tipo Usuario', 'Usuario', 'Actividades rutinarias']]
    df.columns = ['Elemento esencial LR', 'Fecha', 'Departamento', 'Municipio', 'Tipo usuario', 'Usuario', 'Acción diaria']

    # Start with the original DataFrame
    filtered_df = df.copy()

    # Departamento filter
    departamento_filter = st.selectbox(
        'Departamento', 
        ['Todos'] + sorted(df['Departamento'].unique()),
        key="departamento_filter"
    )
    if departamento_filter != 'Todos':
        filtered_df = filtered_df[filtered_df['Departamento'] == departamento_filter]

    # Municipio filter
    municipio_filter = st.multiselect(
        'Municipio', 
        sorted(filtered_df['Municipio'].unique()),
        key="municipio_filter",
        placeholder="Elige una o varias opciones"
    )
    if municipio_filter:
        filtered_df = filtered_df[filtered_df['Municipio'].isin(municipio_filter)]

    # Tipo usuario filter
    tipo_usuario_filter = st.multiselect(
        'Tipo usuario', 
        sorted(filtered_df['Tipo usuario'].unique()),
        key="tipo_usuario_filter",
        placeholder="Elige una o varias opciones"
    )
    if tipo_usuario_filter:
        filtered_df = filtered_df[filtered_df['Tipo usuario'].isin(tipo_usuario_filter)]

    # Usuario filter
    usuario_filter = st.multiselect(
        'Usuario', 
        sorted(filtered_df['Usuario'].unique()),
        key="usuario_filter",
        placeholder="Elige una o varias opciones"
    )
    if usuario_filter:
        filtered_df = filtered_df[filtered_df['Usuario'].isin(usuario_filter)]

    # Elemento esencial LR filter
    accion_filter = st.multiselect(
        'Elemento esencial LR', 
        sorted(filtered_df['Elemento esencial LR'].unique()),
        key="accion_filter",
        placeholder="Elige una o varias opciones"
    )
    if accion_filter:
        filtered_df = filtered_df[filtered_df['Elemento esencial LR'].isin(accion_filter)]

    # Fecha filter
    fecha_filter = st.multiselect(
        'Fecha', 
        sorted(filtered_df['Fecha'].unique()),
        key="fecha_filter",
        placeholder="Elige una o varias opciones"
    )
    if fecha_filter:
        filtered_df = filtered_df[filtered_df['Fecha'].isin(fecha_filter)]

    # Display the filtered DataFrame
    st.write(" ")
    st.dataframe(filtered_df)

    # Export to PDF
    now = (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime("%Y_%m_%d-%H_%M")
    if st.button('Exportar como PDF'):
        pdf_buffer = generate_pdf(filtered_df)
        st.download_button(
            label="Descargar PDF",
            data=pdf_buffer,
            file_name=f"acciones_diarias-{now}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
