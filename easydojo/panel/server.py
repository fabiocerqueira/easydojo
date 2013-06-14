import sys
import time
import os
import signal
import logging

from clint.textui import puts, colored

try:
    import tornado.httpserver
    import tornado.ioloop
    import tornado.web
    import tornado.options
    import tornado.websocket
except ImportError:
    puts(colored.red('Module tornado not found, use: pip install tornado'))
    sys.exit(1)

server = None
SOCKETS = []
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
FORMAT = "[%(asctime)-15s] - %(message)s"
logging.basicConfig(format=FORMAT)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        SOCKETS.append(self)

    def on_message(self, message):
        for socket in SOCKETS:
            if socket is not self:
                socket.write_message(message)

    def on_close(self):
        SOCKETS.remove(self)


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/ws', WSHandler),
], template_path=TEMPLATE_DIR, static_path=STATIC_DIR, debug=True)


def sig_handler(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    logging.info('Stopping http server')
    server.stop()
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.stop()
    logging.info('Shutdown')


def main(port=2020):
    global server
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logging.info('Server runnig on port %d' % port)
    logging.info('WebSocket: ws://localhost:%d/ws' % port)
    tornado.ioloop.IOLoop.instance().start()
    logging.info("Exit...")


if __name__ == "__main__":
    main()
