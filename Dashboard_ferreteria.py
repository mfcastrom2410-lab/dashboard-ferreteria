import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Ejecutivo de Ventas - Ferretería",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y PREPARACIÓN DE DATOS
@st.cache_data
def cargar_datos():
    df = pd.read_excel('Base de datos ferreteria.xlsx', sheet_name='Ventas')
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar la base de datos 'Base de datos ferreteria.xlsx': {e}")
    st.stop()

# 3. BARRA LATERAL (FILTROS)
st.sidebar.title("🔍 Filtros Dinámicos")

# Filtro de Rango de Fechas
fecha_min = df['Fecha'].min().date()
fecha_max = df['Fecha'].max().date()
rango_fechas = st.sidebar.date_input("Rango de Fechas:", [fecha_min, fecha_max], min_value=fecha_min, max_value=fecha_max)

# Filtro por Ciudad
ciudades = ["Todas"] + sorted(list(df['Ciudad'].dropna().unique()))
ciudad_sel = st.sidebar.selectbox("Ciudad:", ciudades)

# Filtro por Categoría
categorias = ["Todas"] + sorted(list(df['Categoría'].dropna().unique()))
categoria_sel = st.sidebar.selectbox("Categoría de Producto:", categorias)

# Filtro por Canal de Venta
canales = ["Todos"] + sorted(list(df['Canal Venta'].dropna().unique()))
canal_sel = st.sidebar.selectbox("Canal de Venta:", canales)

# Filtro por Tipo de Cliente
tipos_cliente = ["Todos"] + sorted(list(df['Tipo Cliente'].dropna().unique()))
tipo_cliente_sel = st.sidebar.selectbox("Tipo de Cliente:", tipos_cliente)

# APLICACIÓN DE FILTROS
df_filtrado = df.copy()

if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[(df_filtrado['Fecha'].dt.date >= rango_fechas[0]) & (df_filtrado['Fecha'].dt.date <= rango_fechas[1])]

if ciudad_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Ciudad'] == ciudad_sel]

if categoria_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoría'] == categoria_sel]

if canal_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Canal Venta'] == canal_sel]

if tipo_cliente_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Tipo Cliente'] == tipo_cliente_sel]

# 4. ENCABEZADO Y KPIS PRINCIPALES
st.title("🏗️ Dashboard Ejecutivo & Analítico de Ferretería")
st.markdown("Plataforma interactiva de inteligencia de negocios para el seguimiento de ventas, rentabilidad y satisfacción.")

st.subheader("📊 Indicadores Clave de Rendimiento (KPIs)")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

ventas_totales = df_filtrado['Total Neto ($)'].sum()
ganancia_total = df_filtrado['Ganancia Neta ($)'].sum()
margen_prom = df_filtrado['Margen (%)'].mean() if len(df_filtrado) > 0 else 0
unidades_vendidas = df_filtrado['Cantidad'].sum()
satisfaccion = df_filtrado['Satisfacción Cliente (1-5)'].mean() if len(df_filtrado) > 0 else 0

kpi1.metric("Ventas Netas", f"${ventas_totales:,.0f}")
kpi2.metric("Ganancia Neta", f"${ganancia_total:,.0f}")
kpi3.metric("Margen Promedio", f"{margen_prom:.1f}%")
kpi4.metric("Unidades Vendidas", f"{unidades_vendidas:,.0f}")
kpi5.metric("Satisfacción", f"⭐ {satisfaccion:.2f} / 5.0")

st.markdown("---")

# 5. ORGANIZACIÓN POR PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendencia y Ventas", 
    "🏷️ Categorías y Productos", 
    "👥 Clientes y Canales", 
    "📋 Detalle de Datos"
])

# --- PESTAÑA 1: TENDENCIA Y VENTAS GEOGRÁFICAS ---
with tab1:
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Evolución Mensual de Ventas y Ganancias")
        df_mensual = df_filtrado.groupby('Mes_Año')[['Total Neto ($)', 'Ganancia Neta ($)']].sum().reset_index()
        fig_line = px.line(df_mensual, x='Mes_Año', y=['Total Neto ($)', 'Ganancia Neta ($)'],
                           markers=True, labels={'value': 'Monto ($)', 'Mes_Año': 'Mes'},
                           color_discrete_sequence=['#1f77b4', '#2ca02c'])
        fig_line.update_layout(legend_title_text='Métrica', hovermode='x unified')
        st.plotly_chart(fig_line, width='stretch')
        
    with c2:
        st.subheader("Distribución de Ganancia Neta por Ciudad")
        df_ciudad = df_filtrado.groupby('Ciudad')['Ganancia Neta ($)'].sum().reset_index()
        fig_pie = px.pie(df_ciudad, names='Ciudad', values='Ganancia Neta ($)', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, width='stretch')

# --- PESTAÑA 2: CATEGORÍAS Y PRODUCTOS ---
with tab2:
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("Top Productos Más Vendidos ($)")
        top_prod = df_filtrado.groupby('Producto')['Total Neto ($)'].sum().reset_index().sort_values(by='Total Neto ($)', ascending=True).tail(8)
        fig_prod = px.bar(top_prod, x='Total Neto ($)', y='Producto', orientation='h',
                          color='Total Neto ($)', color_continuous_scale='Blues')
        st.plotly_chart(fig_prod, width='stretch')
        
    with c4:
        st.subheader("Margen de Ganancia Promedio por Categoría (%)")
        df_margen = df_filtrado.groupby('Categoría')['Margen (%)'].mean().reset_index().sort_values(by='Margen (%)', ascending=False)
        fig_margen = px.bar(df_margen, x='Categoría', y='Margen (%)', color='Margen (%)',
                            color_continuous_scale='Greens', text_auto='.1f')
        st.plotly_chart(fig_margen, width='stretch')

# --- PESTAÑA 3: CLIENTES Y CANALES ---
with tab3:
    c5, c6 = st.columns(2)
    
    with c5:
        st.subheader("Ventas por Canal de Distribución")
        df_canal = df_filtrado.groupby('Canal Venta')['Total Neto ($)'].sum().reset_index()
        fig_canal = px.bar(df_canal, x='Canal Venta', y='Total Neto ($)', color='Canal Venta',
                           color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig_canal, width='stretch')
        
    with c6:
        st.subheader("Relación Método de Pago vs. Satisfacción del Cliente")
        fig_box = px.box(df_filtrado, x='Método Pago', y='Satisfacción Cliente (1-5)', color='Método Pago',
                         points="all")
        st.plotly_chart(fig_box, width='stretch')

# --- PESTAÑA 4: DETALLE DE DATOS ---
with tab4:
    st.subheader("Explorador de Registros")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón de Descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv,
        file_name='reporte_ferreteria_filtrado.csv',
        mime='text/csv'
    )