# MicroPython Basic Components

This library implements classes to simplify use of various frequently used components such as LED, RGB LED, Button, Temperature sensor. To use this library save it onto your microcontroller board and then import it in code normally.

# Documentation
In every class on init you have to specify the pin number **(int)** (or multiple pin numbers) to which the component is connected on the microcontroller.

## LED
#### ```Led(pin_id, pwm=False, pwm_freq=1000)```
```pwm``` - if Pulse Width Modulation is enabled (enables brightness control.)

#### ```Led.on(brightness=1.0)```
Turn the led on and optionally specify the brightness **(0 - 1 inclusive)** (PWM must be enabled.)

#### ```Led.off()```
Turn the led off.

#### ```Led.enable_pwm(pwm_freq=1000)```
Enable pulse width modulation and optionally specify the frequency.

#### ```Led.disable_pwm()```
Disable pulse width modulation.

#### ```async Led.blink(duration, brightness=1.0):```
Turn the led on for a specified amount of miliseconds **(ms)** and turn it off after the time had passed.

#### ```Led.fade_in(duration, brightness=1.0, interval=10):```
Fade the led from turned off to specified brightness over specified amount of miliseconds **(ms)**.  
```interval``` specifies how many miliseconds to wait between each brightness change.

#### ```Led.fade_out(duration, interval=10):```
Fade the led to turned off over specified amount of miliseconds **(ms)**.  
```interval``` specifies how many miliseconds to wait between each brightness change.

#### ```async Led.fade_blink(fade_in, hold, fade_out, brightness=1.0, interval=10):```
Combines the function of ```fade_in``` + ```blink``` + ```fade_out```.   
```hold``` specifies how many miliseconds to keep the led turned on.
<br>

## RGB LED
#### ```RgbLed(pin_r, pin_g, pin_b, freq=1000)```
```freq``` specifies pwm frequency

#### ```RgbLed.on()```
Turn all led colors on to full brightness (white color.)

#### ```RgbLed.off()```
Turn the led off.

#### ```RgbLed.set_color_rgb(r, g, b):```
Turn the colored leds on with specified brightness **(0 - 255 inclusive)**. This creates the rgb color

#### ```RgbLed.set_color(color: str):```
Turn the led on with a specified color in the format of hex color string (e.g. #FFFFFF)

#### ```RgbLed.set_color_hsv(h, s, v):```
Turn the led on with a specified color in HSV color format **(0 - 1 inclusive)**.
<br>

## Button
#### ```Button(pin_id, debounce=50)```
```debounce``` specifies time in ms after change in state during which the button ignores any other changes in state (this filters out noise.)

#### ```Button.on_click(*listeners)```
Add listener functions to be called when the button is pressed.

#### ```Button.on_click_async(*listeners)```
Add async listener functions to be called when the button is pressed. Use only with asyncio event loop running!

#### ```Button.is_pressed()```
Returns True if the button is pressed, False if not.
<br>

## Temperature Sensor
#### ```TemperatureSensor(pin_id)```

#### ```TemperatureSensor.get_temperature()```
Returns current temperature in **°C**, there is a lot of noise and variability.

#### ```TemperatureSensor.get_temperature_fahrenheit()```
Returns current temperature in **°F**, there is a lot of noise and variability.

#### ```TemperatureSensor.start_measuring(interval=1.0, mean_count=15)```
Start measuring loop for ```get_stable_temperature``` functions. These functions work by storing last ```mean_count``` temperatures and returning their arithmetic mean.
```interval``` specifies how often should the sensor read the temperature.  
```mean_count``` specifies how many readings should be stored.

#### ```TemperatureSensor.stop_measuring()```
Stop measuring loop for ```get_stable_temperature``` functions.

#### ```TemperatureSensor.get_stable_temperature()```
Returns current temperature in **°C**, without noise. Start measuring loop with ```Sensor.start_measuring``` before using this function.

#### ```TemperatureSensor.get_stable_temperature_fahrenheit()```
Returns current temperature in **°F**, without noise. Start measuring loop with ```Sensor.start_measuring``` before using this function.

#### ```TemperatureSensor.convert_to_fahrenheit(temp)```
Convert temperature in °C to °F.
