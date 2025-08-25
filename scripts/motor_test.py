#!/usr/bin/env python3
"""
TB6612FNG Motor Driver Test Script - Fixed Version
Tests both motors with forward/backward/stop commands
Cross-platform compatible with improved error handling
"""

import time
import sys
import platform
import os

# Platform detection and GPIO import handling
print('Platform system:', platform.system())
print('Platform machine:', platform.machine())
print('Running as user:', os.environ.get('USER', 'unknown'))

IS_RASPBERRY_PI = False
GPIO = None

if platform.system() == 'Linux' and ('aarch' in platform.machine() or 'arm' in platform.machine()):
    # Running on Raspberry Pi or similar ARM board
    try:
        import RPi.GPIO as GPIO
        IS_RASPBERRY_PI = True
        print("RPi.GPIO imported successfully")
    except ImportError as e:
        print(f"Failed to import RPi.GPIO: {e}")
        print("\nInstall with: sudo apt-get update && sudo apt-get install python3-rpi.gpio")
        print("Or: pip3 install RPi.GPIO")
        sys.exit(1)
else:
    # Running on development machine (Mac/Windows/Linux x86)
    try:
        from fake_rpi.RPi import GPIO
        print("Running in development mode with fake-rpi")
    except ImportError:
        print("Error: fake-rpi not installed. Run: pip install fake-rpi")
        sys.exit(1)

# Pin definitions - Using hardware PWM capable pins on Pi
# Motor A pins
AIN1 = 24   # GPIO24
AIN2 = 23   # GPIO23
PWMA = 12   # GPIO12 (PWM0)

# Motor B pins  
BIN1 = 22   # GPIO22
BIN2 = 27   # GPIO27
PWMB = 13   # GPIO13 (PWM1)

# Control pin
STBY = 16   # GPIO16

def check_gpio_permissions():
    """Check if user has GPIO permissions"""
    if not IS_RASPBERRY_PI:
        return True
    
    # Check if running as root
    if os.geteuid() == 0:
        print("Running as root (sudo)")
        return True
    
    # Check if user is in gpio group
    import grp
    import pwd
    try:
        gpio_gid = grp.getgrnam('gpio').gr_gid
        user_groups = os.getgroups()
        if gpio_gid in user_groups:
            print("User is in gpio group")
            return True
        else:
            username = pwd.getpwuid(os.getuid()).pw_name
            print(f"User '{username}' is NOT in gpio group")
            print(f"Add with: sudo usermod -a -G gpio {username}")
            print("Then logout and login again")
            return False
    except:
        print("Cannot check gpio group membership")
        return False

