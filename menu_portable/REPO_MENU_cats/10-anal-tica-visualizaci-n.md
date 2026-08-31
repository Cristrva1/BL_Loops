# 10. Analítica & Visualización — detalle de repos

> Abre este archivo SOLO si tienes finalistas en esta categoría.
> Cada entrada: desc, stack, instalación, choose/avoid, combina/compite.

## `streamlit`
role=platform · exec=local · setup=easy · mcp=False · prov=— · tags=python,typescript

**Qué es:** A faster way to build and share data apps.
**Stack:** python, typescript
**Repo:** https://github.com/streamlit/streamlit.git

**Instalación** [~]: `git clone https://github.com/streamlit/streamlit.git && cd streamlit && (uv sync || pip install -r requirements.txt)`
_Proyecto Python; usa uv si hay pyproject.toml/uv.lock._

**Elige si:** quieres una UI de datos al vuelo y prototipos rápidos
**Evita si:** necesitas una app productiva con control fino del frontend ([dash](#-dash)).
**Combina con:** `dash`, `data-science-ipython-notebooks`

## `uplot`
role=library · exec=hybrid · setup=medium · mcp=False · prov=— · tags=javascript,javascript-typescript,python,react,typescript

**Qué es:** A small (~50 KB min), fast chart for time series, lines, areas, ohlc & bars _(MIT Licensed)_.
**Stack:** javascript/typescript, python, typescript, javascript, react
**Repo:** https://github.com/leeoniya/uPlot.git

**Instalación** [~]: `pip install uplot   (o: uv add uplot)`
_Nombre PyPI puede diferir de 'uPlot'; verifica en pypi.org._

**Elige si:** priorizas velocidad y peso del bundle
**Evita si:** necesitas tipos de gráfico variados ([echarts](#-echarts)).
**Combina con:** `swr`, `web app moderna`
