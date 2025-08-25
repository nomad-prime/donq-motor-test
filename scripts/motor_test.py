#!/usr/bin/env python3
"""
TB6612FNG Motor Driver Test Script - gpiozero Version
Tests both motors with forward/backward/stop commands
Compatible with Raspberry Pi 5 using gpiozero library
"""

import time
import sys

try:
    from gpiozero import Motor, OutputDevice
    print("gpiozero imported successfully")
except ImportError as e:
    print(f"Failed to import gpiozero: {e}")
    print("\nInstall with: sudo apt update && sudo apt install python3-gpiozero")
    print("Or: pip3 install gpiozero")
    sys.exit(1)

# Pin definitions for TB6612FNG motor driver
# Motor A pins (forward, backward)
MOTOR_A_FORWARD = 24   # AIN1 - GPIO24
MOTOR_A_BACKWARD = 23  # AIN2 - GPIO23
MOTOR_A_PWM = 12       # PWMA - GPIO12 (PWM0)

# Motor B pins (forward, backward)
MOTOR_B_FORWARD = 22   # BIN1 - GPIO22
MOTOR_B_BACKWARD = 27  # BIN2 - GPIO27
MOTOR_B_PWM = 13       # PWMB - GPIO13 (PWM1)

# Control pin
STBY_PIN = 16          # STBY - GPIO16

# Initialize motor objects and standby control
motor_a = None
motor_b = None
standby = None

def setup_motors():
    """Initialize motor objects using gpiozero"""
    global motor_a, motor_b, standby
    
    try:
        print("\nInitializing motors with gpiozero...")
        
        # Create Motor objects - gpiozero handles PWM automatically
        # Motor(forward_pin, backward_pin, enable_pin) or Motor(forward_pin, backward_pin)
        # For TB6612FNG, we'll use the PWM pins as enable pins
        motor_a = Motor(forward=MOTOR_A_FORWARD, backward=MOTOR_A_BACKWARD, enable=MOTOR_A_PWM)
        motor_b = Motor(forward=MOTOR_B_FORWARD, backward=MOTOR_B_BACKWARD, enable=MOTOR_B_PWM)
        
        # Create standby control pin
        standby = OutputDevice(STBY_PIN, active_high=True, initial_value=False)
        
        print("  Motor A configured (Forward=GPIO{}, Backward=GPIO{}, Enable=GPIO{})".format(
            MOTOR_A_FORWARD, MOTOR_A_BACKWARD, MOTOR_A_PWM))
        print("  Motor B configured (Forward=GPIO{}, Backward=GPIO{}, Enable=GPIO{})".format(
            MOTOR_B_FORWARD, MOTOR_B_BACKWARD, MOTOR_B_PWM))
        print("  Standby pin configured (GPIO{})".format(STBY_PIN))
        
        # Enable the motor driver
        standby.on()
        print("\nMotor driver enabled (STBY=HIGH)")
        print("Motor setup successful!")
        
        return True
        
    except Exception as e:
        print(f"\n*** MOTOR SETUP FAILED ***")
        print(f"Error: {e}")
        print("\n=== TROUBLESHOOTING ===")
        print("1. Make sure gpiozero is installed:")
        print("   sudo apt update && sudo apt install python3-gpiozero")
        print("\n2. Check wiring connections")
        print("\n3. Try running with sudo if needed:")
        print("   sudo python3 motor_test.py")
        
        raise

def motor_a_forward(speed=50):
    """Move Motor A forward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    motor_a.forward(speed/100.0)  # gpiozero uses 0.0-1.0 range
    print(f"Motor A: Forward at {speed}% speed")

def motor_a_backward(speed=50):
    """Move Motor A backward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    motor_a.backward(speed/100.0)  # gpiozero uses 0.0-1.0 range
    print(f"Motor A: Backward at {speed}% speed")

def motor_a_stop():
    """Stop Motor A"""
    motor_a.stop()
    print("Motor A: Stopped")

def motor_b_forward(speed=50):
    """Move Motor B forward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    motor_b.forward(speed/100.0)  # gpiozero uses 0.0-1.0 range
    print(f"Motor B: Forward at {speed}% speed")

def motor_b_backward(speed=50):
    """Move Motor B backward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    motor_b.backward(speed/100.0)  # gpiozero uses 0.0-1.0 range
    print(f"Motor B: Backward at {speed}% speed")

def motor_b_stop():
    """Stop Motor B"""
    motor_b.stop()
    print("Motor B: Stopped")

def stop_all_motors():
    """Stop both motors"""
    motor_a.stop()
    motor_b.stop()

