from machine import ADC, Pin, PWM
from math import log
import asyncio
import time


class Led():
    def __init__(self, pin_id, pwm=False, pwm_freq=1000):
        self.led = Pin(pin_id, Pin.OUT)
        self.pwm_enabled = pwm
        self.brightness = 0.0

        if self.pwm_enabled:
            self.enable_pwm(pwm_freq)

    def on(self, brightness=1.0):
        if self.pwm_enabled:
            if brightness < 0 or brightness > 1:
                raise Exception("Brightness can only be from range 0.0 - 1.0 inclusive.")

            self.brightness = brightness
            self.pwm.duty_u16(int(65535 * brightness))
        else:
            if brightness == 1:
                self.brightness = 1.0
                self.led.on()
            else:
                raise Exception("Enable PWM for brightness control.")

    def off(self):
        self.brightness = 0.0
        if self.pwm_enabled:
            self.pwm.duty_u16(0)
        else:
            self.led.off()

    def enable_pwm(self, pwm_freq=1000):
        self.pwm_enabled = True
        self.pwm = PWM(self.led, freq=pwm_freq)
        self.on(self.brightness)
    
    def disable_pwm(self):
        self.pwm_enabled = False
        self.pwm.deinit()
        self.led.init(self.led.OUT)
        self.off()

    async def blink(self, duration, brightness=1.0):
        self.on(brightness)
        await asyncio.sleep_ms(duration)
        self.off()
    
    async def fade_in(self, duration, brightness=1.0, interval=10):
        duration = duration // interval
        for i in range(duration):
            self.on((brightness / duration) * i)
            await asyncio.sleep_ms(interval)
        self.on(brightness)
    
    async def fade_out(self, duration, interval=10):
        start_brightness = self.brightness
        duration = duration // interval
        for i in reversed(range(duration)):
            self.on((start_brightness / duration) * i)
            await asyncio.sleep_ms(interval)
        self.off()
    
    async def fade_blink(self, fade_in, hold, fade_out, brightness=1.0, interval=10):
        await self.fade_in(fade_in, brightness=brightness, interval=interval)
        await asyncio.sleep_ms(hold)
        await self.fade_out(fade_out, interval=interval)


class RgbLed():
    def __init__(self, pin_r, pin_g, pin_b, freq=1000):
        self.red = Pin(pin_r, Pin.OUT)
        self.green = Pin(pin_g, Pin.OUT)
        self.blue = Pin(pin_b, Pin.OUT)

        self.red_pwm = PWM(self.red, freq=freq)
        self.green_pwm = PWM(self.green, freq=freq)
        self.blue_pwm = PWM(self.blue, freq=freq)
    
    def on(self):
        self.set_color_rgb(255, 255, 255)
    
    def off(self):
        self.set_color_rgb(0, 0, 0)
    
    def _parse_hex_str(self, string):
        string = string[1:]
        if len(string) != 6:
            raise Exception("Not a valid hex string.")
        
        r = int(string[0] + string[1], 16)
        g = int(string[2] + string[3], 16)
        b = int(string[4] + string[5], 16)

        return r, g, b

    def set_color_rgb(self, r, g, b):
        for led, value in [(self.red_pwm, r), (self.green_pwm, g), (self.blue_pwm, b)]:
            led.duty_u16(int((65535 / 255) * value))

    def set_color(self, color: str):
        self.set_color_rgb(*self._parse_hex_str(color))

    def set_color_hsv(self, h, s, v):
        def hsv_to_rgb(h, s, v):
            """--- GPT CODE ---"""
            """Convert HSV (0-1 range) to RGB (0-255 range)."""
            i = int(h * 6)
            f = (h * 6) - i
            p = int(255 * v * (1 - s))
            q = int(255 * v * (1 - f * s))
            t = int(255 * v * (1 - (1 - f) * s))
            v = int(255 * v)
            i = i % 6

            if i == 0:
                return (v, t, p)
            elif i == 1:
                return (q, v, p)
            elif i == 2:
                return (p, v, t)
            elif i == 3:
                return (p, q, v)
            elif i == 4:
                return (t, p, v)
            else:
                return (v, p, q)
        
        self.set_color_rgb(*hsv_to_rgb(h, s, v))


class Button():
    def __init__(self, pin_id, debounce=50):
        self.button = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.debounce = debounce

        self.click_listeners = []
        self.click_listeners_async = []
        self.presses = 0

        self._toggled = False
        self._last_pressed = time.ticks_ms()
        self.button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_press_handler)

    def _button_press_handler(self, pin=None):
        if not self.is_pressed():
            self._last_pressed = time.ticks_ms()
            self._toggled = False

        if not self._toggled and self.is_pressed() and time.ticks_diff(time.ticks_ms(), self._last_pressed) >= self.debounce:
            self._last_pressed = time.ticks_ms()
            self._toggled = True
            self._click_fire()

                    
    def _click_fire(self):
        for listener in self.click_listeners:
            listener()

        for listener in self.click_listeners_async:
            asyncio.create_task(listener())
        

    def on_click(self, *listeners):
        for listener in listeners:
            self.click_listeners.append(listener)
    
    def on_release(self, *listeners):
        # TODO
        pass

    # USE ONLY WITH EVENT LOOP
    def on_click_async(self, *listeners):
        for listener in listeners:
            self.click_listeners_async.append(listener)

    def is_pressed(self):
        return self.button.value() == 0
    

# TODO ON_CHANGE
class TemperatureSensor():
    def __init__(self, pin_id):
        self.sensor = ADC(pin_id)

        self.measuring = False
        self.temp_values = []
        self.stable_temp = self.get_temperature()

    def get_temperature(self):
        adc_value = self.sensor.read_u16()
        adc_converted = (65535 - adc_value)
        res = 10000 * ((65536 / adc_converted) - 1)
        temp = 1 / (0.001129148 + (0.000234125 * log(res)) + (0.0000000876741 * log(res)**3))
        temp = temp - 273.15
        return temp
    
    def get_temperature_fahrenheit(self):
        return self.convert_to_fahrenheit(self.get_temperature())
    
    def get_stable_temperature_fahrenheit(self, digits=1):
        return self.convert_to_fahrenheit(self.get_stable_temperature(digits))
    
    def get_stable_temperature(self, digits=1):
        if not self.measuring:
            raise Exception("Start measuring loop before reading stable temperature.")
        return round(self.stable_temp, digits)
    
    def start_measuring(self, interval=1.0, mean_count=15):
        self.mean_count = mean_count
        self.interval = interval

        self.measuring = True

        asyncio.create_task(self._measure_loop())

    def stop_measuring(self):
        self.measuring = False

    def convert_to_fahrenheit(self, temp):
        return temp * (9 / 5) + 32
    
    async def _measure_loop(self):
        while self.measuring:
            self.temp_values.append(self.get_temperature())
            if len(self.temp_values) > self.mean_count:
                self.temp_values.pop(0)
            
            sum = 0
            for temp in self.temp_values:
                sum += temp
            
            self.stable_temp = sum / len(self.temp_values)
            await asyncio.sleep(self.interval)