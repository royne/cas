# Dropi CAS Automation

Paquete portable para gestionar CAS de “Órdenes sin movimiento” desde una instalación propia. No usa ni copia bases de datos, rutas, canales, sesiones, cookies o credenciales de otra persona.

## Instalación sencilla

```bash
git clone https://github.com/royne/cas.git dropi-cas-automation
cd dropi-cas-automation
./scripts/install.sh
```

El instalador crea el entorno Python, instala el paquete, instala `browser-harness` cuando falta, crea `config.toml`, inicializa el workspace local y deja listo el lanzador.

## Uso normal

1. Abrir Dropi en el navegador e iniciar sesión con la cuenta propia.
2. Desde la carpeta del paquete ejecutar:

```bash
./ejecutar-cas.sh
```

Ese único comando realiza: sincronización de pedidos, evaluación, creación de CAS elegibles, revisión de follow-ups y generación de reporte.

Para comprobar una corrida sin crear CAS ni enviar mensajes:

```bash
./ejecutar-cas.sh --dry-run
```

Los reportes quedan en:

```text
runtime/reports/ultimo-resumen.txt
runtime/reports/ultimo-detallado.json
```

## Qué configura cada instalación

`config.toml` pertenece solo a quien instaló el paquete. Por defecto usa el informe Excel oficial de la sesión Dropi del navegador. No necesita Hermes ni MCP para funcionar así.

MCP/ecommerce360 es opcional y solo se puede activar si el dueño de esa instalación ya tiene su propia conexión configurada.

Los metadatos técnicos de CAS para “Órdenes sin movimiento” ya vienen definidos. No son IDs de transportadoras: la transportadora se detecta en cada orden, usando los datos reales de Dropi.

## Qué hace la corrida operacional

- descarga e importa la fuente de órdenes configurada;
- identifica órdenes con movimiento real vencido;
- revalida la guía y verifica que no exista un CAS activo;
- guarda evidencia local antes de crear el CAS;
- crea CAS únicamente tras confirmación de Dropi;
- revisa y envía follow-ups que correspondan;
- guarda bitácora y reportes dentro de su propio workspace.

La única intervención manual inevitable es iniciar sesión en la cuenta propia de Dropi: el paquete nunca distribuye ni guarda credenciales, tokens o cookies.

## Operación avanzada

El lanzador es equivalente a:

```bash
.venv/bin/dropi-cas operate --config ./config.toml --execute
.venv/bin/dropi-cas operate --config ./config.toml --dry-run
```

Se pueden usar los comandos individuales (`sync`, `candidates`, `run`, `followups`, `report`) para diagnóstico técnico. No son necesarios para el uso cotidiano.

## Pruebas locales

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Las pruebas de navegador usan runners falsos; verifican contratos y permisos locales, no validan selectores contra una sesión Dropi real.
