This project consists of a D-Bus API to [Phidgets](http://www.phidgets.com/) devices. 

API
===

Signals
-------

Signals are emitted through the interface "com.phidgets.Phidgets".

- Path: /Device
  - Member: Attached
    - sig: "a{sv}"  (see ...)
    
- Path: /Device
  - Member: Detached
    - sig: "a{sv}"  (see ...)

- Path: /Device
  - Member: Error
    - sig: "a{sv}"  (see ...)

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
