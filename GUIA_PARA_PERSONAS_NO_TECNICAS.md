# Guía rápida para usar CAS Dropi

## Solo necesitas hacer esto

### Primera vez

1. Descarga el repositorio.
2. Entra a su carpeta.
3. Ejecuta:

```bash
./scripts/install.sh
```

Al terminar, la automatización queda instalada en esa misma carpeta.

### Cada vez que quieras operar

1. Abre el navegador.
2. Entra a Dropi e inicia sesión con tu propia cuenta.
3. En la carpeta de la automatización ejecuta:

```bash
./ejecutar-cas.sh
```

El proceso consulta pedidos, crea CAS solo donde corresponde, revisa seguimientos y guarda sus reportes.

## Si primero quieres revisar sin hacer cambios

```bash
./ejecutar-cas.sh --dry-run
```

Esta versión puede leer pedidos y preparar el análisis, pero no crea CAS ni envía mensajes.

## Dónde ver los resultados

Al terminar, abre:

```text
runtime/reports/ultimo-resumen.txt
```

Para auditoría técnica completa queda también:

```text
runtime/reports/ultimo-detallado.json
```

## Importante

- Cada persona usa su propia sesión de Dropi.
- No se comparten contraseñas, cookies ni tokens.
- No necesitas configurar Hermes ni MCP para el modo normal.
- El sistema usa Excel oficial de Dropi como fuente normal.
- Los datos CAS necesarios para “Órdenes sin movimiento” ya están listos: no tienes que escribir IDs.
- Las transportadoras se detectan desde cada pedido; no se configuran manualmente.

## Si aparece un problema de navegador

Comprueba que Dropi siga abierto e iniciado sesión. Después vuelve a ejecutar el mismo comando. Si el navegador solicita permitir depuración remota, acepta esa ventana y repite el comando.
