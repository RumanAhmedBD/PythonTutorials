from RPLCD.i2c import CharLCD
from time import sleep

# Correct configuration for a 20x4 LCD
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=20,
    rows=4,
    dotsize=8,
    charmap='A02',
    auto_linebreaks=True
)

lcd.clear()

# Write on all 4 lines
lcd.write_string('Line 1: Hello World!')
#lcd.cursor_pos = (1, 0)
lcd.write_string('Line 2: LCD Ready')
#lcd.cursor_pos = (2, 0)
lcd.write_string('Line 3: Raspberry Pi')
#lcd.cursor_pos = (3, 0)
lcd.write_string('Line 4: I2C OK')
