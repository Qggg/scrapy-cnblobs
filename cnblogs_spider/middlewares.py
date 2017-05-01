# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class CnblogsSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectError, ConnectionRefusedError
from scrapy.core.downloader.handlers.http11 import TunnelError

import requests
import json
class ProxyMgr:
    def __init__(self):
        self.proxyes = [{"proxy":None, "valid":True, "count":0}]
        self.url_getall = "http://127.0.0.1:4999/getall/"
        self.url_deleteone = "http://127.0.0.1:4999/delete?proxy="
        self.validproxycount=0
        self.validproxycuridx=0
        self.lastProxy=None

    def add_new_proxys(self):
        proxylist = json.loads(requests.get(self.url_getall).text)
        tempnew=[]
        for anewproxy in proxylist:
            for aexistproxy in self.proxyes:
                #找是否已经存在
                #print("self.proxyes={},aexistproxy = {}".format(str(self.proxyes),str(aexistproxy)))
                if anewproxy == aexistproxy["proxy"]:
                    if aexistproxy["valid"] == False:
                        #已经失效了，那么从服务端删掉
                        requests.get(self.url_deleteone+aexistproxy["proxy"][7:])
                        print("del url=",self.url_deleteone+aexistproxy["proxy"][7:])
                        del aexistproxy
                    continue
                else:
                    tempnew.append({"proxy":"http://{}".format(anewproxy), "valid":True, "count":0})
                    # tempnew.append({"proxy": "https://{}".format(anewproxy), "valid": True, "count": 0})
                    self.validproxycount += 1
        self.proxyes += tempnew

    def set_proxy_invalid(self, aproxy):
        if aproxy == None:
            return

        maxnum = len(self.proxyes)
        for idx in range(maxnum):
            if aproxy == self.proxyes[idx]["proxy"]:
                # self.proxyes[idx]["valid"] = False
                self.validproxycount -= 1
                if idx <= self.validproxycuridx and self.validproxycuridx>0:
                    self.validproxycuridx -= 1
                print("del url=", self.url_deleteone + self.proxyes[idx]["proxy"][7:])
                requests.get(self.url_deleteone + self.proxyes[idx]["proxy"][7:])
                del self.proxyes[idx]
                return

    def get_valid_proxy_count(self):
        return self.validproxycount

    def get_all_proxy_count(self):
        return len(self.proxyes)

    def get_a_proxy(self, changeproxy=False):
        if self.get_valid_proxy_count() == 0:
            # print("1111111111")
            return None
        if changeproxy == False and self.lastProxy!=None:
            return self.lastProxy
        #轮转
        idx = self.validproxycuridx
        loopcnt = 0
        # print("proxyes=",self.proxyes)
        while loopcnt<self.get_all_proxy_count():
            loopcnt += 1
            idx += 1
            if idx == self.get_all_proxy_count()-1:
                idx = 0
            #print("proxyes[idx]={},proxyes={}".format(str(self.proxyes[idx]), str(self.proxyes)))
            if self.proxyes[idx]["valid"] == True and self.proxyes[idx]["proxy"] != None:
                self.validproxycuridx = idx
                self.proxyes[idx]["count"] += 1
                self.lastProxy = self.proxyes[idx]["proxy"]
                return self.proxyes[idx]["proxy"]
        # print("222222222")
        return None


class HttpProxyMiddleware(object):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectError, ConnectionRefusedError, ValueError, ResponseNeverReceived, TunnelError)

    def __init__(self):
        #拿全部
        self.proxy_getter = ProxyMgr()
        self.proxy_getter.add_new_proxys()
        self.cur_proxy_used_cnt=0
        self.MAX_PROXY_USED_CNT = 50
        self.MIN_PROXY_CNT_NEED_SUPLY = 10

    def set_proxy_into_request(self, request, changeProxy=False):
        ret=None
        if changeProxy==True or self.cur_proxy_used_cnt > self.MAX_PROXY_USED_CNT:
            ret = self.proxy_getter.get_a_proxy(True)
            self.cur_proxy_used_cnt = 0
            if changeProxy==True:
                print("Force to change proxy ",ret)
            else:
                print("Reach Max time,need to change proxy ",ret)
        else:
            ret = self.proxy_getter.get_a_proxy()
            print("Use old proxy ", ret)

        if ret != None:
            request.meta["proxy"] = ret
        else:
            if "proxy" in request.meta.keys():
                del request.meta["proxy"]

    def process_request(self, request, spider):
        pass

    def process_response(self, request, response, spider):
        return response

    def process_request1(self, request, spider):
        #随机拿一个
        # dont_redirect
        # dont_retry
        # handle_httpstatus_list
        # dont_merge_cookies(see
        # cookies
        # parameter
        # of
        # Request
        # constructor)
        # cookiejar
        # redirect_urls
        # bindaddress
        request.meta["dont_redirect"] = True
        # request.dont_filter = True
        self.set_proxy_into_request(request)
        #如果太少了，就补充
        if self.proxy_getter.get_valid_proxy_count() < self.MIN_PROXY_CNT_NEED_SUPLY:
            self.proxy_getter.add_new_proxys()
        # print("request meta",str(request.meta))

    def process_response1(self, request, response, spider):
        """
        检查response.status，如果返回失败那么就更换
        :param request: 
        :param response: 
        :param spider: 
        :return: 
        """
        if "proxy" in request.meta.keys():
            print("request use proxy",request.meta["proxy"])
        else:
            print("request not use a proxy")

        #这个是返回结果有问题，所以要重新组装req
        if response.status != 200 and \
            not (hasattr(spider, "website_possible_httpstatus_list") and response.status in spider.website_possible_httpstatus_list):
            newreq = request.copy()
            newreq.dont_filter = True

            if "proxy" in request.meta.keys():
                self.proxy_getter.set_proxy_invalid(request.meta["proxy"])
            self.set_proxy_into_request(newreq, changeProxy=True)
            return newreq
        else:
            return response

    def process_exception(self, request, exception, spider):
        # print("process_exception 111111111")
         if isinstance(exception, self.DONT_RETRY_ERRORS):
            # print("type = ",type(exception))
            newreq = request.copy()
            newreq.dont_filter = True
            if "proxy" in request.meta.keys():
                self.proxy_getter.set_proxy_invalid(request.meta["proxy"])
            self.set_proxy_into_request(newreq, changeProxy=True)
            # print("process_exception 222222222")
            return newreq
        # print("process_exception 33333333333333")