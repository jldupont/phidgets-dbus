This project consists of a D-Bus API to [Phidgets](http://www.phidgets.com/) devices. 

Applications
------------

 - "phidgets-manager" : publishes the signals "Attached", "Detached", "Error" and "Devices" on path "/Device"

 - "phidgets-ifk" : publishes the signals "Din", "Dout", "Ain" and "Error" on path "/Device"

 - "phidgets-sensors" : publishes the signal "State" which reflects the current state of an input. 
  This application must be configured through "sensors.config" file located in "~/.phidgets-dbus" directory.
 
 - "phidgets-couchdb" : records event from "phidgets-ifk" to a local couchdb database


"phidgets-ifk" requires "phidgets-manager" to be running: it subscribes to the "Devices"
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


Signals emitted through the interface "org.sensors":

- Path: /State
  - Member: /State
    - sig: "ssv"  (device_id, sensor_name, sensor_state)


Sensors configuration
=====================

Example "sensors.config" file (YAML syntax):

<pre>
Devices:

 ## Device unique id i.e. serial
 80860:
  pins:
   3: porte_fournaise
   4: porte_escalier
   0: porte_garage_1
   1: porte_garage_2

States:
 porte_escalier:
  0: Open
  1: Closed
 porte_garage_1:
  0: Open
  1: Closed
 porte_garage_2:
  0: Open
  1: Closed
 porte_fournaise:
  0: Open
  1: Closed
</pre>

Installation
============
There are 2 methods:

1. Use the Ubuntu Debian repository [jldupont](https://launchpad.net/~jldupont/+archive/jldupont)  with the package "phidgets-dbus"

2. Use the "Download Source" function of this git repo and use "sudo make install"

Dependencies
============

* DBus python bindings
* Phidgets Library (available in the PPA)
* Python Phidgets Library (available in the PPA)

Python Phidgets module
======================

There is an issue with releases of Phidgets' Python module. Please see [this thread](http://phidgets.com/phorum/viewtopic.php?f=26&t=3485&p=13883) to help resolve it.

History
=======

 - v1.2: 
   - added check for Phidgets library (desktop notification popup if not found)
   - added 'phidgets-couchdb' application

 - v1.3:  just changed polling interval for IFK down to 1 second

