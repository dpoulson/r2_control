def steering(x, y, drive_mod):
    """ Combine Axis output to power differential drive motors """
    # convert to polar
    r = math.hypot(x, y)
    t = math.atan2(y, x)

    # rotate by 45 degrees
    t += math.pi / 4

    # back to cartesian
    left = r * math.cos(t)
    right = r * math.sin(t)

    # rescale the new coords
    left = left * math.sqrt(2)
    right = right * math.sqrt(2)

    # clamp to -1/+1
    left = (max(-1, min(left, 1)))*drive_mod
    right = (max(-1, min(right, 1)))*drive_mod

    if not args.dryrun:
        if _config.get('Drive', 'type') == "Sabertooth":
            drive.motor(0, left)
            drive.motor(1, right)
        elif _config.get('Drive', 'type') == "ODrive":
            drive.axis0.controller.input_vel = left*10
            drive.axis1.controller.input_vel = right*10
    if args.curses:
        # locate("                   ", 13, 11)
        # locate("                   ", 13, 12)
        locate('%10f' % left, 13, 11)
        locate('%10f' % right, 13, 12)

    return left, right