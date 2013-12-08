import serial
import time
import multiprocessing

class SerialProcess(multiprocessing.Process):

    def __init__(self, taskQ, resultQ):
        multiprocessing.Process.__init__(self)
        self.taskQ = taskQ
        self.resultQ = resultQ
        self.usbPort = '/dev/ttyATH0'
        self.sp = serial.Serial(self.usbPort, 115200, timeout=1)

    def close(self):
        self.sp.close()

    def run(self):

        self.sp.flushInput()

        while True:
            #look for incoming tornado request
            if not self.taskQ.empty():
                task = self.taskQ.get()

                # send it to the arduino
                dataOut = str(task)
                self.sp.write(dataOut)
                #print "arduino received from tornado: " + data

            #look for incoming serial data
            msg = ""
            if (self.sp.inWaiting() > 0):
                # assemble string of comma separated values to send to
                # client websocket
                while (self.sp.inWaiting() > 0):
                    dataIn = ord(self.sp.read())
                    msg += str(dataIn) + ","

                msg = msg[:-1] # chop off trailing comma
                #print msg
                self.resultQ.put(msg)