def cleanup():
    """Clean up motors and GPIO safely"""
    try:
        stop_all_motors()
        
        # Disable motor driver
        if standby:
            standby.off()
            
        # Close motor objects (gpiozero handles cleanup automatically)
        if motor_a:
            motor_a.close()
        if motor_b:
            motor_b.close()
        if standby:
            standby.close()
            
        print("Motor cleanup complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def run_motor_test():
    """Run a comprehensive motor test"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test - Automated Mode (gpiozero)")
    print("="*50)
    print("\nPin Configuration:")
    print(f"Motor A: Forward=GPIO{MOTOR_A_FORWARD}, Backward=GPIO{MOTOR_A_BACKWARD}, PWM=GPIO{MOTOR_A_PWM}")
    print(f"Motor B: Forward=GPIO{MOTOR_B_FORWARD}, Backward=GPIO{MOTOR_B_BACKWARD}, PWM=GPIO{MOTOR_B_PWM}")
    print(f"STBY=GPIO{STBY_PIN}")
    print("\n⚠️  Make sure:")
    print("  - STBY is connected to GPIO16")
    print("  - VM is connected to motor power supply (6-12V)")
    print("  - VCC is connected to 3.3V")
    print("  - GND connections are secure")
    print("="*50)
    
    try:
        # Setup
        setup_motors()
        time.sleep(1)
        
        # Test Motor A
        print("\n=== Testing Motor A ===")
        motor_a_forward(30)
        time.sleep(2)
        motor_a_stop()
        time.sleep(1)
        
        motor_a_backward(30)
        time.sleep(2)
        motor_a_stop()
        time.sleep(1)
        
        # Test Motor B
        print("\n=== Testing Motor B ===")
        motor_b_forward(30)
        time.sleep(2)
        motor_b_stop()
        time.sleep(1)
        
        motor_b_backward(30)
        time.sleep(2)
        motor_b_stop()
        time.sleep(1)
        
        # Test both motors together
        print("\n=== Testing Both Motors ===")
        print("Both forward...")
        motor_a_forward(40)
        motor_b_forward(40)
        time.sleep(2)
        
        print("Both backward...")
        motor_a_backward(40)
        motor_b_backward(40)
        time.sleep(2)
        
        print("Turning left (Motor A back, Motor B forward)...")
        motor_a_backward(40)
        motor_b_forward(40)
        time.sleep(2)
        
        print("Turning right (Motor A forward, Motor B back)...")
        motor_a_forward(40)
        motor_b_backward(40)
        time.sleep(2)
        
        stop_all_motors()
        print("\n✅ Test Complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
    finally:
        cleanup()

def interactive_mode():
    """Interactive motor control"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test - Interactive Mode (gpiozero)")
    print("="*50)
    print("\nCommands:")
    print("  Motor A: af (forward), ab (backward), as (stop)")
    print("  Motor B: bf (forward), bb (backward), bs (stop)")
    print("  Both: stop (stop all), q (quit)")
    print("="*50)
    
    try:
        setup_motors()
        
        while True:
            cmd = input("\nEnter command: ").lower().strip()
            
            if cmd == 'q':
                break
            elif cmd == 'af':
                motor_a_forward(50)
            elif cmd == 'ab':
                motor_a_backward(50)
            elif cmd == 'as':
                motor_a_stop()
            elif cmd == 'bf':
                motor_b_forward(50)
            elif cmd == 'bb':
                motor_b_backward(50)
            elif cmd == 'bs':
                motor_b_stop()
            elif cmd == 'stop':
                stop_all_motors()
            else:
                print("Unknown command! Use: af, ab, as, bf, bb, bs, stop, q")
                
    except KeyboardInterrupt:
        print("\n⚠️  Exiting interactive mode")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        cleanup()

def diagnostic_mode():
    """Run diagnostic checks without motor control"""
    import platform
    import os
    
    print("\n" + "="*50)
    print("TB6612FNG Diagnostic Mode (gpiozero)")
    print("="*50)
    
    print("\n1. System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {sys.version}")
    print(f"   User: {os.environ.get('USER', 'unknown')}")
    print(f"   Is root: {os.geteuid() == 0}")
    
    print("\n2. GPIO Library:")
    try:
        from gpiozero import Device
        print("   gpiozero library: Available")
        print(f"   Pin factory: {Device.pin_factory.__class__.__name__}")
    except ImportError:
        print("   ERROR: gpiozero not available")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n3. Checking /proc/cpuinfo:")
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'Hardware' in line or 'Revision' in line or 'Model' in line:
                    print(f"   {line.strip()}")
    except:
        print("   ERROR: Cannot read /proc/cpuinfo")
    
    print("\n4. Checking GPIO access:")
    for dev in ['/dev/gpiochip0', '/dev/gpiochip1', '/dev/gpiomem']:
        if os.path.exists(dev):
            try:
                stat = os.stat(dev)
                print(f"   {dev}: exists (mode: {oct(stat.st_mode)})")
            except:
                print(f"   {dev}: exists but cannot stat")
        else:
            print(f"   {dev}: not found")
    
    print("\n5. Testing basic pin setup (no motors):")
    try:
        from gpiozero import LED
        test_pin = LED(STBY_PIN)
        test_pin.off()
        test_pin.close()
        print("   ✅ Basic pin control works")
    except Exception as e:
        print(f"   ❌ Pin control failed: {e}")
        print("   Try: sudo apt update && sudo apt install python3-gpiozero")

if __name__ == "__main__":
    print("TB6612FNG Motor Test Script")
    print("1. Run automated test")
    print("2. Interactive mode")
    print("3. Diagnostic mode (check system without motors)")
    
    choice = input("Choose option (1, 2, or 3): ").strip()
    
    if choice == "1":
        run_motor_test()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        diagnostic_mode()
    else:
        print("Invalid choice!")