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
countdown_time = 300
countdown_code = 300
countdown_state = 'resume'
ws_clients = []
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
FORMAT = "[%(asctime)-15s] - %(message)s"
logging.basicConfig(format=FORMAT)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        logging.info('[ws] connected: {0}'.format(self.request.remote_ip))
        ws_clients.append(self)

    def on_message(self, message):
        global countdown_state
        global countdown_code
        global countdown_time
        logging.info('[ws] message received: {0}'.format(message))
        if message == 'resume_pause':
            if countdown_state == 'resume':
                countdown_state = 'pause'
            elif countdown_state == 'pause':
                countdown_state = 'resume'
            self.broadcast(countdown_state)
        elif message == 'restart':
            countdown_code = countdown_time
        else:
            self.broadcast(message)

    def broadcast(self, message):
        global ws_clients
        for socket in ws_clients:
            socket.write_message(message)

    def on_close(self):
        logging.info('[ws] disconnected: {0}'.format(self.request.remote_ip))
        ws_clients.remove(self)


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


def countdown():
    global countdown_code
    global countdown_time
    global ws_clients
    ioloop = tornado.ioloop.IOLoop.current()
    if countdown_state == 'resume':
        if ws_clients:
            str_time = time.strftime('%M:%S', time.gmtime(countdown_code))
            for s in ws_clients:
                s.write_message(str_time)
        if countdown_code:
            countdown_code -= 1
        else:
            countdown_code = countdown_time
    ioloop.add_timeout(time.time() + 1, countdown)


def main(port=2020, code_time=300):
    global server
    global countdown_time
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    logging.info('Server runnig on port %d' % port)
    logging.info('WebSocket: ws://localhost:%d/ws' % port)
    countdown_time = code_time
    countdown()
    tornado.ioloop.IOLoop.instance().start()
    logging.info("Exit...")


if __name__ == "__main__":
    main()
