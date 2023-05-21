# sbusPythonDriver
a Python driver for the Taranis SBUS protocol

derivated from
- [Sokrates80/sbus_driver_micropython git hub](https://github.com/Sokrates80/sbus_driver_micropython)
- [https://os.mbed.com/users/Digixx/code/SBUS-Library_16channel/file/83e415034198/FutabaSBUS/FutabaSBUS.cpp/](os.mbed.com/users/Digixx/code/SBUS-Library_16channel)
- [https://os.mbed.com/users/Digixx/notebook/futaba-s-bus-controlled-by-mbed/](os.mbed.com/users/Digixx/notebook/futaba-s-bus-controlled-by-mbed/)
- [https://www.ordinoscope.net/index.php/Electronique/Protocoles/SBUS](ordinoscope.net/index.php/Electronique/Protocoles/SBUS)

This allow you to connect an FRsky receiver to your raspberry pi (or any UART compatible port) and decode values

It supports 16 standard Channels plus 2 digitals. (to be confirmed)

It has been tested only on the below FrSky receivers:
- X8R
- XM+

