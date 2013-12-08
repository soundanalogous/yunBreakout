Arduino Yun Serial to WebSocket Bridge
---

This code is based largely on the following post: [http://niltoid.com/blog/raspberry-pi-arduino-tornado/](http://niltoid.com/blog/raspberry-pi-arduino-tornado/).
The following topics in the Arduino forum were also helpful:

- [WebSockes with Yun?](http://forum.arduino.cc/index.php?PHPSESSID=4pku83vo5og8qfscpebc21la53&topic=194934.msg1445071#msg1445071)
- [Tty for serial port to Arduino from Linino](http://forum.arduino.cc/index.php?PHPSESSID=3e1b76gh53llbkearekqvndtg3&topic=191820.15)


This bridge was designed to use BreakoutJS with an Arduino Yun without the use
of Breakout Server (since the server is running directly on the Yun). This code
could easily be adapted for your own purposes. It is not entirely specific to
BreakoutJS.

This is experimental code. Try it at your own risk. If you have ideas for
improvement, please start a discussion or open a pull request.

In order to use this bridge you'll first need to install a few things on your
Yun:

1. ssh into your Yun:

   On a mac:
   ```bash
   $ ssh root@YOUR-YUN-NAME.local
   ```

   Enter your password when prompted

2. Install dependencies:

    You'll need to install pyserial, pyopenssl, python-openssl. Enter the
    following 3 commands.

    ```bash
    $ opkg install python pyserial
    $ opkg install pyopenssl
    $ opkg install python-openssl
    ```


3. Install Tornado WebServer (this is used as the WebSocket server):

    Download the Tornado using curl and follow the commands below to build:
    ```bash
    $ curl -o /tmp/tornado 'https://pypi.python.org/packages/source/t/tornado/tornado-3.1.1.tar.gz' -k
    $ cd /tmp/
    $ tar xvzf tornado
    $ cd tornado-3.1.1
    $ python setup.py build
    $ python setup.py install
    ```

    I'm currently only using the server for WebSockets, but you can optionally
    host static web pages from the server as well. I have commented out that
    functionality. See comments in the code to enable.

4. Copy the contents of `linino/breakout/` to your Yun.

   This will copy the `breakout` directory to the home directory in your Yun's
   Linino linux installation. You can change the destination to copy them
   elsewhere. Google "scp" if you're not familiar with the use of secure copy.

    ```bash
   $ scp -r ./breakout root@YOUR-YUN-NAME.local:~/
   ```

   Enter your password when prompted


5. Compile and upload `arduino/StandardFirmataYun`


6. Disable Arduino bridge serial communication:

    Because this code essentialy hijacks Serial1 (which is what the Arduino
    Bridge library uses to communicate with linino) you'll need to prevent
    the linino bridge from accessing Serial1. The following steps will get
    that set up (but heed the warning!!!).

    Note that performing the following step is necessary to get Firmata to
    work with WebSockets on the Yun. However if you do this, *you will not be
    able to use the Arduino Bridge library until you undo this change*.

    It may be wise to make a backup before modifying this file. *Do not ever
    delete the inittab file or you may brick your Yun.*

    ```bash
    $ cd /etc/inittab
    $ vim inittab
    ```
    In the inittab file, comment out the line beginning with `ttyATH0`:
    `# ttyATH0::askfirst:/bin/ash --login`
    
    ```bash
    $ reboot -f
    ```

    At this point you'll need to close your session and log back in via ssh
    after a couple of minutes. If you have trouple ssh'ing into your Yun after
    this, see the troubleshooting section below.


7.  Run the script
    
    ```bash
    $ cd ~/breakout   # or whever you copied the files to
    $ python server.py
    ```

    In the near future this will launch automatically when your Yun boots, but
    I'm keeping it this way for now while it's alpha.


8.  Open one of files in `examples\getting_started\` in a text editor.

    You'll need to updeate the hostname (1st parameter passed to IOBoard constructor)
    to the name or IP address of your Yun.

    Serve the file from a local webserver. You should be able to interact with
    you're Yun. Note that at this time only a single client can reliably connect
    to a single Yun. If you uncomment line 29 of breakout/server.py you can
    establish a 2 client websocket connections to a single Yun. However any more
    than 2 greatly diminishes performance. I'm looking into the cause of this.


Troubleshooting
---

I've had difficulty establishing a ssh connection
from time to time. If you absolutely cannot connect again after editing
inittab, try this:

1. Load an example sketch that doesn't use Serial such as: Examples -> Basics -> BareMinimum
2. Power cycle the Yun and wait a couple of minutes for a full boot
3. ssh into the Yun (should work now)
4. Reupload StandardFirmataYun to the board

I know this is super annoying but it's the only thing I've found that works
(somewhat reliably) so far.


