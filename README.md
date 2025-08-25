# TB6612FNG Motor Driver Test for Raspberry Pi Robot

Cross-platform motor driver testing suite for TB6612FNG dual motor driver.

## Features

- Platform detection (auto-detects Raspberry Pi vs development machine)
- Simulated GPIO on Mac/Windows for development
- Interactive and automated test modes
- Proper GPIO cleanup and error handling
- Hardware PWM support on compatible pins

## Pin Configuration

Updated to use hardware PWM-capable pins:

| Function | GPIO Pin | Notes                            |
| -------- | -------- | -------------------------------- |
| AIN1     | GPIO 24  | Motor A direction 1              |
| AIN2     | GPIO 23  | Motor A direction 2              |
| PWMA     | GPIO 12  | Motor A speed (HW PWM)           |
| BIN1     | GPIO 22  | Motor B direction 1              |
| BIN2     | GPIO 27  | Motor B direction 2              |
| PWMB     | GPIO 13  | Motor B speed (HW PWM)           |
| STBY     | GPIO 16  | Standby (must be HIGH to enable) |

## Installation

### On Mac (Development)

```bash
pip install -r requirements-dev.txt
# or with uv:
uv pip install -r requirements-dev.txt
```

### On Raspberry Pi

```bash
pip install -r requirements-pi.txt
sudo python3 scripts/motor_test.py
```

## Usage

Run the improved script that handles both platforms:

```bash
# On Mac (development mode)
python scripts/motor_test.py

# On Raspberry Pi (requires sudo for GPIO access)
sudo python3 scripts/motor_test.py
```

Choose between:

1. Automated test - Runs through all motor combinations
2. Interactive mode - Manual control with commands

## Important Notes

1. **Power Supply**: Ensure VM pin on TB6612FNG is connected to appropriate motor voltage (5-12V)
2. **STBY Pin**: Must be connected and set HIGH to enable the driver
3. **GPIO Access**: On Raspberry Pi, script requires sudo for GPIO access
4. **PWM Pins**: Uses GPIO 18 and 19 which support hardware PWM on all Pi models
