#!/usr/bin/python

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options

import time
import multiprocessing
import serialProcess

define("port", default=8887, help="run on the given port", type=int)

clients = []

# uncomment to serve static html pages from the Yun
# also uncomment line 58
#class IndexHandler(tornado.web.RequestHandler):
#   def get(self):
#       self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        clients.append(self)
        # elable multiclient mode for BreakoutJS
        #self.write_message("config: multiClient")

    def on_message(self, message):
        #print 'tornado received from client: %s' % message
        data = ""
        q = self.application.settings.get('queue')
        # assemble a string of chars to send to the arduino
        for msg in message.split(","):
            data += chr(int(msg))
        q.put(data)

    def on_close(self):
        print 'connection closed'
        clients.remove(self)

############################# MAIN ##############################

def main():

    taskQ = multiprocessing.Queue()
    resultQ = multiprocessing.Queue()

    sp = serialProcess.SerialProcess(taskQ, resultQ)
    sp.daemon = True
    sp.start()

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [
            #(r"/", IndexHandler),
            (r"/websocket", WebSocketHandler)
        ], queue = taskQ
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print "Listening on port: ", options.port

    def checkResults():
        if not resultQ.empty():
            result = resultQ.get()
            #print "tornado received from arduino: " + result
            for c in clients:
                c.write_message(result)

    mainLoop = tornado.ioloop.IOLoop.instance()
    scheduler = tornado.ioloop.PeriodicCallback(checkResults, 10, io_loop = mainLoop)
    scheduler.start()
    mainLoop.start()

if __name__ == "__main__":
    main()
