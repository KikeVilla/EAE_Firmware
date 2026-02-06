"""
UNIT TESTING FOR EAE_FIRMWARE
Candidate: Jorge Enrique Villa Chacon
Requirements: Point 7.1.7 (Unit Testing)
"""
import sys
import os

# Esto le dice a Python que busque en la carpeta donde está este archivo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from firmware import EpirocCoolingFirmware
import unittest
from firmware import EpirocCoolingFirmware

class TestCoolingFirmware(unittest.TestCase):
    
    def setUp(self):
        """Inicializa el sistema con el setpoint por defecto de 65.0°C."""
        self.ecu = EpirocCoolingFirmware(target_temp=65.0)

    def test_standby_mode(self):
        """Verifica que el sistema permanezca en STANDBY si la ignición (IN5) está OFF."""
        # Datos: Temp alta, Nivel OK, pero Ignición OFF
        pump, fan = self.ecu.update_system(temp=90.0, ignition=False, level_ok=True)
        self.assertEqual(pump, 0)
        self.assertEqual(fan, 0)
        self.assertEqual(self.ecu.state, "STANDBY")

    def test_alarm_mode_safety(self):
        """Verifica la parada de emergencia si el LMC100 (IN4) detecta bajo nivel [Punto 7.5]."""
        # Datos: Ignición ON, Temp operativa, pero Nivel FALLA
        pump, fan = self.ecu.update_system(temp=70.0, ignition=True, level_ok=False)
        self.assertEqual(pump, 0)
        self.assertEqual(fan, 0)
        self.assertEqual(self.ecu.state, "ALARM")

    def test_high_temp_override(self):
        """Verifica que la bomba WP32 (OUT3) suba al 100% si se superan los 80°C [Punto 7.1.3]."""
        # Datos: Temp de 85°C supera el umbral de HIGH_TEMP definido en firmware.py
        pump, fan = self.ecu.update_system(temp=85.0, ignition=True, level_ok=True)
        self.assertEqual(pump, 100.0)
        self.assertEqual(self.ecu.state, "HIGH_TEMP")

    def test_pid_normal_operation(self):
        """Verifica que en condiciones normales el sistema esté en estado NORMAL."""
        # Datos: Temp por debajo del umbral de emergencia pero cerca del setpoint
        pump, fan = self.ecu.update_system(temp=60.0, ignition=True, level_ok=True)
        self.assertEqual(self.ecu.state, "NORMAL")
        # El ventilador (OUT5) debería estar apagado bajo 60°C según la lógica definida
        self.assertEqual(fan, 0)

if __name__ == "__main__":
    unittest.main()