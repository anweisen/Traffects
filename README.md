# Traffects
The api &amp; control code of my traffic light effect system

## Stats Tracker

This program comes with a simple stats tracking system, which uses a txt file to save them.
They are updated every 100ms and the changes can be viewed using an editor like visual studio code in real time.

The structure of the tracker.txt file is a simple row of numbers with the following meanings:
- amount of updates for the green light (on or off)
- amount of updates for the yellow light (on or off)
- amount of updates for the red light (on or off)
- amount of bytes sent to the arduino using the serial connection
- amount of seconds the program was running