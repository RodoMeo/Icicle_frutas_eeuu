#Script 1:  Icicle
import pandas as pd
import plotly.graph_objects as go
import os

# Establecer directorio de trabajo
os.chdir(r'E:\OneDrive\MSONI\Medium\Artículos\2025\Diciembre\Icicle\Datos')

# CARGAR Y LIMPIAR DATOS
df = pd.read_csv(r'E:\OneDrive\Bases_datos\Scripts\EEUU\Puertos_por_Capitulo\exports_capitulo_08\exports_08.csv')
df['Fecha'] = pd.to_datetime(df['Fecha'])
df = df[(df['Fecha'].dt.year >= 2017) & (df['Fecha'].dt.year <= 2024)]
df = df[~df['País'].isin(['USMCA (NAFTA)', 'USMCA', 'NAFTA'])].copy()
df = df[df['Valor US$'] > 0].copy()
df['Producto'] = df['Subpartida'].astype(str) + ' - ' + df['Descripción'].str[:30]

# AGREGAR Y FILTRAR
df_agg = df.groupby(['País', 'Puerto', 'Producto']).agg({'Valor US$': 'sum'}).reset_index()

TOP_PAISES = 10
TOP_PRODUCTOS = 50
top_paises = df_agg.groupby('País')['Valor US$'].sum().nlargest(TOP_PAISES).index
df_filtrado = df_agg[df_agg['País'].isin(top_paises)].copy()
top_productos = df_filtrado.groupby('Producto')['Valor US$'].sum().nlargest(TOP_PRODUCTOS).index
df_filtrado = df_filtrado[df_filtrado['Producto'].isin(top_productos)]

# CONSTRUIR JERARQUÍA
labels = ['Chapter 08<br>Edible Fruits<br>& Nuts']
parents = [""]
values = [df_filtrado['Valor US$'].sum()]
ids = ["root"]

for pais in df_filtrado['País'].unique():
    labels.append(pais)
    parents.append("root")
    values.append(df_filtrado[df_filtrado['País'] == pais]['Valor US$'].sum())
    ids.append(pais)

for _, row in df_filtrado.groupby(['País', 'Puerto'])['Valor US$'].sum().reset_index().iterrows():
    labels.append(row['Puerto'])
    parents.append(row['País'])
    values.append(row['Valor US$'])
    ids.append(f"{row['País']}-{row['Puerto']}")

for _, row in df_filtrado.iterrows():
    labels.append(row['Producto'])
    parents.append(f"{row['País']}-{row['Puerto']}")
    values.append(row['Valor US$'])
    ids.append(f"{row['País']}-{row['Puerto']}-{row['Producto']}")

# CREAR ICICLE CHART
fig = go.Figure(go.Icicle(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    marker=dict(
        colorscale='Greens',
        line=dict(color='white', width=2)
    ),
    root=dict(color='#1e5c12'),
    textfont=dict(size=11),
    hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>% of parent: %{percentParent:.1%}<extra></extra>'
))

fig.update_layout(
    title={
        'text': 'U.S. Exports - Chapter 08: Edible Fruits and Nuts<br><sub>Top 10 Countries → Ports → Products (Total - 2017-2024)</sub><br>Zoom in for details<sub></sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18}
    },
    height=1200,
    margin=dict(t=120, l=5, r=5, b=5),
    font=dict(family='Arial', size=11),
    paper_bgcolor='white',
    plot_bgcolor='white'
)

# GUARDAR
archivo = 'icicle_chapter08_exports.html'
fig.write_html(archivo, config={'displayModeBar': False}, include_plotlyjs='cdn')

print(f"\n✅ Archivo guardado: {os.path.join(os.getcwd(), archivo)}")
print(f"📊 Total Value: ${df_filtrado['Valor US$'].sum():,.2f}")
print(f"🌎 Countries: {df_filtrado['País'].nunique()}")
print(f"📦 Products: {df_filtrado['Producto'].nunique()}")
