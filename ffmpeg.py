#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

# 8192 サンプル * 2 バイト * 2 チャンネル (ステレオ)
BUFFER_SIZE = 8192 * 2 * 2


def load_audio(audio_file):
    proc = subprocess.Popen([
        'ffmpeg',
        '-i', audio_file,
        '-vn', '-c:a', 'pcm_s16le', '-r:a', '44100', '-ac', '2',
        '-f', 's16le', '-',
    ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while True:
        buf = proc.stdout.read(BUFFER_SIZE)
        if buf == b'':
            break
        yield buf

    # 念の為
    proc.kill()
