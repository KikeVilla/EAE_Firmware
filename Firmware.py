"""
EPIROC EAE ENGINEERING CHALLENGE - SECTION 7.1: FIRMWARE
Candidate: Jorge Enrique Villa Chacon
Features: CANBUS Simulation, PID Control, State Machine, CLI Arguments.
"""

import sys
import math

class PIDController:
    """Standard PID logic to manage cooling setpoints."""
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0

    def compute(self, current_value):
        error = self.setpoint - current_value
        self.integral += error
        # Anti-windup: limit integral to avoid massive overshoots
        self.integral = max(-50, min(50, self.integral))
        derivative = error - self.prev_error
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return max(0, min(100, output))

class EpirocCoolingFirmware:
    def __init__(self, target_temp=65.0):
        self.state = "STANDBY"
        self.pid = PIDController(kp=4.5, ki=0.2, kd=0.8, setpoint=target_temp)
        self.current_temp = 0.0

    def update_system(self, temp, ignition, coolant_ok):
        """Processes the state machine and hardware logic."""
        self.current_temp = temp

        # State 1: STANDBY / OFF
        if not ignition:
            self.state = "STANDBY"
            return self.send_canbus(0, 0)

        # State 2: ALARM (Critical Safety - Point 7.5)
        if not coolant_ok:
            self.state = "ALARM"
            return self.send_canbus(0, 0)

        # State 3: RUNNING (PID active)
        output_pwm = self.pid.compute(temp)
        
        if temp > 80:
            self.state = "HIGH_TEMP"
            pump_pwm = 100  # Max cooling override
            fan_pwm = output_pwm
        else:
            self.state = "NORMAL"
            pump_pwm = output_pwm
            fan_pwm = output_pwm if temp > 60 else 0

        return self.send_canbus(pump_pwm, fan_pwm)

    def send_canbus(self, pump, fan):
        """Simulates J1939 CANBUS messaging (Point 7.1.1)."""
        # Simulated CAN ID for Cooling Status: 0x18FECA01
        can_msg = {
            "ID": "0x18FECA01",
            "State": self.state,
            "Temp": f"{self.current_temp}C",
            "Pump_OUT3": f"{round(pump, 1)}%",
            "Fan_OUT5": f"{round(fan, 1)}%"
        }
        print(f"[CANBUS TX] {can_msg}")
        return pump, fan

if __name__ == "__main__":
    # Point 7.1.4: Command Line Arguments for Setpoints
    setpoint = 65.0
    if len(sys.argv) > 1:
        try:
            setpoint = float(sys.argv[1])
            print(f"Firmware initialized with Custom Setpoint: {setpoint}C")
        except ValueError:
            print("Invalid setpoint argument. Defaulting to 65.0C")

    # Simulation Run
    ecu = EpirocCoolingFirmware(target_temp=setpoint)
    print("\n--- Running Cooling Loop Simulation ---")
    ecu.update_system(temp=50.0, ignition=True, coolant_ok=True)
    ecu.update_system(temp=75.0, ignition=True, coolant_ok=True)
    ecu.update_system(temp=90.0, ignition=True, coolant_ok=True)
    ecu.update_system(temp=90.0, ignition=True, coolant_ok=False) # Test Alarm