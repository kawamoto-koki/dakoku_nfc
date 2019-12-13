# -*- coding: utf-8 -*-
import binascii
import nfc
import time
import requests
import os.path
import os
from threading import Thread, Timer

# Suica待ち受けの1サイクル秒
TIME_cycle = 1.0
# Suica待ち受けの反応インターバル秒
TIME_interval = 0.2
# タッチされてから次の待ち受けを開始するまで無効化する秒
TIME_wait = 3
# 音量設定
SOUND_Volume = '100%'
os.system('amixer set PCM ' + SOUND_Volume)

# NFC接続リクエストのための準備
# 212F(FeliCa)で設定
target_req_suica = nfc.clf.RemoteTarget("212F")
# 0003(Suica)
target_req_suica.sensf_req = bytearray.fromhex("0000030000")

# dakoku_san API endpoint
url = os.environ['DAKOKU_SAN_API_URL']
# dakoku_san API Token
token = os.environ['DAKOKU_SAN_API_TOKEN']
header = {'Authorization': 'Bearer ' + token}

print 'Suica waiting...'
while True:
    # USBに接続されたNFCリーダに接続してインスタンス化
    clf = nfc.ContactlessFrontend('usb')
    # Suica待ち受け開始
    # clf.sense( [リモートターゲット], [検索回数], [検索の間隔] )
    target_res = clf.sense(target_req_suica, iterations=int(TIME_cycle//TIME_interval)+1 , interval=TIME_interval)

    if target_res != None:
        os.system('aplay assets/touch.wav')
        tag = nfc.tag.activate_tt3(clf, target_res)
        tag.sys = 3

        #IDmを取り出す
        idm = binascii.hexlify(tag.idm)
        print 'Suica detected. idm = ' + idm
        data = {'idm': idm}
        response = requests.put(url, data=data, header=header)

        # リクエスト失敗時にエラー音を鳴らす
        if not response.status_code == requests.codes.ok:
            print(response.text)
            os.system('aplay assets/error.wav')
        #end if

        # カード登録時にのみ音を鳴らす
        res_json = response.json()
        res_code = res_json['context']
        if res_code == 'save_idm'
            os.system('aplay assets/save_idm.wav')
            print(res_json.values())
        #end if
	time.sleep(TIME_wait)
    #end if

    clf.close()

#end while
