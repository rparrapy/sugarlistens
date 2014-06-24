Sugar Listens
============

Speech recognition for the Sugar Learning Platform.

##What is this about?
*Sugar Listens* is a GSoC 2014 project that seeks to provide speech recognition capabilities to Sugar Activity developers.
For more information, please refer to the project [proposal](https://wiki.sugarlabs.org/go/Summer_of_Code/2014/Sugar_Listens).


##Setup and Run
1. Clone this repository: 

  ```
  git clone https://github.com/rparrapy/sugarlistens.git
  ```
  
2. Install the module with setuptools:

 ```
 cd sugarlistens
 python setup.py develop
 
 ```
 
3. Sugar Listens uses D-Bus' system bus to communicate with Sugar Activities.
For this to work, you must enable it by adding a few lines to the existing policy element of **/etc/dbus-1/system.conf**:

 ```
 <policy context="default">
    ...
    <!-- This lines are needed for Sugar Listens to work -->
    <allow own="org.sugarlabs.listens.recognizer"/>
    <allow send_destination="org.sugarlabs.listens.recognizer"/>
    <allow receive_sender="org.sugarlabs.listens.recognizer"/>
 <policy context="default">
 ```
 
4. Run Sugar Listens in a terminal window:

 ```
 python sugarlistens/sugarlistens/recognizer.py
 ```
 
5. Test it by running one of the following projects:
 * [Livedemo](https://github.com/rparrapy/sugarlistens-livedemo): it doesn't get much simpler than this.
 * [Maze](https://github.com/rparrapy/maze): ready to play a game?
 * [Sugar](https://github.com/rparrapy/sugar): try running your favorite Sugar Activities with your voice. Pretty cool, huh?



##Thanks
Current implementation is based on the [Pocketsphinx](http://cmusphinx.sourceforge.net/) speech recognition engine, so thanks to the guys at CMU that made this possible.
