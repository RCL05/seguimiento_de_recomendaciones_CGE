from django.http import HttpResponse


def dashboard(request):
    return HttpResponse(
        """<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>SITRA-CGE UNL</title>
<style>body{font-family:system-ui;margin:0;background:#f4f7fb;color:#172033}
header{background:#123b64;color:white;padding:2rem 8vw}main{max-width:1000px;margin:2rem auto;padding:0 1rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}
.card{background:white;border-radius:12px;padding:1.2rem;box-shadow:0 2px 8px #0001}
.status{color:#0b7650;font-weight:700}</style></head>
<body><header><h1>SITRA-CGE UNL</h1><p>Seguimiento y trazabilidad de recomendaciones CGE</p></header>
<main><h2>Panel de demostración</h2><div class="cards">
<section class="card"><strong>Recomendaciones</strong><p id="total">Cargando...</p></section>
<section class="card"><strong>Estado del servicio</strong><p class="status">Disponible</p></section>
<section class="card"><strong>Flujo</strong><p>Pendiente → Ejecución → Revisión → Cumplida</p></section>
</div><p>API: <a href="/health/">/health/</a></p></main>
<script>fetch('/api/v1/recomendaciones').then(r=>r.json()).then(x=>{document.querySelector('#total').textContent=(x.data||[]).length+' registradas'}).catch(()=>document.querySelector('#total').textContent='Sin conexión')</script>
</body></html>""",
        content_type="text/html; charset=utf-8",
    )
