import socket


def check():
    """ Tries to do a DNS lookup to see if we have an internet connection """
    try:
        host = socket.gethostbyname("www.google.com")
        socket.create_connection((host, 80), 2)
        internet_connection = True
    except Exception as e:
        internet_connection = False
    return internet_connection
