This project consists of a D-Bus API to [Phidgets](http://www.phidgets.com/) devices. 

Applications
------------

- "phidgets-manager" : publishes the signals "Attached", "Detached", "Error" and "Devices" on path "/Device"

- "phidgets-ifk" : publishes the signals "Din", "Dout", "Ain" and "Error" on path "/Device"

The latter ("phidgets-ifk") requires "phidgets-manager" to be running: it subscribes to the "Devices"
signal in order to be notified of new "InterfaceKit" devices to service.

Signals
-------

Signals are emitted through the interface "com.phidgets.Phidgets".

- Path: /Device
  - Member: Attached
    - sig: "a{sv}"
    
- Path: /Device
  - Member: Detached
    - sig: "a{sv}"

- Path: /Device
  - Member: Error
    - sig: "a{sv}"

- Path: /Device
  - Member: Devices  ## discovered devices, repeating interval
    - sig: "aa{sv}"

- Path: /Device
  - Member: Din  (Digital Input Changed event)
    - sig: "sii" (serial, pin#, value)
     
- Path: /Device
  - Member: Dout  (Digital Output Changed event)
    - sig: "sii" (serial, pin#, value)

- Path: /Device
  - Member: AIN  (Analog Input Changed event)
    - sig: "sii" (serial, pin#, value)



Installation
============
There are 2 methods:

1. Use the Ubuntu Debian repository [jldupont](https://launchpad.net/~jldupont/+archive/phidgets)  with the package "rbsynclastfm"

2. Use the "Download Source" function of this git repo and use "sudo make install"

Dependencies
============

* DBus python bindings
* Phidgets Library (available in the PPA)
* Python Phidgets Library (available in the PPA)
