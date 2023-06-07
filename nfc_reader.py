 # -*- coding: utf8 -*-
import binascii
import nfc
import os
import datetime
from os.path import exists
from post_slack import post_slack
import subprocess
import requests
import time
import random
import time



class MyCardReader(object):
    def on_connect(self, tag):
    
        #タッチ時の処理
        self.read_kucard(tag)
        
        print(datetime.datetime.now())
        print("タッチされました。 会員ID:"+str(self.idm) ,'会員氏名:'+(self.name))#タグ情報を全て表示
        print("カードを離してください")
        #print(tag)

        #IDmのみ取得して表示
        #self.idm = binascii.hexlify(tag._nfcid)
        #print("IDm : " + str(self.idm))

        #特定のIDmだった場合のアクション
        if self.idm == "00000000000000":
            print("【 登録されたIDです 】")

        return True
    

    def read_kucard(self, tag):
        servc = 0x1A8B
        service_code = [nfc.tag.tt3.ServiceCode(servc >> 6, servc & 0x3F)]

        tag.dump() # これがないと何故かうまくいかなかった

        bc_id = [nfc.tag.tt3.BlockCode(0)]
        bd_id = tag.read_without_encryption(service_code, bc_id)
        student_id = int(bd_id[2:-4].decode("utf-8"))

        bc_name = [nfc.tag.tt3.BlockCode(1)]
        student_name = (
            tag.read_without_encryption(service_code, bc_name)
            .decode("shift-jis")
            .rstrip("\x00")
        )

        self.idm = student_id
        self.name = student_name

    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr={'on-connect': self.on_connect})
        finally:
            clf.close()
        
 
if __name__ == '__main__':
    
    #if os.path.exists(path)==False:
        #os.mkdir(path)
    
    cr = MyCardReader()
    member_in = set()
    while True:
        #最初に表示
        print(datetime.datetime.now())
        print("ようこそ、SilverGymへ\n")

        #タッチ待ち
        try:
            cr.read_id()
        except AttributeError as e:
            print(e)
            print("カードが読み取れませんでした。職員証か学生証であることを確認してください。")
            print()
            print("-------------------------------------------------------------------")
            time.sleep(1)
            continue
        except nfc.tag.tt3.Type3TagCommandError:
            print("カードを離すのが早すぎます。")
            print()
            print("-------------------------------------------------------------------")
            continue

        
        music_list = ['waon.mp3', 'effect1.mp3', 'effect2.mp3', 'effect4.mp3']
        
        subprocess.run(['mpg321', random.choice(music_list)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    
        #リリース時の処理
        name = cr.name
        
        if name not in member_in:
            member_in.add(name)
            text = f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} : {name}が入室しました。"
            text2 = "10回3セット、しっかり追い込んでください"
            state = "enter"
        else:
            member_in.discard(name)
            text = f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} : {name}が退室しました。"
            text2 = "おつかれさまでした。"
            state = "exit"
            
        if len(member_in) == 0:
            text3 = "現在の入室メンバーはいません。"
        else:
            text3 = f"現在の入室メンバー: {member_in}。"
            
        print()
        print(text)
        print()
        print(text2)
        print()
        print(text3)
        
        #csv
        record='record'
        myfile='management.csv'
        if not exists(record):
            os.mkdir(record)
            
        with open(myfile,'w'):
            pass
        
        log_File=f'{record}/management.csv'#日時とIDの出力ファイル名
        csv_line=f'{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\t{cr.name}\t{state}'#出力内容
        
        #出力する
        with open(log_File,mode="a")as csv_file:
            csv_file.write(csv_line+'\r\n')
            
            
        # slack    
        try:
            post_slack(text + "\n\n" + text3)
            
            url='https://brain-dev-reg.slack.com/archives/CA9U8213Q'
            token='xoxb-349065939186-5178413647760-nD7m3G9r4kzC0jripch4hmqz'
            channel='CA9U8213Q'
            text='cr.idmが入室しました。'
            
            data={'token':token,'channel':channel,'text':text}
            requests.post(url,data=data)
        except:
            print()
            print("slackに通知できませんでした。問題ありませんが、何回か続くようでしたら担当者に連絡ください。")
            print()
            
        
        print("-------------------------------------------------")
        
#
        
