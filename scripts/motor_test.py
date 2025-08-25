#!/usr/bin/env python3
"""
TB6612FNG Motor Driver Test Script
Tests both motors with forward/backward/stop commands
Cross-platform compatible (Mac development, Raspberry Pi deployment)
"""

import time
import sys
import platform

# Platform detection and GPIO import handling
if platform.system() == 'Linux' and 'arm' in platform.machine():
    # Running on Raspberry Pi
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
else:
    # Running on development machine (Mac/Windows/Linux x86)
    try:
        from fake_rpi.RPi import GPIO
        IS_RASPBERRY_PI = False
        print("Running in development mode with fake-rpi")
    except ImportError:
        print("Error: fake-rpi not installed. Run: pip install fake-rpi")
        sys.exit(1)

# Pin definitions - Using hardware PWM capable pins on Pi
# Motor A pins
AIN1 = 24   # General purpose GPIO
AIN2 = 23   # General purpose GPIO
PWMA = 12   # Hardware PWM pin

# Motor B pins  
BIN1 = 22   # General purpose GPIO
BIN2 = 27   # General purpose GPIO
PWMB = 13   # Hardware PWM pin

# Control pin
STBY = 16   # General purpose GPIO

def setup_gpio():
    """Initialize GPIO pins"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Set all pins as outputs
        GPIO.setup([AIN1, AIN2, PWMA, BIN1, BIN2, PWMB, STBY], GPIO.OUT)
        
        # Set up PWM for speed control (1000Hz frequency)
        pwm_a = GPIO.PWM(PWMA, 1000)
        pwm_b = GPIO.PWM(PWMB, 1000)
        
        # Start PWM with 0% duty cycle
        pwm_a.start(0)
        pwm_b.start(0)
        
        # Enable the motor driver
        GPIO.output(STBY, GPIO.HIGH)
        print("Motor driver enabled!")
        
        if not IS_RASPBERRY_PI:
            print("WARNING: Running in simulation mode - no actual GPIO control")
        
        return pwm_a, pwm_b
    except Exception as e:
        print(f"Error during GPIO setup: {e}")
        if IS_RASPBERRY_PI:
            print("Check if script is run with sudo: sudo python3 motor_test_improved.py")
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
    motor_a_stop(pwm_a)
    motor_b_stop(pwm_b)

def cleanup(pwm_a, pwm_b):
    """Clean up GPIO and PWM"""
    try:
        stop_all_motors(pwm_a, pwm_b)
        pwm_a.stop()
        pwm_b.stop()
        GPIO.output(STBY, GPIO.LOW)  # Disable motor driver
        GPIO.cleanup()
        print("GPIO cleanup complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def run_motor_test():
    """Run a comprehensive motor test"""
    print("Starting TB6612FNG Motor Test...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Running on Raspberry Pi: {IS_RASPBERRY_PI}")
    print("\nPin Configuration:")
    print(f"Motor A: AIN1={AIN1}, AIN2={AIN2}, PWMA={PWMA}")
    print(f"Motor B: BIN1={BIN1}, BIN2={BIN2}, PWMB={PWMB}")
    print(f"STBY={STBY}")
    print("\nMake sure STBY is connected and VM is connected to power supply!")
    
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
        print("\n=== Test Complete ===")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        cleanup(pwm_a, pwm_b)

def interactive_mode():
    """Interactive motor control"""
    print("Starting Interactive Mode...")
    print("\nCommands:")
    print("  Motor A: af (forward), ab (backward), as (stop)")
    print("  Motor B: bf (forward), bb (backward), bs (stop)")
    print("  Both: stop (stop all), q (quit)")
    
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
        print("\nExiting interactive mode")
    finally:
        cleanup(pwm_a, pwm_b)

if __name__ == "__main__":
    print("TB6612FNG Motor Test Script")
    print("1. Run automated test")
    print("2. Interactive mode")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        run_motor_test()
    elif choice == "2":
        interactive_mode()
    else:
        print("Invalid choice!")