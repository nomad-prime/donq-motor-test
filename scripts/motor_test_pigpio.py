#!/usr/bin/env python3
"""
TB6612FNG Motor Driver Test Script - Using pigpio
Alternative implementation using pigpio library which often works better
on newer Raspberry Pi systems when RPi.GPIO has issues
"""

import time
import sys
import platform
import os

print('Platform:', platform.system(), platform.machine())

# Check if running on Raspberry Pi
IS_RASPBERRY_PI = platform.system() == 'Linux' and ('aarch' in platform.machine() or 'arm' in platform.machine())

if IS_RASPBERRY_PI:
    try:
        import pigpio
        print("pigpio library loaded successfully")
    except ImportError:
        print("Error: pigpio not installed")
        print("Install with:")
        print("  sudo apt-get update")
        print("  sudo apt-get install python3-pigpio")
        print("  sudo systemctl enable pigpiod")
        print("  sudo systemctl start pigpiod")
        sys.exit(1)
else:
    print("This script requires a Raspberry Pi with pigpio")
    print("For development, use motor_test.py with fake-rpi instead")
    sys.exit(1)

# Pin definitions
AIN1 = 24   # GPIO24
AIN2 = 23   # GPIO23
PWMA = 12   # GPIO12 (PWM0)

BIN1 = 22   # GPIO22
BIN2 = 27   # GPIO27
PWMB = 13   # GPIO13 (PWM1)

STBY = 16   # GPIO16

# PWM frequency
PWM_FREQUENCY = 1000  # 1kHz

class MotorController:
    def __init__(self):
        self.pi = None
        self.connected = False
        
    def connect(self):
        """Connect to pigpio daemon"""
        try:
            print("\nConnecting to pigpio daemon...")
            self.pi = pigpio.pi()
            
            if not self.pi.connected:
                print("Failed to connect to pigpio daemon")
                print("\nMake sure pigpiod is running:")
                print("  sudo systemctl start pigpiod")
                print("Or start manually:")
                print("  sudo pigpiod")
                return False
            
            print("Connected to pigpio daemon")
            self.connected = True
            
            # Setup pins
            self.setup_pins()
            return True
            
        except Exception as e:
            print(f"Error connecting to pigpio: {e}")
            return False
    
    def setup_pins(self):
        """Setup GPIO pins"""
        print("\nConfiguring GPIO pins...")
        
        # Set pin modes
        for pin in [AIN1, AIN2, BIN1, BIN2, STBY]:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)  # Initialize to LOW
            
        # Setup PWM pins
        self.pi.set_mode(PWMA, pigpio.OUTPUT)
        self.pi.set_mode(PWMB, pigpio.OUTPUT)
        
        # Set PWM frequency
        self.pi.set_PWM_frequency(PWMA, PWM_FREQUENCY)
        self.pi.set_PWM_frequency(PWMB, PWM_FREQUENCY)
        
        # Initialize PWM to 0
        self.pi.set_PWM_dutycycle(PWMA, 0)
        self.pi.set_PWM_dutycycle(PWMB, 0)
        
        # Enable motor driver
        self.pi.write(STBY, 1)
        print("Motor driver enabled (STBY=HIGH)")
        print("GPIO setup complete")
    
    def motor_a_forward(self, speed=50):
        """Move Motor A forward (speed: 0-100)"""
        if not self.connected:
            return
        
        speed = max(0, min(100, speed))
        duty_cycle = int(speed * 255 / 100)  # Convert to 0-255 range
        
        self.pi.write(AIN1, 1)
        self.pi.write(AIN2, 0)
        self.pi.set_PWM_dutycycle(PWMA, duty_cycle)
        print(f"Motor A: Forward at {speed}% speed")
    
    def motor_a_backward(self, speed=50):
        """Move Motor A backward (speed: 0-100)"""
        if not self.connected:
            return
        
        speed = max(0, min(100, speed))
        duty_cycle = int(speed * 255 / 100)
        
        self.pi.write(AIN1, 0)
        self.pi.write(AIN2, 1)
        self.pi.set_PWM_dutycycle(PWMA, duty_cycle)
        print(f"Motor A: Backward at {speed}% speed")
    
    def motor_a_stop(self):
        """Stop Motor A"""
        if not self.connected:
            return
        
        self.pi.write(AIN1, 0)
        self.pi.write(AIN2, 0)
        self.pi.set_PWM_dutycycle(PWMA, 0)
        print("Motor A: Stopped")
    
    def motor_b_forward(self, speed=50):
        """Move Motor B forward (speed: 0-100)"""
        if not self.connected:
            return
        
        speed = max(0, min(100, speed))
        duty_cycle = int(speed * 255 / 100)
        
        self.pi.write(BIN1, 1)
        self.pi.write(BIN2, 0)
        self.pi.set_PWM_dutycycle(PWMB, duty_cycle)
        print(f"Motor B: Forward at {speed}% speed")
    
    def motor_b_backward(self, speed=50):
        """Move Motor B backward (speed: 0-100)"""
        if not self.connected:
            return
        
        speed = max(0, min(100, speed))
        duty_cycle = int(speed * 255 / 100)
        
        self.pi.write(BIN1, 0)
        self.pi.write(BIN2, 1)
        self.pi.set_PWM_dutycycle(PWMB, duty_cycle)
        print(f"Motor B: Backward at {speed}% speed")
    
    def motor_b_stop(self):
        """Stop Motor B"""
        if not self.connected:
            return
        
        self.pi.write(BIN1, 0)
        self.pi.write(BIN2, 0)
        self.pi.set_PWM_dutycycle(PWMB, 0)
        print("Motor B: Stopped")
    
    def stop_all(self):
        """Stop both motors"""
        self.motor_a_stop()
        self.motor_b_stop()
    
    def cleanup(self):
        """Clean up GPIO and close connection"""
        if self.connected and self.pi:
            print("\nCleaning up...")
            self.stop_all()
            self.pi.write(STBY, 0)  # Disable motor driver
            self.pi.stop()
            self.connected = False
            print("Cleanup complete")

