import warnings

import re
import random
import json
from .base import BaseCracker
from curl_cffi import requests

warnings.filterwarnings('ignore')


class ShapeV2Cracker(BaseCracker):
    
    cracker_name = "shape"
    cracker_version = "v2"    

    """
    shape cracker
    :param href: 触发 shape 验证的首页地址
    :param user_agent: 请求流程使用 ua
    :param script_url: 加载 shape vmp 脚本的 url
    :param vmp_url: shape vmp 脚本的 url
    :param pkey: shape 加密参数名, x-xxxx-a 中的 xxxx, 如星巴克的 Dq7hy5l1-a 传  dq7hy5l1 即可
    :param request: 需要 shape 签名的接口内容
    :param fast: 是否加速计算, 默认 false （网站风控低可使用该模式）
    :param submit: 是否直接提交 request 返回响应, 默认 false
    :param return_header: submit 为 true 时返回的响应是否返回响应头 headers, 默认 false
    :param timeout: 最大破解超时时间
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "html": None,
        "pkey": None,
        "request": None,
        "action": None,
        "count": 1,
        "script_url": None,
        "script_content": None,
        "vmp_url": None,
        "vmp_regexp": None,
        "vmp_content": None,
        "user_agent": None,
        "proxy": None,
        "country": None,
        "ip": None,
        "timezone": None,
        "headers": {},
        "cookies": {},
        "fast": True,
        "submit": False,
        "timeout": 30
    }
    
    def request(self):
        if not self.user_agent:
            version = random.randint(115, 131)
            self.user_agent = random.choice([
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
                f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
                f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0',
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0",
            ])
            self.wanda_args["user_agent"] = self.user_agent
            
        platform = '"macOS"' if 'Mac' in self.user_agent else '"Windows"'

        origin = "/".join(self.href.split("/")[0:3])

        impersonates = [
            "chrome116", "chrome119", "chrome120", "chrome124", "edge99", "edge101",
        ]
        if platform == '"macOS"':
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
            'accept': '*/*',
            'priority': 'u=1',
            'referer': self.href,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': platform,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
        }
        if not self.wanda_args.get("pkey"):
            html = self.html
            if not html:
                response = self.session.get(self.href, headers=headers)
                html = response.text

            if 'ISTL-REDIRECT-TO' not in html:
                raise Warning("未触发 shape 盾")

            country = self.wanda_args.get("country")
            _ip = self.wanda_args.get("ip")
            timezone = self.wanda_args.get("timezone")
            self.wanda_args = {
                "href": self.href,
                "html": html,
                "user_agent": self.user_agent,
                "fast": self.fast,

                "branch": self.branch,
                "is_auth": self.wanda_args["is_auth"],
            }
            
            if country:
                self.wanda_args["country"] = country
            
            if _ip:
                self.wanda_args["ip"] = _ip
            
            if timezone:
                self.wanda_args["timezone"] = timezone
        
        else:
            if not self.wanda_args.get("script_url"):
                
                data = {
                    "method": "read",
                    "key": self.pkey.lower(),
                }
                site_arg = requests.post(
                    f"http://{self.api_host}/api/wanda/shape/p",
                    json=data
                ).text
                if not site_arg:
                    raise Warning("暂不支持的站点, 请联系管理员添加")
                
                site_arg = json.loads(site_arg)
                
                self.wanda_args["script_url"] = site_arg.get("script_url")
                self.wanda_args["vmp_url"] = site_arg.get("vmp_url")
                self.wanda_args["vmp_regexp"] = site_arg.get("vmp_regexp")
                
                if not self.wanda_args.get("request"):
                    self.wanda_args["request"] = site_arg.get("request")
            
            if self.wanda_args["script_url"]:
                
                if not self.wanda_args.get("script_content"):
                    try:
                        script = self.session.get(self.wanda_args["script_url"], headers=headers, verify=False).text
                        self.wanda_args["script_content"] = script
                    except:
                        raise Warning("初始化脚本获取失败")

                vmp_url = self.wanda_args.get("vmp_url")
                if not vmp_url:
                    if self.wanda_args.get("vmp_regexp"):
                        try:
                            vmp_url = re.search(self.wanda_args["vmp_regexp"], script)[1]
                        except:
                            raise Warning("vmp 地址获取失败")

                if vmp_url:
                    if not vmp_url.startswith("http"):
                        vmp_url = origin + vmp_url
                    
                    if not self.wanda_args.get("vmp_content"):
                        try:
                            vmp_resp = self.session.get(vmp_url, headers=headers, verify=False)
                            if vmp_resp.status_code != 200:
                                raise Warning("vmp 脚本请求失败")
                            self.wanda_args["vmp_url"] = vmp_url
                            self.wanda_args["vmp_content"] = vmp_resp.text
                        except:
                            raise Warning("vmp 获取失败")

                if self.wanda_args.get("vmp_regexp"):
                    del self.wanda_args["vmp_regexp"]
                    
            else:
                raise Warning("配置异常, 请联系管理员")

        self.wanda_args["cookies"] = {
            **self.cookies,
            **{
                k: v for k, v in self.session.cookies.items()
            }
        }
        if self.wanda_args.get("proxy") and not self.submit:
            del self.wanda_args["proxy"]
    

class ShapeV1Cracker(BaseCracker):
    
    cracker_name = "shape"
    cracker_version = "v1"    

    """
    shape cracker
    :param href: 触发 shape 验证的首页地址
    :param user_agent: 请求流程使用 ua
    :param vmp_url: shape vmp 脚本的 url
    :param vmp_content: shape vmp 脚本内容
    :param timeout: 最大破解超时时间
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "proxy": None,
        "vmp_url": None,
        "vmp_content": None,
        "script_url": None,
        "script_content": None,
        "user_agent": None,
        "country": None,
        "ip": None,
        "headers": {},
        "cookies": {},
        "fast": True,
        "timeout": 30
    }

    def request(self):
        if not self.user_agent:
            version = random.randint(115, 134)
            self.user_agent = random.choice([
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
                f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
                f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0',
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0",
            ])
            self.wanda_args["user_agent"] = self.user_agent
            
        platform = '"macOS"' if 'Mac' in self.user_agent else '"Windows"'

        domain = self.href.split("/")[2]
        origin = "/".join(self.href.split("/")[0:3])

        impersonates = [
            "chrome116", "chrome119", "chrome120", "chrome124", "edge99", "edge101",
        ]
        if platform == '"macOS"':
            impersonates += ["safari15_3", "safari15_5", "safari17_0", "safari17_2_ios"]     
        
        impersonate = random.choice(impersonates)
        self.session = requests.Session(impersonate=impersonate)
        if self.proxy:
            self.session.proxies.update({
                "all": "http://" + self.proxy
            })
        if self.cookies:
            self.session.cookies.update(self.cookies)
        
        if not self.wanda_args.get("script_url"):
            
            data = {
                "method": "read",
                "key": domain,
            }
            site_arg = requests.post(
                f"http://{self.api_host}/api/wanda/shape/p",
                json=data
            ).text
            if not site_arg:
                raise Warning("暂不支持的站点, 请联系管理员添加")
            
            site_arg = json.loads(site_arg)
            if site_arg.get("script_url"):
                self.wanda_args["script_url"] = site_arg["script_url"]
                
            self.wanda_args["vmp_url"] = site_arg.get("vmp_url")
            self.wanda_args["vmp_regexp"] = site_arg.get("vmp_regexp")
        
        headers = {
            'accept': '*/*',
            'priority': 'u=1',
            'referer': self.href,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': platform,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
        }
        if self.wanda_args.get("script_url"):
            if not self.wanda_args.get("script_content"):
                try:
                    script = self.session.get(self.wanda_args["script_url"], headers=headers, verify=False).text
                    self.wanda_args["script_content"] = script
                except:
                    raise Warning("初始化脚本获取失败")

        vmp_url = self.wanda_args.get("vmp_url")
        if not vmp_url:
            if self.wanda_args.get("vmp_regexp"):
                try:
                    vmp_url = re.search(self.wanda_args["vmp_regexp"], script)[1]
                except:
                    raise Warning("vmp 地址获取失败")

        if vmp_url:
            if not vmp_url.startswith("http"):
                vmp_url = origin + vmp_url
            
            if not self.wanda_args.get("vmp_content"):
                try:
                    vmp_resp = self.session.get(vmp_url, headers=headers, verify=False)
                    if vmp_resp.status_code != 200:
                        raise Warning("vmp 脚本请求失败")
                    self.wanda_args["vmp_url"] = vmp_url
                    self.wanda_args["vmp_content"] = vmp_resp.text
                except:
                    import traceback
                    traceback.print_exc()
                    raise Warning("vmp 获取失败")
        
        if self.wanda_args.get("vmp_regexp"):
            del self.wanda_args["vmp_regexp"]

        self.wanda_args["cookies"] = {
            **self.cookies,
            **{
                k: v for k, v in self.session.cookies.items()
            }
        }
        if self.wanda_args.get("proxy"):
            del self.wanda_args["proxy"]
