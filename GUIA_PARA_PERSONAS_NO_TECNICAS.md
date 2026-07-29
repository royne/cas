# Guía simple: qué hace la automatización de CAS

## En una frase

Este paquete ayuda a revisar pedidos de Dropi que llevan demasiado tiempo sin movimiento, prepara y crea casos de soporte (CAS) solo cuando corresponde, y permite hacer seguimiento posterior de forma controlada.

No reemplaza a la persona responsable: organiza la información, reduce trabajo repetitivo y pone barreras para evitar acciones accidentales.

## Qué problema resuelve

Cuando una guía no cambia de estado durante muchas horas, puede requerir una gestión con la transportadora mediante un CAS.

Sin automatización, una persona tendría que:

1. Descargar pedidos.
2. Buscar guías una por una.
3. Abrir el detalle de cada pedido.
4. Revisar el historial de movimientos.
5. Decidir si está realmente detenido.
6. Revisar si ya existe un CAS.
7. Tomar evidencia.
8. Crear el CAS.
9. Recordar hacer seguimiento más adelante.

El paquete ordena estas etapas y guarda una bitácora local de lo realizado.

## Qué guarda y dónde

Cada instalación crea su propia carpeta de trabajo llamada `runtime`.

Dentro de ella guarda:

- una base de datos local (`automation.sqlite3`);
- un snapshot de pedidos importado desde Excel o, si está habilitado, desde MCP;
- evidencias capturadas para CAS;
- resultados de evaluaciones y seguimientos.

No usa la base de datos de otra instalación. Cada persona, empresa o computador tiene su propio historial local.

## Qué NO guarda

El paquete no debe guardar ni compartir:

- contraseñas;
- tokens;
- cookies;
- sesión del navegador;
- credenciales de Dropi;
- datos de otra empresa;
- canales de mensajería;
- archivos de otra operación.

La persona debe iniciar sesión manualmente en su propio navegador de Dropi.

## Las etapas del proceso

### 1. Instalación y preparación local

Los comandos iniciales crean las carpetas y la base de datos local.

En esta etapa no se abre Dropi, no se descargan pedidos y no se crean CAS.

```bash
dropi-cas doctor --config ./config.toml
dropi-cas init --config ./config.toml
```

### 2. Revisar que Dropi esté disponible

La persona abre su navegador, inicia sesión en Dropi y permite que el paquete compruebe que ve la pantalla de pedidos.

```bash
dropi-cas diagnose-dropi --config ./config.toml --allow-external-read
```

Este paso solo revisa la sesión. No crea ni modifica nada.

### 3. Elegir cómo traer los pedidos: Excel o MCP

Cada instalación puede usar una de dos fuentes. La elección se hace en el archivo privado `config.toml`.

#### Opción A — Excel: disponible para todos

Esta es la opción predeterminada. La persona inicia sesión en Dropi desde el navegador y el paquete solicita el informe oficial de pedidos.

```toml
[orders_source]
provider = "excel"
```

Después ejecuta:

```bash
dropi-cas sync --config ./config.toml --allow-external-read
```

El paquete descarga el Excel a su propia carpeta e importa los pedidos a su base local. No crea CAS, no crea chats y no envía mensajes.

#### Opción B — MCP: datos frescos sin descargar Excel

Esta opción solo sirve para personas o empresas que ya tienen acceso al MCP `ecommerce360` en Hermes. No se comparte una cuenta MCP entre instalaciones.

Antes de activarla, la persona responsable debe:

1. Tener Hermes instalado y configurado en su computador.
2. Conectar su propia cuenta MCP `ecommerce360` dentro de Hermes.
3. Confirmar que la conexión responde:

```bash
hermes mcp list
hermes mcp test ecommerce360
```

4. Cambiar el `config.toml` privado del paquete:

```toml
[orders_source]
provider = "mcp"
mcp_config_path = "~/.hermes/config.yaml"
mcp_window_days = 25
```

5. Ejecutar el mismo comando de lectura:

```bash
dropi-cas sync --config ./config.toml --allow-external-read
```

Con MCP, el paquete consulta los pedidos actuales, los guarda en su propia base local y no abre el navegador para esa importación. Si el MCP informa que el rango quedó incompleto, el paquete se detiene y no importa datos parciales.

El archivo `config.toml` solo apunta a la configuración privada de Hermes. No debe copiar tokens, contraseñas ni datos de otra empresa dentro del paquete.

### 4. Revisar el historial real de una guía

Para saber si una guía está realmente detenida, no basta con mirar el Excel. El paquete puede abrir el detalle de una guía y leer sus movimientos reales.

