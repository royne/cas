import unittest

from dropi_cas_automation.history import parse_order_history


class HistoryParserTests(unittest.TestCase):
    def test_parses_latest_movement_from_order_history(self):
        text = """ORDEN PARA:
Orden #123
Número de Guía: 034000000001
Compañia de envío: carrier-a
Estatus: EN TRANSPORTE
Historial de estados:
#\tFecha Estatus\tEstatus\tUsuario\tComentario
1\t01/01/2026 10:30 AM\tEN BODEGA ORIGEN\toperator\tIngreso
2\t02/01/2026 03:15 PM\tEN TRANSPORTE\toperator\tSalida
Historial de Cartera
"""

        history = parse_order_history(text)

        self.assertEqual(history.order_id, "123")
        self.assertEqual(history.guide, "034000000001")
        self.assertEqual(history.last_movement.status, "EN TRANSPORTE")
        self.assertEqual(history.last_movement.movement_at, "2026-01-02 15:15:00")
