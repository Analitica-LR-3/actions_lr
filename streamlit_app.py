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
    # Use landscape orientation and reduce margins
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                            leftMargin=5, rightMargin=5, topMargin=15, bottomMargin=15)

    # Define custom styles for text
    styles = getSampleStyleSheet()

    # Bold title style with Times-Bold
    title_style = ParagraphStyle(
        'Title',
        fontName='Times-Bold',
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    # Bold subtitle style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName='Times-Bold',
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    # Define custom style for wrapping text in paragraphs
    custom_paragraph_style = ParagraphStyle(
        'Custom',
        fontName='Times-Roman',
        fontSize=7,
        leading=9,
        alignment=TA_LEFT,
        wordWrap='CJK',
        maxLineLength=None,
    )

    # Prepare the data for the table, wrap text in Paragraphs
    data = [[Paragraph(str(col), custom_paragraph_style) for col in df.columns]]
    for i, row in df.iterrows():
        data.append([Paragraph(str(cell), custom_paragraph_style) for cell in row])

    # Define column widths
    col_widths = [40, 45, 55, 55, 120, 55, 180]

    # Create the table with data
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Apply styles to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f5f5f5'),
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

    # Add logo image
    logo = Image("reports/figures/Logo_Partido.jpeg", width=60, height=35)

    # Title on the left
    title = Paragraph("Acciones de Libertad Religiosa, Consolidado Nacional", title_style)

    # Subtitle above the title
    formatted_date = format_date()
    subtitle_text = f"Cohorte {formatted_date}"
    subtitle = Paragraph(subtitle_text, subtitle_style)

    # Add an empty paragraph to create space between the title, logo, and the table
    empty_paragraph = Paragraph("<br/><br/>", custom_paragraph_style)

    # Create a layout to have title and subtitle at the left, and logo at the right
    header_layout = Table([[title, logo], [subtitle, '']], colWidths=[450, 90])

    # Align the logo to the right in the table
    header_layout.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 0)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')
    ]))

    # Create the list of elements to be added to the PDF
    elements = [header_layout, empty_paragraph, table]

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def main():
    st.title('Acciones Diarias')

    refresh = st.button('Refrescar datos')

    if 'data' not in st.session_state or refresh:
        st.session_state.data = get_data()

    df = st.session_state.data
    df.columns = ['Elemento esencial LR', 'Fecha', 'Departamento', 'Municipio', 'Usuario', 'Tipo usuario', 'Acción diaria']

    # Filter options
    departamentos = sorted(df['Departamento'].unique().tolist())
    municipios = sorted(df['Municipio'].unique().tolist())
    usuarios = sorted(df['Usuario'].unique().tolist())
    tipos_usuario = sorted(df['Tipo usuario'].unique().tolist())
    
    # Initialize session state for selected filters if not already set
    if 'selected_departamento' not in st.session_state:
        st.session_state.selected_departamento = None

    if 'selected_municipio' not in st.session_state:
        st.session_state.selected_municipio = None

    if 'selected_usuario' not in st.session_state:
        st.session_state.selected_usuario = None

    if 'selected_tipo_usuario' not in st.session_state:
        st.session_state.selected_tipo_usuario = None

    # Update filter options based on previous selections
    departamento_filter = st.selectbox('Departamento', ['Todos'] + departamentos)
    
    if departamento_filter != 'Todos':
        st.session_state.selected_departamento = departamento_filter
    else:
        st.session_state.selected_departamento = None

    if st.session_state.selected_departamento:
        municipios_filtered = df[df['Departamento'] == st.session_state.selected_departamento]['Municipio'].unique().tolist()
        municipio_filter = st.selectbox('Municipio', ['Todos'] + sorted(municipios_filtered))
    else:
        municipio_filter = st.selectbox('Municipio', ['Todos'] + sorted(municipios))

    if municipio_filter != 'Todos':
        st.session_state.selected_municipio = municipio_filter
    else:
        st.session_state.selected_municipio = None

    if st.session_state.selected_departamento:
        filtered_df = df[df['Departamento'] == st.session_state.selected_departamento]
    else:
        filtered_df = df

    if st.session_state.selected_municipio:
        filtered_df = filtered_df[filtered_df['Municipio'] == st.session_state.selected_municipio]

    # Update Usuario and Tipo usuario filters based on Municipio selection
    if st.session_state.selected_municipio:
        usuarios_filtered = filtered_df['Usuario'].unique().tolist()
        tipos_usuario_filtered = filtered_df['Tipo usuario'].unique().tolist()
    else:
        usuarios_filtered = usuarios
        tipos_usuario_filtered = tipos_usuario

    accion_filter = st.multiselect('Elemento esencial LR', filtered_df['Elemento esencial LR'].unique().tolist())
    fecha_filter = st.multiselect('Fecha', filtered_df['Fecha'].unique().tolist())
    usuario_filter = st.multiselect('Usuario', sorted(usuarios_filtered))
    tipo_usuario_filter = st.multiselect('Tipo usuario', sorted(tipos_usuario_filtered))

    if accion_filter:
        filtered_df = filtered_df[filtered_df['Elemento esencial LR'].isin(accion_filter)]
    if fecha_filter:
        filtered_df = filtered_df[filtered_df['Fecha'].isin(fecha_filter)]
    if usuario_filter:
        filtered_df = filtered_df[filtered_df['Usuario'].isin(usuario_filter)]
    if tipo_usuario_filter:
        filtered_df = filtered_df[filtered_df['Tipo usuario'].isin(tipo_usuario_filter)]

    st.write(" ")
    st.dataframe(filtered_df)

    now = (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime("%Y_%m_%d-%H_%M")
    if st.button('Exportar como PDF'):
        pdf_buffer = generate_pdf(filtered_df)
        st.download_button(
            label="Descargar PDF",
            data=pdf_buffer,
            file_name=f"acciones_diarias-{now}.pdf",
            mime="application/pdf"
        )

    # Hide Streamlit's menu and footer
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()