#!/usr/bin/env python3

import asyncio
import os
import ssl
import threading
import signal
import json
from logging import getLogger, basicConfig, INFO
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.log import app_log
from websocket import create_connection
import glob

from ffmpeg import load_audio


basicConfig(
    format='%(asctime)s000 - %(levelname)-4s - %(process)-5d - %(name)s - %(message)s',
    level=INFO
)
clients = set()
audio_count = 0
face_detect_audios_path = os.environ.get('FACE_DETECT_AUDIOS_PATH')
no_face_detect_audios_path = os.environ.get('NO_FACE_DETECT_AUDIOS_PATH')
# フォルダ内のファイル名をすべて取得
face_detect_audio = glob.glob(face_detect_audios_path + "*.mp3")
no_face_detect_audio = glob.glob(no_face_detect_audios_path + "*.mp3")
# app_log.info("face_detect_audio: {}".format(face_detect_audio))
# app_log.info("no_face_detect_audio: {}".format(no_face_detect_audio))

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, x-requested-with, Content-Type, Accept")
        self.set_header('Access-Control-Allow-Methods',
                        'PUT, DELETE, POST, GET, OPTIONS')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()



class AudioStreamer:
    def __init__(self, tornado_websocket_handler):
        self.ws = tornado_websocket_handler

    async def process(self, message):
        file_path = message

        app_log.info("[AudioStreamer] start streaming: {}".format(file_path))

        for chunk in load_audio(file_path):
            try:
                await self.ws.write_message(chunk, binary=True)
            except Exception:
                app_log.info("[AudioStreamer] failed to stream: {}".format(file_path))
                self.ws.close()
                return

        app_log.info("[AudioStreamer] complete streaming: {}".format(file_path))



class WebSocketRandomKeepListeningHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_streamer = AudioStreamer(tornado_websocket_handler=self)

    def check_origin(self, origin):
        return True

    def open(self):
        app_log.info("[WebSocketRandomKeepListeningHandler] WebSocket opened")

    def on_message(self, message):
        app_log.info(
            f"[WebSocketRandomKeepListeningHandler] receive message: {message}")
        message = message.split("_")

        # clientの登録と削除
        if message[0] == "start":
            if self not in clients:
                app_log.info(
                    f"[WebSocketRandomKeepListeningHandler] add client: {message[2]}")
                clients.add(self)
        elif message[0] == "close":
            app_log.info(
                    f"[WebSocketRandomKeepListeningHandler] close client: {message[2]}")
            self.close()

    def on_close(self):
        app_log.info("[WebSocketRandomKeepListeningHandler] WebSocket closed")
        if self in clients:
            app_log.info("[WebSocketRandomKeepListeningHandler] delete client")
            clients.remove(self)



class StreamingAudioHookHandler(BaseHandler):
    async def get(self, parsed_url):
        global audio_count
        if parsed_url == "face":
            audio_type = face_detect_audio[audio_count % len(face_detect_audio)]
        elif parsed_url == "noface":
            audio_type = no_face_detect_audio[audio_count % len(no_face_detect_audio)]
        else:   # error
            self.set_status(404)
            self.write("Not Found")
            self.flush()
            return

        app_log.info("[StreamingAudioHookHandler] current audio_type: {}".format(audio_type))
        audio_count = audio_count + 1
        # app_log.info("[StreamingAudioHookHandler] audio_count: {}".format(audio_count))

        futures = map(lambda client: client.audio_streamer.process(audio_type), clients)
        await asyncio.gather(*futures)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(audio_type, ensure_ascii=False))
        self.flush()



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/audio_hook/([^/]+)", StreamingAudioHookHandler),
            (r"/websocket_random_keep_listening", WebSocketRandomKeepListeningHandler),
        ]
        super().__init__(handlers)


def signal_handler(signum, frame):
    app_log.info("Interrupt caught")
    tornado.ioloop.IOLoop.instance().stop()


def main():

    app = Application()

    app.listen(8889)
    tornado.ioloop.IOLoop.instance().start()

    # or you can use a custom handler,
    # in which case recv will fail with EINTR
    app_log.info("registering sigint")
    signal.signal(signal.SIGINT, signal_handler)



if __name__ == "__main__":
    main()
