import os
import json
import requests
import pywifi
import time

errNum=0
iface = pywifi.PyWiFi().interfaces()[0]# 获取第一个无线网卡
def outprint(text:str)->str:
    '''打印并保存日志'''
    fliePath=os.path.join(os.getcwd(),'log')
    if not os.path.exists(fliePath):os.mkdir(fliePath)
    logFile=os.path.join(fliePath,f'{time.strftime("%Y-%m-%d",time.localtime())}.txt')
    text=f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]{text}'
    with open(logFile,'at') as f:
        f.writelines('\n'+text)
    print(text)
    return text

def getNet()->bool:
    '''获取网络状态'''
    global errNum
    try:
        response=requests.get('http://httpdns.alicdn.com/multi_httpdns_resolve?host_key=baidu.com')
        json.loads(response.text)['ttl']
        outprint(f'网络状态正常')
        return True
    except:
        outprint(f'网络状态异常:{errNum}')
        return False

def getWifiConfigList()->list:
    '''获取wifi列表'''
    global iface
    wifilists=[]
    ssidList=[]
    signalList=[]
    wifilist=[]
    configList=[]
    iface.scan()#扫描WiFi
    results = iface.scan_results()# 获取扫描结果
    for result in results:
        if result.ssid=='':
            continue
        try:
            signal_num=ssidList.index(result.ssid)
            if signalList[signal_num]>result.signal:
                ssidList[signal_num]=result.ssid
                signalList[signal_num]=result.signal
            else:
                continue
        except:
            ssidList.append(result.ssid)
            signalList.append(result.signal)
    for i in range(len(ssidList)):
        wifia={
            "ssid":ssidList[i],
            "signal":signalList[i]
        }
        wifilist.append(wifia)
    wifilist=sorted(wifilist,key=lambda x:-x['signal'])
    configFile=os.path.join(os.getcwd(),'config.json')
    with open(configFile,'r') as f:
        configList=json.loads(f.read())

    for wifia in wifilist:
        ssid=wifia["ssid"]
        for wifib in configList:
            if ssid==wifib['ssid']:
                wifilists.append(wifib)
    outprint(f'获取wifi列表，数量{len(wifilists)}个')
    return wifilists

def conWifi(wifiConfig:dict)->bool:
    '''链接wifi'''
    global iface
    profile = pywifi.Profile()
    profile.ssid = wifiConfig['ssid']
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    profile.key = wifiConfig['password']
    iface.disconnect()# 断开当前连接的无线网络
    # iface.remove_all_network_profiles()#删除所有连接过的wifi文件
    tmp_profile = iface.add_network_profile(profile)#添加wifi文件
    iface.connect(tmp_profile)# 连接wifi
    time.sleep(8)
    if iface.status() != pywifi.const.IFACE_CONNECTED:
        outprint(f'wifi连接失败，wifi:{wifiConfig}')
        return False
    else:
        return getNet()


while True:
    if errNum>=50:
        break
    if getNet():
        time.sleep(30*60)
    else:
        wifiList=getWifiConfigList()
        if len(wifiList)==0:time.sleep(8);wifiList=getWifiConfigList()
        for wifiConfig in wifiList:
            if conWifi(wifiConfig):
                break
            errNum+=1
            time.sleep(8)

