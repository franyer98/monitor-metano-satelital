"""Monitor de metano satelital sobre Campo Rubiales."""
import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from app.satelite import obtener_serie

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="Monitor de Metano Satelital — Campo Rubiales")


@app.get("/metano/serie")
def serie_metano(dias: int = Query(90, ge=7, le=365)):
    try:
        return JSONResponse(obtener_serie(dias=dias))
    except Exception as e:
        logger.error(f"Error consultando Earth Engine: {e}")
        raise HTTPException(503, f"No se pudo consultar el dato satelital: {e}")


@app.get("/", response_class=HTMLResponse)
def dashboard():
    html = """<!doctype html>
<html lang='es'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Monitor de Metano — Campo Rubiales</title>
<script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'></script>
<style>
  body { font-family: system-ui, sans-serif; background: #0D1220; color: #E8ECF4;
         max-width: 820px; margin: 0 auto; padding: 24px 16px; }
  h1 { font-size: 1.3rem; } h1 span { color: #8B9DFF; }
  p.sub { color: #8A93A6; font-size: .9rem; margin-top: -6px; }
  .card { background: #1B2438; border: 1px solid #39465F; border-radius: 14px;
          padding: 18px; margin-top: 18px; }
  .stats { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 14px; }
  .stat { background: #161F33; border-radius: 10px; padding: 12px 16px; flex: 1;
          min-width: 130px; }
  .stat b { display: block; font-size: 1.4rem; color: #8B9DFF; }
  .stat span { color: #8A93A6; font-size: .8rem; }
  #estado { color: #8A93A6; font-size: .85rem; margin-top: 10px; }
  footer { color: #5A6478; font-size: .78rem; margin-top: 24px; line-height: 1.5; }
</style></head>
<body>
  <h1>🛰️ <span>Monitor de Metano</span> — Campo Rubiales</h1>
  <p class='sub'>Concentración atmosférica de CH₄ (Sentinel-5P/TROPOMI, dato público) sobre el área del campo.</p>

  <div class='card'>
    <canvas id='grafico' height='110'></canvas>
    <div class='stats' id='stats'></div>
    <div id='estado'>Cargando datos satelitales…</div>
  </div>

  <footer>
    Fuente: Copernicus Sentinel-5P (procesado por ESA), producto TROPOMI Level 3
    CH4, vía Google Earth Engine. Revisita ~2 días. Este es un promedio regional
    (no puntual por cluster) — un pico no confirma una fuga específica, es una
    señal para cruzar con inspecciones OGI en tierra.
  </footer>

<script>
fetch('/metano/serie?dias=90')
  .then(r => r.json())
  .then(datos => {
    document.getElementById('estado').textContent = datos.length + ' lecturas satelitales en los últimos 90 días.';
    const fechas = datos.map(d => d.fecha);
    const valores = datos.map(d => d.ch4_ppb);

    new Chart(document.getElementById('grafico'), {
      type: 'line',
      data: {
        labels: fechas,
        datasets: [{
          label: 'CH₄ (ppb, promedio regional)',
          data: valores,
          borderColor: '#8B9DFF',
          backgroundColor: 'rgba(139,157,255,0.15)',
          fill: true, tension: 0.3, pointRadius: 2,
        }]
      },
      options: {
        scales: {
          x: { ticks: { color: '#8A93A6', maxTicksLimit: 8 }, grid: { color: '#222C42' } },
          y: { ticks: { color: '#8A93A6' }, grid: { color: '#222C42' } },
        },
        plugins: { legend: { labels: { color: '#E8ECF4' } } },
      }
    });

    if (valores.length) {
      const prom = (valores.reduce((a,b)=>a+b,0)/valores.length).toFixed(1);
      const max = Math.max(...valores).toFixed(1);
      const min = Math.min(...valores).toFixed(1);
      document.getElementById('stats').innerHTML = `
        <div class='stat'><b>${prom}</b><span>Promedio (ppb)</span></div>
        <div class='stat'><b>${max}</b><span>Máximo (ppb)</span></div>
        <div class='stat'><b>${min}</b><span>Mínimo (ppb)</span></div>
      `;
    }
  })
  .catch(e => {
    document.getElementById('estado').textContent = '⚠️ No se pudo cargar el dato satelital (revisa que EE_SERVICE_ACCOUNT_JSON esté configurado).';
  });
</script>
</body></html>"""
    return HTMLResponse(html)


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok", "app": "Monitor de Metano Satelital"}