def setup_gpio():
    """Initialize GPIO pins with better error handling"""
    pwm_a = None
    pwm_b = None
    
    try:
        # Check permissions first
        if IS_RASPBERRY_PI and not check_gpio_permissions():
            print("\nWARNING: May not have GPIO permissions!")
        
        print("\nInitializing GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Set all pins as outputs one by one for better error tracking
        pins = {
            'AIN1': AIN1, 'AIN2': AIN2, 'PWMA': PWMA,
            'BIN1': BIN1, 'BIN2': BIN2, 'PWMB': PWMB,
            'STBY': STBY
        }
        
        for name, pin in pins.items():
            try:
                GPIO.setup(pin, GPIO.OUT)
                print(f"  {name} (GPIO{pin}) configured")
            except Exception as e:
                print(f"  ERROR setting up {name} (GPIO{pin}): {e}")
                raise
        
        # Set up PWM for speed control
        print("\nSetting up PWM channels...")
        try:
            pwm_a = GPIO.PWM(PWMA, 1000)  # 1kHz frequency
            print("  PWM A initialized")
        except Exception as e:
            print(f"  ERROR initializing PWM A: {e}")
            raise
        
        try:
            pwm_b = GPIO.PWM(PWMB, 1000)  # 1kHz frequency
            print("  PWM B initialized")
        except Exception as e:
            print(f"  ERROR initializing PWM B: {e}")
            if pwm_a:
                pwm_a.stop()
            raise
        
        # Start PWM with 0% duty cycle
        pwm_a.start(0)
        pwm_b.start(0)
        print("  PWM channels started")
        
        # Enable the motor driver
        GPIO.output(STBY, GPIO.HIGH)
        print("\nMotor driver enabled (STBY=HIGH)")
        
        if not IS_RASPBERRY_PI:
            print("\nWARNING: Running in simulation mode - no actual GPIO control")
        else:
            print("\nGPIO setup successful!")
        
        return pwm_a, pwm_b
        
    except Exception as e:
        print(f"\n*** GPIO SETUP FAILED ***")
        print(f"Error: {e}")
        
        if IS_RASPBERRY_PI:
            print("\n=== TROUBLESHOOTING ===")
            print("1. Check if running with sudo:")
            print("   sudo python3 motor_test_fixed.py")
            print("\n2. Check RPi.GPIO installation:")
            print("   pip3 list | grep RPi.GPIO")
            print("\n3. Reinstall RPi.GPIO if needed:")
            print("   sudo apt-get install python3-rpi.gpio")
            print("\n4. Check GPIO chip access:")
            print("   ls -l /dev/gpiochip*")
            print("\n5. For 'Cannot determine SOC' error, try:")
            print("   sudo apt-get update")
            print("   sudo apt-get upgrade")
            print("   sudo rpi-update")
            
            # Try to provide more specific help based on error
            error_str = str(e).lower()
            if 'cannot determine soc' in error_str:
                print("\n*** SPECIFIC ERROR: SOC Detection Failed ***")
                print("This usually means:")
                print("- RPi.GPIO can't detect your Pi model")
                print("- /proc/cpuinfo might be missing hardware info")
                print("- Try using pigpio library instead:")
                print("  sudo apt-get install python3-pigpio")
                print("  sudo systemctl start pigpiod")
        
        # Clean up any partially initialized resources
        if pwm_a:
            try:
                pwm_a.stop()
            except:
                pass
        if pwm_b:
            try:
                pwm_b.stop()
            except:
                pass
        
        raise

def motor_a_forward(pwm_a, speed=50):
    """Move Motor A forward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(speed)
    print(f"Motor A: Forward at {speed}% speed")

def motor_a_backward(pwm_a, speed=50):
    """Move Motor A backward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(speed)
    print(f"Motor A: Backward at {speed}% speed")

def motor_a_stop(pwm_a):
    """Stop Motor A"""
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    pwm_a.ChangeDutyCycle(0)
    print("Motor A: Stopped")

def motor_b_forward(pwm_b, speed=50):
    """Move Motor B forward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    pwm_b.ChangeDutyCycle(speed)
    print(f"Motor B: Forward at {speed}% speed")

def motor_b_backward(pwm_b, speed=50):
    """Move Motor B backward at given speed (0-100)"""
    if speed < 0 or speed > 100:
        print(f"Warning: Speed {speed} out of range, clamping to 0-100")
        speed = max(0, min(100, speed))
    
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    pwm_b.ChangeDutyCycle(speed)
    print(f"Motor B: Backward at {speed}% speed")

def motor_b_stop(pwm_b):
    """Stop Motor B"""
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)
    pwm_b.ChangeDutyCycle(0)
    print("Motor B: Stopped")

def stop_all_motors(pwm_a, pwm_b):
    """Stop both motors"""
    if pwm_a:
        motor_a_stop(pwm_a)
    if pwm_b:
        motor_b_stop(pwm_b)

def cleanup(pwm_a=None, pwm_b=None):
    """Clean up GPIO and PWM safely"""
    try:
        if pwm_a and pwm_b:
            stop_all_motors(pwm_a, pwm_b)
        if pwm_a:
            pwm_a.stop()
        if pwm_b:
            pwm_b.stop()
        
        # Try to disable motor driver
        try:
            GPIO.output(STBY, GPIO.LOW)
        except:
            pass
        
        GPIO.cleanup()
        print("GPIO cleanup complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def run_motor_test():
    """Run a comprehensive motor test"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test - Automated Mode")
    print("="*50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Running on Raspberry Pi: {IS_RASPBERRY_PI}")
    print("\nPin Configuration:")
    print(f"Motor A: AIN1=GPIO{AIN1}, AIN2=GPIO{AIN2}, PWMA=GPIO{PWMA}")
    print(f"Motor B: BIN1=GPIO{BIN1}, BIN2=GPIO{BIN2}, PWMB=GPIO{PWMB}")
    print(f"STBY=GPIO{STBY}")
    print("\n⚠️  Make sure:")
    print("  - STBY is connected to GPIO16")
    print("  - VM is connected to motor power supply (6-12V)")
    print("  - VCC is connected to 3.3V")
    print("  - GND connections are secure")
    print("="*50)
    
    pwm_a = None
    pwm_b = None
    
    try:
        # Setup
        pwm_a, pwm_b = setup_gpio()
        time.sleep(1)
        
        # Test Motor A
        print("\n=== Testing Motor A ===")
        motor_a_forward(pwm_a, 30)
        time.sleep(2)
        motor_a_stop(pwm_a)
        time.sleep(1)
        
        motor_a_backward(pwm_a, 30)
        time.sleep(2)
        motor_a_stop(pwm_a)
        time.sleep(1)
        
        # Test Motor B
        print("\n=== Testing Motor B ===")
        motor_b_forward(pwm_b, 30)
        time.sleep(2)
        motor_b_stop(pwm_b)
        time.sleep(1)
        
        motor_b_backward(pwm_b, 30)
        time.sleep(2)
        motor_b_stop(pwm_b)
        time.sleep(1)
        
        # Test both motors together
        print("\n=== Testing Both Motors ===")
        print("Both forward...")
        motor_a_forward(pwm_a, 40)
        motor_b_forward(pwm_b, 40)
        time.sleep(2)
        
        print("Both backward...")
        motor_a_backward(pwm_a, 40)
        motor_b_backward(pwm_b, 40)
        time.sleep(2)
        
        print("Turning left (Motor A back, Motor B forward)...")
        motor_a_backward(pwm_a, 40)
        motor_b_forward(pwm_b, 40)
        time.sleep(2)
        
        print("Turning right (Motor A forward, Motor B back)...")
        motor_a_forward(pwm_a, 40)
        motor_b_backward(pwm_b, 40)
        time.sleep(2)
        
        stop_all_motors(pwm_a, pwm_b)
        print("\n✅ Test Complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
    finally:
        cleanup(pwm_a, pwm_b)

def interactive_mode():
    """Interactive motor control"""
    print("\n" + "="*50)
    print("TB6612FNG Motor Test - Interactive Mode")
    print("="*50)
    print("\nCommands:")
    print("  Motor A: af (forward), ab (backward), as (stop)")
    print("  Motor B: bf (forward), bb (backward), bs (stop)")
    print("  Both: stop (stop all), q (quit)")
    print("="*50)
    
    pwm_a = None
    pwm_b = None
    
    try:
        pwm_a, pwm_b = setup_gpio()
        
        while True:
            cmd = input("\nEnter command: ").lower().strip()
            
            if cmd == 'q':
                break
            elif cmd == 'af':
                motor_a_forward(pwm_a, 50)
            elif cmd == 'ab':
                motor_a_backward(pwm_a, 50)
            elif cmd == 'as':
                motor_a_stop(pwm_a)
            elif cmd == 'bf':
                motor_b_forward(pwm_b, 50)
            elif cmd == 'bb':
                motor_b_backward(pwm_b, 50)
            elif cmd == 'bs':
                motor_b_stop(pwm_b)
            elif cmd == 'stop':
                stop_all_motors(pwm_a, pwm_b)
            else:
                print("Unknown command! Use: af, ab, as, bf, bb, bs, stop, q")
                
    except KeyboardInterrupt:
        print("\n⚠️  Exiting interactive mode")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        cleanup(pwm_a, pwm_b)

def diagnostic_mode():
    """Run diagnostic checks without motor control"""
    print("\n" + "="*50)
    print("TB6612FNG Diagnostic Mode")
    print("="*50)
    
    print("\n1. System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {sys.version}")
    print(f"   User: {os.environ.get('USER', 'unknown')}")
    print(f"   Is root: {os.geteuid() == 0}")
    
    print("\n2. GPIO Library:")
    if GPIO:
        print(f"   Module: {GPIO.__name__}")
        if hasattr(GPIO, 'VERSION'):
            print(f"   Version: {GPIO.VERSION}")
        print(f"   Is Raspberry Pi: {IS_RASPBERRY_PI}")
    else:
        print("   ERROR: GPIO module not loaded")
    
    if IS_RASPBERRY_PI:
        print("\n3. Checking /proc/cpuinfo:")
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'Hardware' in line or 'Revision' in line:
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
        
        print("\n5. Testing basic GPIO setup (no motors):")
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(STBY, GPIO.OUT)
            GPIO.output(STBY, GPIO.LOW)
            print("   ✅ Basic GPIO control works")
            GPIO.cleanup()
        except Exception as e:
            print(f"   ❌ GPIO control failed: {e}")

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