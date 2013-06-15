EasyDojo
========

Simple tools developed to help in Coding Dojo sessions

Install and use
---------------

Install ::

    pip install -e git://github.com/fabiocerqueira/easydojo.git#egg=easydojo

Use ::

    $ easy_dojo --help
    Easy Dojo

    Simple tool to help in Coding Dojo sessions

    Usage:
        easy_dojo init <name>
        easy_dojo watch [--handlers=<handlers>] [<args>...]
        easy_dojo panel [<port>]
        easy_dojo list
        easy_dojo (-h | --help)
        easy_dojo --version

    Options:
        --handlers=<handlers>     Handlers used on watch command(separated by commas)
        port    Port used on tornado server of EasyDojo Panel(default=2020)
        -h --help     Show this screen.
        --version     Show version.

Handlers
--------

::

    $ easy_dojo list
    List of all handlers:
        * Arduino -  Send a serial command to arduino with tests results 
        
        * MacNotify -  Displays tests results on console and a Mac Desktop notification 
        
        * WebSocket -  Send tests results via WebSocket.
                    args:
                        <url> - url to websocket server
                    example: easy_dojo watch --handler=WebSocket ws://localhost:2020/ws
            
        
        * Socket -  Send a network command via socket with tests results.
                    args:
                        <host> - host of server
                        <port> - port used on server
                    example: easy_dojo watch --handler=Socket localhost 2020

Contributing
------------

Your contributions are welcome! ::

Get the code ::

    git clone git://github.com/fabiocerqueira/easydojo.git

Install dependencies ::

    pip install -r requirements.txt

Run tests ::

    make test