```bash
dropi-cas refresh-history \
  --config ./config.toml \
  --guide NUMERO_DE_GUIA \
  --allow-external-read
```

Guarda el último movimiento real y su fecha en la base local.

### 5. Encontrar candidatos a CAS

Una guía se considera candidata si sigue abierta, tiene guía, tiene movimiento real registrado y supera el número de horas configurado sin actualización.

```bash
dropi-cas candidates --config ./config.toml
```

El número de horas se puede ajustar en `config.toml`. Por defecto se usa 24 horas.

Este comando solo muestra una lista: no crea CAS.

### 6. Simular el proceso completo

Antes de crear algo real, se ejecuta una simulación.

```bash
dropi-cas run --config ./config.toml --dry-run
```

La simulación muestra qué pedidos serían tratados, pero no abre el wizard de CAS, no toma evidencia y no envía mensajes.

### 7. Crear un CAS real

La creación real exige permisos explícitos y debe comenzar con una sola guía o un límite de uno.

```bash
dropi-cas run \
  --config ./config.toml \
  --execute \
  --limit 1 \
  --allow-external-read \
  --allow-external-writes \
  --case-service-type-id "ID_DE_SERVICIO"
```

Antes de crear un CAS, el proceso:

1. vuelve a leer el historial de la guía;
2. valida que siga siendo candidata;
3. revisa la elegibilidad del CAS;
4. captura evidencia visible del pedido;
5. intenta detectar si ya existe un caso;
6. crea el CAS solo si Dropi lo permite;
7. guarda localmente el chat confirmado y programa un seguimiento pendiente.

### Protección contra duplicados

Si Dropi muestra que la orden ya tiene un CAS abierto, el proceso se detiene.

No debe crear un segundo caso, subir evidencia ni registrar un CAS nuevo como si hubiera sido creado.

## Seguimientos (follow-ups)

Cuando se confirma un CAS, el paquete registra localmente un seguimiento pendiente. Por defecto queda programado para 48 horas después.

Primero se puede revisar qué seguimientos vencieron sin enviar nada:

```bash
dropi-cas followups --config ./config.toml --dry-run
```

Para enviar un seguimiento real:

```bash
dropi-cas followups \
  --config ./config.toml \
  --execute \
  --allow-external-read \
  --allow-external-writes \
  --case-service-type-id "ID_DE_SERVICIO"
```

Antes de enviar, el proceso vuelve a revisar que:

- la guía continúe sin movimiento suficiente;
- el CAS siga confirmado como activo;
- el seguimiento siga pendiente.

Si la guía ya se movió o el caso activo no se puede confirmar, el follow-up se marca como omitido y no se envía un mensaje.

## Reporte local

El comando siguiente muestra un resumen local:

```bash
dropi-cas report --config ./config.toml
```

Incluye, entre otros datos:

- número de pedidos importados;
- CAS abiertos registrados por el paquete;
- follow-ups pendientes;
- follow-ups vencidos.

## Reglas de seguridad importantes

Hay dos permisos que una persona debe escribir de forma explícita:

- `--allow-external-read`: permite leer información de Dropi.
- `--allow-external-writes`: permite crear CAS o enviar follow-ups.

Sin esas opciones, los comandos que afectan Dropi se bloquean.

Además:

- `--dry-run` nunca crea CAS ni envía mensajes;
- `--execute` declara que se quiere realizar una acción real;
- `--limit 1` permite probar una sola guía antes de procesar más;
- cada acción confirmada queda registrada en la SQLite local.

## Qué debe revisar una persona antes de usar el modo real

1. Que el navegador tenga la sesión correcta de Dropi.
2. Que el `config.toml` apunte a la carpeta de trabajo deseada.
3. Que primero se haya ejecutado `sync` y `run --dry-run`.
4. Que las guías candidatas tengan sentido para el negocio.
5. Que la primera prueba se haga con `--limit 1`.
6. Que se revise el resultado local con `report`.

## Qué no hace todavía por sí solo

El paquete no instala un horario automático por defecto.

Una persona, Hermes, cron de Linux o un scheduler externo debe decidir cuándo ejecutar los comandos. Esto es intencional: evita que una instalación recién creada comience a crear CAS o enviar mensajes automáticamente.

## Resumen final

El proceso separa claramente tres niveles:

```text
Consultar información: seguro y de solo lectura.
Simular decisiones: seguro y sin cambios externos.
Crear CAS o enviar mensajes: acción real, con permisos explícitos.
```

La recomendación es usar siempre este orden:

```text
instalar → doctor → init → diagnose-dropi → sync → refresh-history → candidates → dry-run → ejecutar una guía controlada
```
