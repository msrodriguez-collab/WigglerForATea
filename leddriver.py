

def colorduty(hex):
    '''
    Decodes a hexadecimal color code into red, green and blue brightness.
    Then, uses gamma correction to return the corresponding PWM for these brightnesses.
    hexadecimal formatting: 0xRRGGBB
    '''
    
    redvalue = (hex >> 16) & 0xFF
    greenvalue = (hex >> 8) & 0xFF
    bluevalue = hex & 0xFF
    #converting to PWM using gamma correction
    red = int((redvalue / 255) ** 2.8 * 100)
    green = int((greenvalue / 255) ** 2.8 * 100)
    blue = int((bluevalue / 255) ** 2.8 * 100)
    return red, green, blue

#testing PWM for max all colors


    