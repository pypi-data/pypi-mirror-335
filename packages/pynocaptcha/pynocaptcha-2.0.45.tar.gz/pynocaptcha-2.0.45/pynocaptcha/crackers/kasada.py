# -*- coding: UTF-8 -*-

import re
import random
import base64
from curl_cffi import requests
from urllib.parse import urlencode
from loguru import logger
from .base import BaseCracker
from .utils import parse_client_hints


class KasadaCtCracker(BaseCracker):
    cracker_name = "kasada"
    cracker_version = "ct"

    """
    kasada x-kpsdk-ct cracker
    :param href: 触发验证的页面地址
    :param script_url: p.js 脚本地址
    调用示例:
    cracker = KasadaCtCracker(
        user_token="xxx",
        href="https://arcteryx.com/ca/en/shop/mens/beta-lt-jacket-7301",
        script_url="https://mcprod.arcteryx.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        proxy="user:pass@ip:port",
        debug=True,
    )
    ret = cracker.crack()
    """

    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "proxy": None,
        "fp_host": None,
        "fp_html": None,
        "ips_script": None,
        "ips_headers": None,
        "country": None,
        "ip": None,
        "timezone": None,
        "submit": False,
        "iframe": True,
        "user_agent": None,
        "timeout": 30
    }

    def request(self):            
        if 'fp_html' in self.wanda_args:
            return

        self._fp_protocol = self.href.split("://")[0]
        if not self.fp_host:
            self.fp_host = self.href.split("/")[2]
            
        country = self.wanda_args.get("country")
        _ip = self.wanda_args.get("ip")
        timezone = self.wanda_args.get("timezone")
            
        if not self.user_agent:
            version = random.randint(115, 134)
            self.user_agent = random.choice([
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
                f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
                f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0',
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0",
            ])
            
        # 跟 ua 版本对应
        sec_ch_ua = parse_client_hints(self.user_agent)
        sec_ch_ua_ptf = '"macOS"' if 'Mac' in self.user_agent else '"Windows"'

        impersonates = [
            "chrome116", "chrome119", "chrome120", "chrome124", "edge99", "edge101",
        ]
        if sec_ch_ua_ptf == '"macOS"':
            impersonates += ["safari15_3", "safari15_5", "safari17_0", "safari17_2_ios"]     
        
        impersonate = random.choice(impersonates)
        self.session = requests.Session(impersonate=impersonate)
        if self.proxy:
            self.session.proxies.update({
                "all": "http://" + self.proxy
            })
        if self.cookies:
            self.session.cookies.update(self.cookies)

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-HK,zh;q=0.9',
            'sec-fetch-dest': "document",
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': "none",
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agent,
            'sec-ch-ua': sec_ch_ua,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': sec_ch_ua_ptf,
        }
        
        if self.iframe:            
            headers["sec-fetch-dest"] = "iframe"
            headers["sec-fetch-site"] = "same-site"
            response = self.session.get(f"{self._fp_protocol}://{self.fp_host}/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-1.0.0", headers=headers)
        else:
            response = self.session.get(self.href, headers=headers)

        if response.status_code not in [429, 200]:
            raise Exception(f"fp status code: {response.status_code}")
        
        self.fp_html = response.text
        if '/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js' not in self.fp_html and 'KPSDK' in self.fp_html:
            self.wanda_args = {
                "href": self.href,
                "fp_host": self.fp_host,
                "fp_html": self.fp_html,
                "user_agent": self.user_agent,
                "cookies": dict(self.session.cookies),
                "submit": self.submit,
                "iframe": self.iframe,
                
                "branch": self.branch,
                "is_auth": self.wanda_args["is_auth"],
            }
            if self.submit:
                if not self.proxy:
                    raise Warning("缺少代理")
                self.wanda_args["proxy"] = self.proxy
        else:
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-HK,zh;q=0.9',
                'priority': 'u=1',
                'referer': self.href,
                'sec-ch-ua': sec_ch_ua,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': sec_ch_ua_ptf,
                'sec-fetch-dest': 'script',
                'sec-fetch-mode': 'no-cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self.user_agent,
            }
            
            # KP_UIDz
            self.uidk = None
            for k, _ in self.session.cookies.items():
                if k.endswith('-ssn'):
                    self.uidk = k.replace('-ssn', '')
            
            if not self.uidk:
                raise Warning("站点异常, 请联系管理员处理")

            ips_url = self._fp_protocol + '://' + self.fp_host + re.search(r'src="(\/149e9513-01fa-4fb0-aad4-566afd725d1b\/2d206a39-8ed7-437e-a3be-862e0f06eea3\/ips\.js\?.*?)"', self.fp_html)[1].replace('amp;', '')
            
            if not self.submit:
                ips_resp = self.session.get(ips_url, headers=headers)
                self.wanda_args = {
                    "href": self.href,
                    "fp_host": self.fp_host,
                    "fp_html": self.fp_html,
                    "ips_script": ips_resp.text,
                    "ips_headers": dict(ips_resp.headers),
                    "cookies": dict(self.session.cookies),
                    "user_agent": self.user_agent,
                    "submit": False,
                    "iframe": self.iframe,
                    
                    "branch": self.branch,
                    "is_auth": self.wanda_args["is_auth"],
                }
            else:
                self.wanda_args = {
                    "href": self.href,
                    "fp_host": self.fp_host,
                    "fp_html": self.fp_html,
                    "cookies": dict(self.session.cookies),
                    "user_agent": self.user_agent,
                    "submit": True,
                    "iframe": self.iframe,
                    "proxy": self.proxy,

                    "branch": self.branch,
                    "is_auth": self.wanda_args["is_auth"],
                }

        if country:
            self.wanda_args["country"] = country
            
        if _ip:
            self.wanda_args["ip"] = _ip
        
        if timezone:
            self.wanda_args["timezone"] = timezone

    def response(self, result):
        if hasattr(self, 'session'):  
            fp_url = f"{self._fp_protocol}://{self.fp_host}/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/fp?x-kpsdk-v=j-1.0.0"
            if not self.submit:          
                headers = {
                    'accept': '*/*',
                    'accept-language': self._extra_data['accept-language'],
                    'content-type': 'application/octet-stream',
                    'origin': f'{self._fp_protocol}://{self.fp_host}',
                    'priority': 'u=1, i',
                    'referer': self.href if self.iframe else fp_url,
                    'sec-ch-ua': self._extra_data["sec-ch-ua"],
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': self._extra_data["sec-ch-ua-platform"],
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': self.user_agent,
                    **result["headers"]
                }
                
                response = self.session.post(
                    f'{self._fp_protocol}://{self.fp_host}/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/tl',
                    headers=headers,
                    data=base64.b64decode(result["post_data"].encode()),
                )
                # if self.debug:
                #     logger.debug(f'kasada tl result: {response.status_code}, {response.text}')
                
                if 'reload' not in response.text:
                    raise Exception("kasada 验证失败")
                
                kpsdk_ct = response.headers.get('x-kpsdk-ct')
                kpsdk_st = int(response.headers.get('x-kpsdk-st'))
            else:
                # 把 cookie set 进去
                kpsdk_ct = result['x-kpsdk-ct']
                kpsdk_st = int(result['x-kpsdk-st'])
                self.session.cookies.update({
                    self.uidk: kpsdk_ct,
                    self.uidk + "-ssn": kpsdk_ct
                })

            headers = {
                'sec-ch-ua': self._extra_data["sec-ch-ua"],
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': self._extra_data["sec-ch-ua-platform"],
                'upgrade-insecure-requests': '1',
                'user-agent': self._extra_data["user-agent"],
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-dest': 'iframe',
                'referer': self.href,
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': self._extra_data["accept-language"],
                'priority': 'u=0, i',
            }
            resp = self.session.get(fp_url, headers=headers)
            
            # if self.debug:
            #     logger.debug(f'kasada cookie reset status: {resp.status_code}')
            
            if resp.status_code == 200:
                kpsdk = re.search(r"KPSDK.message='KPSDK:DONE:(.*?)::.*?:2:(\d+):1-", resp.text)
                kpsdk_ct = kpsdk[1]
                kpsdk_st = int(kpsdk[2])
            
            _result = {
                "x-kpsdk-ct": kpsdk_ct,
                "x-kpsdk-st": kpsdk_st,
            }
            if result.get("x-kpsdk-cd"):
                _result["x-kpsdk-cd"] = result["x-kpsdk-cd"]
            
            if self.debug:
                logger.info(_result)
            return _result
        return result


class KasadaCdCracker(BaseCracker):
    cracker_name = "kasada"
    cracker_version = "cd"

    """
    kasada x-kpsdk-ct cracker
    :param href: 触发验证的页面地址
    调用示例:
    cracker = KasadaCdCracker(
        user_token="xxx",
        href="https://arcteryx.com/ca/en/shop/mens/beta-lt-jacket-7301",
        debug=True,
    )
    ret = cracker.crack()
    """

    # 必传参数
    must_check_params = ["href", "st"]
    option_params = {
        "ct": ""
    }
