

def locate(user_string="PS3 Controller", x=0, y=0):
    """ Place the text at a certain location """
    # Don't allow any user errors. Python's own error detection will check for
    # syntax and concatination, etc, etc, errors.
    x = int(x)
    y = int(y)
    if x >= 80:
        x = 80
    if y >= 40:
        y = 40
    if x <= 0:
        x = 0
    if y <= 0:
        y = 0
    HORIZ = str(x)
    VERT = str(y)
    # Plot the user_string at the starting at position HORIZ, VERT...
    print("\033["+VERT+";"+HORIZ+"f"+user_string)
