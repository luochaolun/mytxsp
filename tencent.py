import requests
import time
import re
import json
import random
import execjs
from tabulate import tabulate #表格对不齐，运行pip install wcwidth
from urllib.parse import parse_qs, urlsplit, quote
from tools import djb2Hash, updata_yaml, dealck, get_config

class tencent:
    def __init__(self, url):
        self.url = url
        self.vid = self.get_vid()
        self.userAgent = "mozilla/5.0 (windows nt 10.0; win64; x64) applewebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        self.logintoken = {
            "access_token": "",
            "appid": "",
            "vusession": "",
            "openid": "",
            "vuserid": "",
            "main_login": ""
        }
        self.int_time = int(time.time())
        self.cookie = self.get_cookie()
        self.cookie_dict = {}

        self.headers = {
            "User-Agent": self.userAgent,
            "Referer": "https://v.qq.com",
            "Cookie": self.cookie,
        }
        self.re = requests.session()
        self.re.headers.update(self.headers)
        self.login()
        self.parse_cookie()

    def get_cookie(self):
        config = get_config()
        txck = config["txck"]
        return txck

    def login(self):
        cookie = dealck(self.cookie)
        for i in self.logintoken:
            self.logintoken[i] = cookie.get(i)
        url = 'https://access.video.qq.com/user/auth_refresh'
        params = {
            "vappid": "11059694",
            "vsecret": "fdf61a6be0aad57132bc5cdf78ac30145b6cd2c1470b0cfe",
            "type": self.logintoken["main_login"],
            "g_tk": "",
            "g_vstk": djb2Hash(self.logintoken["vusession"]),
            "g_actk": djb2Hash(self.logintoken["access_token"]),
            "_": str(int(time.time() * 1000)),
        }
        data = self.re.get(url, params=params).text
        data = json.loads(data.split("=")[1])
        access_token = data["access_token"]
        vusession = data["vusession"]
        self.cookie = self.cookie.replace(self.logintoken["access_token"], access_token)
        self.cookie = self.cookie.replace(self.logintoken["vusession"], vusession)
        self.logintoken["access_token"] = access_token
        self.logintoken["vusession"] = vusession
        self.headers = {
            "User-Agent": self.userAgent,
            "Referer": "https://v.qq.com",
            "Cookie": self.cookie,
        }
        self.re.headers.update(self.headers)
        updata_yaml("txck", self.cookie)

    def parse_cookie(self):
        if self.cookie:
            for i in self.cookie.split(";"):
                kv = i.split("=")
                self.cookie_dict[kv[0].strip()] = kv[1]

    def get_vid(self):
        this_url = urlsplit(self.url)
        host = this_url.netloc
        if host == 'v.qq.com':
            pathArr = this_url.path.split("/")
            if pathArr[2] == 'cover' and len(pathArr) == 4:
                vid = None
            else:
                vid = pathArr[-1].split(".")[0]
        elif host == 'm.v.qq.com':
            this_query = parse_qs(this_url.query)
            try:
                vid = this_query['vid'][0]
            except:
                vid = None
        else:
            vid = None

        return vid

    def getGUID(self):
        s = ""
        for i in range(32):
            s += random.choice('abcdef1234567890')
        return s

    def get_vinfoparams(self):
        spsrt = "1"
        charge = "1"
        defaultfmt = "auto"
        otype = "ojson"
        guid = self.getGUID()
        platform = "10901"
        # 随机数 + platform
        flowid = self.getGUID() + "_" + platform
        sdtfrom = "v1010"
        defnpayver = "1"
        appVer = "3.5.57"
        host = "v.qq.com"
        ehost = quote(self.url)
        refer = "v.qq.com"
        sphttps = "1"
        tm = self.int_time
        spwm = "4"
        logintoken = quote(str({"main_login": self.cookie_dict['main_login'], "openid": self.cookie_dict['openid'],
                                "appid": self.cookie_dict['appid'],
                                "access_token": self.cookie_dict['access_token'],
                                "vuserid": self.cookie_dict['vuserid'],
                                "vusession": self.cookie_dict['vusession']}))
        defn = "fhd"    # 可选参数 1: 'sd', 2: 'hd', 3: 'shd', 4: 'fhd'
        fhdswitch = "0"
        show1080p = "1"
        isHLS = "1"
        dtype = "3"
        sphls = "2"
        spgzip = "1"
        dlver = "2"
        drm = "32"
        hdcp = "1"
        spau = "1"
        spaudio = "15"
        defsrc = "1"
        encryptVer = "9.1"
        cKey = self.get_cKey(platform, appVer, self.vid, guid, tm)
        fp2p = "1"
        spadseg = "3"
        result = f"spsrt={spsrt}&charge={charge}&defaultfmt={defaultfmt}&otype={otype}&guid={guid}&flowid={flowid}&platform={platform}&sdtfrom={sdtfrom}&defnpayver={defnpayver}&appVer={appVer}&host={host}&ehost={ehost}&refer={refer}&sphttps={sphttps}&tm={tm}&spwm={spwm}&logintoken={logintoken}&vid={self.vid}&defn={defn}&fhdswitch={fhdswitch}&show1080p={show1080p}&isHLS={isHLS}&dtype={dtype}&sphls={sphls}&spgzip={spgzip}&dlver={dlver}&drm={drm}&hdcp={hdcp}&spau={spau}&spaudio={spaudio}&defsrc={defsrc}&encryptVer={encryptVer}&cKey={cKey}&fp2p={fp2p}&spadseg={spadseg}"
        return result

    def get_cKey(self, platform, version, vid, guid, tm):
        file = './js/getck.js'
        ctx = execjs.compile(open(file).read())
        params = ctx.call("getckey", platform, version, vid, '', guid, tm)
        return params

    @staticmethod
    def get_list(url):
        def get_cid():
            this_url = urlsplit(url)
            host = this_url.netloc
            if host == 'v.qq.com':
                pathArr = this_url.path.split("/")
                if pathArr[2] == 'page':
                    cid = None
                else:
                    cid = pathArr[3].split(".")[0]
            elif host == 'm.v.qq.com':
                this_query = parse_qs(this_url.query)
                try:
                    cid = this_query['cid'][0]
                except:
                    cid = None
            else:
                cid = None

            return cid

        def get_video_data(data, ret=[]):
            cookies = {
                "appid": "wxa75efa648b60994b",
                "vversion_name": "8.2.95.1",
                "video_bucketid": "4",
                "video_omgid": ""
            }
            params = {
                "video_appid": "3000002",
                "guid": "",
                "vplatform": "5",
                "callerid": "3000002"
            }
            headers = {
                "Accept-Encoding": "gzip,compress,br,deflate",
                "Connection": "keep-alive",
                "Host": "pbaccess.video.qq.com",
                "Referer": "https://servicewechat.com/wxa75efa648b60994b/629/page-frame.html",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.42(0x18002a2e) NetType/WIFI Language/zh_CN",
                "content-type": "application/json"
            }
            url = "https://pbaccess.video.qq.com/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData"
            response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)
            response_data = response.json()
            module_list_datas = response_data['data']['module_list_datas']
            for module_list_data in module_list_datas:
                module_data = module_list_data['module_datas'][0]
                if module_data['module_params']['module_type'] == "episode_list":
                    has_next = module_data['module_params']['has_next']
                    item_datas = module_data['item_data_lists']['item_datas']
                    for item_data in item_datas:
                        item_type = item_data['item_type']
                        if int(item_type) == 23:
                            print(item_data['item_params']['sub_title'])
                            continue
                        item_params = item_data['item_params']
                        play_type = item_params['play_type']
                        if int(play_type) != 1:
                            continue
                        cover_c_title = item_params['cover_c_title']
                        play_title = item_params['play_title']
                        vid = item_params['vid']
                        # defn = eval(item_params['defn'])
                        # defn = sorted(defn.items(), key=lambda x: x[1], reverse=True)
                        ret.append([cover_c_title, play_title, vid])
                    if has_next == "true":
                        next_page_context = module_data['module_params']['next_page_context']
                        data = {
                            "page_params": {
                                "page_type": "detail_operation",
                                "cid": "",
                                "page_id": "vsite_episode_list",
                                "page_context": next_page_context,
                            }
                        }
                        get_video_data(json.dumps(data, separators=(',', ':')), ret)
                    else:
                        break
            return ret

        cid = get_cid()
        if cid is None:
            return None
        #cid = url.split("/")[5].split(".")[0]
        data = {
            "page_params": {
                "page_type": "video_detail",
                "cid": cid
            }
        }

        data = get_video_data(json.dumps(data, separators=(',', ':')))
        return data

    def start(self):
        if self.vid is None:
            return ('', '')

        vinfoparams = self.get_vinfoparams()
        params = {"buid": "vinfoad", "vinfoparam": vinfoparams}
        res = requests.post("https://vd.l.qq.com/proxyhttp", headers=self.headers, json=params)
        res_json = json.loads(res.json()['vinfo'])
        title = ''
        vurl = ''
        fname = ''
        try:
            title = res_json['vl']['vi'][0]['ti']
            vurl = res_json['vl']['vi'][0]['ul']['ui'][0]['url']
            fname = res_json['vl']['vi'][0]['ul']['ui'][0]['hls']['pt']
        except:
            pass
        vurl += fname
    
        return (title, vurl)