def run_automated_test():
    """Run automated motor test"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test (pigpio) - Automated Mode")
    print("="*50)
    
    controller = MotorController()
    
    if not controller.connect():
        print("Failed to initialize motor controller")
        return
    
    try:
        print("\n=== Testing Motor A ===")
        controller.motor_a_forward(30)
        time.sleep(2)
        controller.motor_a_stop()
        time.sleep(1)
        
        controller.motor_a_backward(30)
        time.sleep(2)
        controller.motor_a_stop()
        time.sleep(1)
        
        print("\n=== Testing Motor B ===")
        controller.motor_b_forward(30)
        time.sleep(2)
        controller.motor_b_stop()
        time.sleep(1)
        
        controller.motor_b_backward(30)
        time.sleep(2)
        controller.motor_b_stop()
        time.sleep(1)
        
        print("\n=== Testing Both Motors ===")
        print("Both forward...")
        controller.motor_a_forward(40)
        controller.motor_b_forward(40)
        time.sleep(2)
        
        print("Both backward...")
        controller.motor_a_backward(40)
        controller.motor_b_backward(40)
        time.sleep(2)
        
        print("Turning left...")
        controller.motor_a_backward(40)
        controller.motor_b_forward(40)
        time.sleep(2)
        
        print("Turning right...")
        controller.motor_a_forward(40)
        controller.motor_b_backward(40)
        time.sleep(2)
        
        controller.stop_all()
        print("\n✅ Test Complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        controller.cleanup()

def run_interactive_mode():
    """Interactive motor control"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test (pigpio) - Interactive Mode")
    print("="*50)
    print("\nCommands:")
    print("  Motor A: af (forward), ab (backward), as (stop)")
    print("  Motor B: bf (forward), bb (backward), bs (stop)")
    print("  Both: stop (stop all), q (quit)")
    print("="*50)
    
    controller = MotorController()
    
    if not controller.connect():
        print("Failed to initialize motor controller")
        return
    
    try:
        while True:
            cmd = input("\nEnter command: ").lower().strip()
            
            if cmd == 'q':
                break
            elif cmd == 'af':
                controller.motor_a_forward(50)
            elif cmd == 'ab':
                controller.motor_a_backward(50)
            elif cmd == 'as':
                controller.motor_a_stop()
            elif cmd == 'bf':
                controller.motor_b_forward(50)
            elif cmd == 'bb':
                controller.motor_b_backward(50)
            elif cmd == 'bs':
                controller.motor_b_stop()
            elif cmd == 'stop':
                controller.stop_all()
            else:
                print("Unknown command!")
                
    except KeyboardInterrupt:
        print("\n⚠️  Exiting")
    finally:
        controller.cleanup()

def check_pigpio_daemon():
    """Check if pigpiod is running"""
    print("\nChecking pigpio daemon status...")
    
    # Check if pigpiod process is running
    result = os.system("pgrep pigpiod > /dev/null")
    if result == 0:
        print("✅ pigpiod is running")
        return True
    else:
        print("❌ pigpiod is NOT running")
        print("\nTo start pigpiod:")
        print("  sudo systemctl start pigpiod")
        print("Or:")
        print("  sudo pigpiod")
        return False

if __name__ == "__main__":
    if not IS_RASPBERRY_PI:
        print("This script requires a Raspberry Pi")
        sys.exit(1)
    
    print("TB6612FNG Motor Test - pigpio version")
    print("\nThis version uses pigpio library which often works")
    print("better when RPi.GPIO has SOC detection issues")
    
    # Check daemon status
    check_pigpio_daemon()
    
    print("\nOptions:")
    print("1. Run automated test")
    print("2. Interactive mode")
    print("3. Start pigpiod and run test")
    
    choice = input("\nChoose option (1, 2, or 3): ").strip()
    
    if choice == "1":
        run_automated_test()
    elif choice == "2":
        run_interactive_mode()
    elif choice == "3":
        print("\nStarting pigpiod...")
        os.system("sudo pigpiod")
        time.sleep(2)
        if check_pigpio_daemon():
            run_automated_test()
    else:
        print("Invalid choice!")