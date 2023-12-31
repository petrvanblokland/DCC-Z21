# DCC-Z21

This repository contains Python sources for connecting to DCC-Z21 equipment such as DR5000 control centers, SwitchPilot-Servo and LokSound5 decoders;
The sources describe Python classes for typilcal objects and protocols. By importing the classes in environments that run Python (such as scripting from MacOS terminal, DrawBot.com and webbrowsers) it is possible to define model train layouts and operation schedules entirely by code. No other 3rd-party applications are necessary.

All is very much in development, so for now classes, methods and file architecture can still be alteret without notice.

[z21.py] <--- (LAN) ---> [DR5000]  <--- (2-wire rails) ---> [LokSound5]

This is an initial project start. More outlines for future development will be posted soon.

The development is done on MacOS, but since most Python code will only use standard labraries, it should not be a problem to run on Windows or Linux.

For questions, additional info and contributions, contact tptr@petr.com

## Sources

* **z21.py** Contains the main classes and global helper functions
* **testController.py** Test the basic controller functions, such a track power on/off and overall settings.
* **TrainTheTrain** contains the ongoing results of a test, to see what would be needed to write an application for (partly) replacing Koploper. If successful this may become a separate repository.


## Interesting references

### Z21

* (z21-lan-protokoll-en.pdf) https://www.z21.eu/en/downloads/manuals
* (Search for "Z21 protocol") https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjxspnA26CCAxUByaQKHerhDIYQFnoECBkQAQ&url=https%3A%2F%2Fwww.z21.eu%2Fmedia%2FKwc_Basic_DownloadTag_Component%2Froot-en-main_47-1652-959-downloadTag-download%2Fdefault%2Fd559b9cf%2F1693227100%2Fz21-lan-protokoll-en.pdf&usg=AOvVaw1cieQ0kRk9t1ShfXgtry4k&opi=89978449
* https://www.z21.eu/en/z21-system/general-information
* https://github.com/grizeldi/z21-drive

## Connecting BRAWA Test track “Der BRAWA Rollenprüfstand”

* https://www.stummiforum.de/t79402f2-Der-BRAWA-Rollenpr-fstand.html#msg837779

### General links

* (Inspired by) https://gitlab.com/z21-fpm/z21_python
* http://www.francescpinyol.cat/dcc.html#z21_python

## History 

* 2023-10-27 Tested on DR5000 via LAN with LokSound5
