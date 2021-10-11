# random-voice-streaming-periodic  
random-voice-streaming-periodicは、ランダムに選択された音声データを定期的にストリーミングするマイクロサービスです。

## 概要  
random-voice-streaming-periodicは、HTTPリクエストが送られると、動作します。     
送信されたリクエストのエンドポイントごとに、別のフォルダからランダムに音声ファイル(.mp3)が1つ選択され、そのデータをストリーミングします。    
たとえば、  
-  `/audio_hook/face`というリクエストが送られた際は、`FACE_DETECT_AUDIOS_PATH`で設定したフォルダ内から、    
-  `/audio_hook/noface`というリクエストが送られた際は、`NO_FACE_DETECT_AUDIOS_PATH`で設定したフォルダ内から、   
ランダムにファイルを1つ選択して音声を再生します。   

## 動作環境
random-voice-streaming-periodicは、Kubernetes上での動作を前提としています。以下の環境が必要となります。        
* OS: Linux OS   
* CPU: ARM/AMD/Intel   
* Kubernetes/AION   

## セットアップ
1. このリポジトリをクローンする

```sh
$ git clone git@github.com:latonaio/random-voice-streaming-periodic.git
```

2. docker imageを作成する

```sh
$ cd /path/to/random-voice-streaming-periodic
$ make docker-build
```

## 起動方法
### 環境変数
`k8s/random-voice-streaming-periodic.yaml`内に記載する。   

|変数名    |値       |   
| --------|---------|   
|PORT     |8889     |   
|TZ       |Asia/Tokyo|   
|FACE_DETECT_AUDIOS_PATH|`/audio_hook/face`というリクエストが送られた際に再生する音声ファイルが入っているフォルダのパス|    
|NO_FACE_DETECT_AUDIOS_PATH|`/audio_hook/noface`というリクエストが送られた際に再生する音声ファイルが入っているフォルダのパス|   

`FACE_DETECT_AUDIOS_PATH`と`NO_FACE_DETECT_AUDIOS_PATH`の各フォルダがある1つ上の階層までのパスを、   
*  `volumes > name: data > hostPath: > path:`    
に記載してください。 

pod内でのパスを指定する場合は、`containers: > volumeMounts: > name: data > mountPath:`に適宜パスを設定してください。

### デプロイ
```
$ cd /path/to/random-voice-streaming-periodic
$ kubectl apply -f k8s/random-voice-streaming-periodic.yaml
```

### 音声データをdocker-imageにするには
**（動作未確認です）**   
1. random-voice-streaming-periodic内に音声を入れるフォルダを以下のように作成し、音声データを格納する。その後、`make docker-build`を実行する。   
   
例）  
```
$ cd /path/to/random-voice-streaming-periodic
$ mkdir voice-resources/face-audios
$ mkdir voice-resources/no-face-audios
```
2. `k8s/random-voice-streaming-periodic.yaml`内のenvの値とvolumes pathを書き換えて、デプロイする。   
例）
```
      containers:
          env:
          - name: FACE_DETECT_AUDIOS_PATH
            value: "./voice-resources/face-audios/"
          - name: NO_FACE_DETECT_AUDIOS_PATH
            value: "./voice-resources/no-face-audios/"
    （中略）
      volumes:
      - name: data
        hostPath:
          path: ./voice-resources/
```

### 使い方
1. `ws://localhost:30104/websocket_random_keep_listening` にアクセスする
1. `/raudio_hook/face`または`/raudio_hook/noface`というエンドポイントでHTTPリクエストを送る   
    例）`curl -v http://localhost:8889/audio_hook/face`   


<!-- * Sending message specify keyword (like 'hello')
* Getting binary raw audio data until send 'EOS' message
* if keyword does not exist in Mysql, Getting 'Not found' message -->


## I/O
### input
* 特定のHTTPリクエスト（定期的なもの）

### output
* ランダム選択された音声データを、ストリーミングする。
