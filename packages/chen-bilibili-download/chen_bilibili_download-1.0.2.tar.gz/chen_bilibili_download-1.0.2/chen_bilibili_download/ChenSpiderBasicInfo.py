import random


class ChenSpiderBasicInfo:
    """ 这是一个获取头部信息和代理信息的父类"""

    def __init__(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        }
        proxies = {
            "http": ["47.99.112.148", "8.137.38.48", "114.231.46.160", "180.122.147.205", "117.69.232.248",
                     "112.244.230.117", "114.232.110.33", "114.232.110.141", "182.34.37.218", "117.69.237.103",
                     '36.6.144.235'],
            "https": ['114.106.137.169', '117.69.233.179', '113.223.213.80', '117.71.154.81']
        }
        self.headers = headers
        self.proxies = proxies
        self.random_proxy = {
            "http": random.choice(self.proxies["http"]),
            # 'https':random.choice(proxies["https"])
        }

    def get_headers(self):
        """ 获取头部信息"""

        return self.headers

    def get_random_proxy(self):
        """这是一个获取随机代理proxy（怕会封所以每次都用随机代理）的函数"""

        self.random_proxy = {
            "http": random.choice(self.proxies["http"]),
            # 'https':random.choice(proxies["https"])
        }
        return self.random_proxy