if __name__ == '__main__':
    #url = 'https://v.qq.com/x/cover/mzc002009eh8rti/t0048z8o7fo.html'
    #url = 'https://m.v.qq.com/x/m/play?cid=mzc002009eh8rti&vid=t0047nzr5q0&mobile=1&ptag=11966'
    #url = 'https://v.qq.com/x/cover/mzc002009eh8rti.html'
    #url = 'https://v.qq.com/x/page/q3536054nq0.html'
    #url = 'https://m.v.qq.com/x/m/play?vid=q3536054nq0&cid=&url_from=share&second_share=0&share_from=copy'
    #url = 'https://v.qq.com/x/cover/mzc002006wiw7ll/r0047sjjwbr.html'
    #url = 'https://v.qq.com/x/cover/mzc00200whsp9r6/a0047l69jnp.html'
    url = 'https://v.qq.com/x/cover/mzc00200d3xsqel/q0047g609um.html'
    tx = tencent(url)

    data = tx.get_list(url)
    if data is not None:
        print(tabulate(data, headers=['Nb', 'cover_c_title', 'play_title', 'vid'], tablefmt="grid",
                   showindex=range(1, len(data) + 1)))

    title, vurl = tx.start()
    savepath = f"./download/{title}/"
    cmd = f"N_m3u8DL-RE.exe \"{vurl} \" --tmp-dir ./cache --save-name \"{title}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count"
    with open("{}.bat".format(title), "a", encoding="utf-8") as f:
        f.write("chcp 65001\n")
        f.write(cmd)
        f.write("\n")
    print(f"已生成下载脚本{title}.bat 请运行下载")
    print(title, vurl)
