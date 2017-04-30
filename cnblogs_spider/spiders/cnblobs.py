import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy import FormRequest
from cnblogs_spider.items import CnblogsSpiderArticleItem,CnblogsSpiderAuthorItem,CnblogsSpiderAuthorAvatarItem
from pyquery import PyQuery as pq
import re
import json
from urllib.request import urlretrieve
from cnblogs_spider.spiders.write_txt_into_file import WriteIntoFile
import math
from cnblogs_spider.mongodb_pipelines.mongodb_operate import mongodb_operate

class cnblobsSpider(scrapy.Spider):
    name = 'cnblogs_spider'
    allowed_domains = ['cnblogs.com',
                       'home.cnblogs.com']
    # start_urls = ['https://passport.cnblogs.com/user/signin']
    ahearder = {"Host": "passport.cnblogs.com",
                "Connection": "keep-alive",
                "Origin": "https://passport.cnblogs.com",
                "VerificationToken": "",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://passport.cnblogs.com/user/signin",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.8",
                # "Cookie": acookies,
                }
    MAX_ACCOUNT_CNT_PER_PAGE = 45
    website_possible_httpstatus_list = [404,]

    def start_requests(self):
        loginurl = 'https://passport.cnblogs.com/user/signin'
        return [Request(loginurl, callback=self.post_login, meta={'download_timeout': 5})]


    def post_login(self, response):
        verificationtoken = re.search("'VerificationToken': '(.+)'", response.text).group(1)
        self.ahearder['VerificationToken'] = verificationtoken
        #这是我的用户名密码。
        imgdata={'captchaId':"LoginCaptcha",
                    'captchaInstanceId':"970a47806f08426eb80a2ccfc4525f90",
                    'captchaUserInput':"NYB9"}
        formdata1={"input1":"YTiBJFqCFgdBnM8P65yd7YL+OYPzLV8ZClgmZMK/v7Llp9XZJTLiDD/fIlXOgwMe5UATrJ0mOgOtw/36p3RfGn34PaQB1aRmCGT0CRJniwTFyhf7SsJ9sPFEB477hDN5tQ3inTp+cVSwWf9gMkqE2j4hDLmMg61sF+RfUjT6WT0=",
                    "input2":"jlGnwhRHk1rOcHYoYv+f4qfvoe7xuZYJ02WbiogigR5LPeY5u3M+8bp66nf1Ooa/TsgaolDSLJ5UzsIlIv9qVI6p0jyMjMyzIzAAM2rzNCqtN0jx4zfeGLBFf/L3sBxBCJRA26vdgLXP2XVyTgsR2Y+YDSMPNpnzAAkfBj5dIxQ=",
                    "remember":"False"}
        formdata={"input1":"TrD/XJDeb3l+eaN4g1tHnhuxbUe6TPJrTLU0YGuA/HKbLvMnyHjFZWaLGkQfTSASVVLdeVHfanjM4TXXlor8GCnLk48/oxq00A+fFFi46OlMsCdLvWY7Pyid5eLo8uxMFt9hurRaFOi1zOMKBzLRfmg3n/LeGff0pvJOW/D4gTU=",
                    "input2":"hL2+KFDzjTUiu3FFI+PlDD/TNy3MlEda01NRu4dQgek1+NsBOzm1SeA8urTvK688wanTE3r1JGJNjPljzZuhyD03NCSmdNo5Z/nyfyoQxt0v7z2UrTEWDG69GSyxxwKUFqrGntT16HpvUNHsS/qZgVnOAOUB/D5SYm8QxJZE724=",
                  "remember":"False"}
        imgurl_sel=response.xpath('//*[@id="LoginCaptcha_CaptchaImage"]/@src')

        if len(imgurl_sel)>0:
            #取出链接地址
            imgurl = imgurl_sel.extract()[0]
            #取出ID
            # print("srccccc=", response.xpath('//*[@id="LoginCaptcha_CaptchaImage"]').extract())
            imgdata['captchaInstanceId'] = re.search(r'&t=(\w+)',imgurl).group(1)
            print("imgurl=", imgurl)
            print("captchaInstanceId=", imgdata['captchaInstanceId'] )
            #把链接地址保存到图片
            urlretrieve('https://passport.cnblogs.com'+imgurl, filename="c:\\renzhengma.jpg")
            imgcode = input('>>>>>')
            imgdata['captchaUserInput'] = imgcode
            formdata.update(imgdata)

        print("logindata = ", formdata)
        return [FormRequest.from_response(response, body=json.dumps(formdata), method ='POST',headers=self.ahearder, callback=self.after_login)]


    def post_login1(self, response):
        verificationtoken = re.search("'VerificationToken': '(.+)'", response.text).group(1)
        self.ahearder['VerificationToken'] = verificationtoken

        mycookie = {'UM_distinctid' : '15ac7afa5693a1-0f8c8acda74df2-33485362-1aeaa0-15ac7afa56a389',
                    '.CNBlogsCookie' : 'E2D611DBB3DF01083441C9131DCBDE78230C699B8AECC2954BC399CB6C22F4092A3755DD6A3676F6DB6FF29C0B24467D605207E58ECE492B8DEACCC0D988FDDABB06341BD80A693F8B39C8696AA28A612BA4D195',
                    '.Cnblogs.AspNetCore.Cookies' : 'CfDJ8Mmb5OBERd5FqtiQlKZZIG6b5zM4nPEN4vPt0BDk9wbX5X1WJY0VkAM-h_5_KD3BoMW_TDnopc7qdDaR8cwbqE-XcLGFws_FOzp2rsEJO0ykYzzAaf3-8omeLgemcuEr4wcZgv7L0wLAibMF2QxlftL1vRKpUM8WtAYKQDTHPn1PCdS8ECZJs8dPLxN1A6C4vydU-LyNX3LRBq2ioyLIJ9xZoQAHrP8MnXJ_WbXAil02FDhaHGps8xlLPV1ODlKQsIlaCt_mjc2NN-zkcbzqcEBu3sHbXVygAbumo4HUqUq-',
                    '_ga' : 'GA1.2.1353711182.1488298292',
                    '_gid' : 'GA1.2.275945890.1493529025',
                    '_gat' : '1',}

        return [Request(url="https://home.cnblogs.com/u/zhaoforyou/",headers=self.ahearder, cookies=mycookie, callback=self.after_login)]
    # def parse_start_url(self, response):
    #     verificationtoken = re.search("'VerificationToken': '(.+)'", response.text).group(1)
    #     self.ahearder['VerificationToken'] = verificationtoken
    #     #这是我的用户名密码。
    #     formdata={"input1":"YTiBJFqCFgdBnM8P65yd7YL+OYPzLV8ZClgmZMK/v7Llp9XZJTLiDD/fIlXOgwMe5UATrJ0mOgOtw/36p3RfGn34PaQB1aRmCGT0CRJniwTFyhf7SsJ9sPFEB477hDN5tQ3inTp+cVSwWf9gMkqE2j4hDLmMg61sF+RfUjT6WT0=",
    #                 "input2":"jlGnwhRHk1rOcHYoYv+f4qfvoe7xuZYJ02WbiogigR5LPeY5u3M+8bp66nf1Ooa/TsgaolDSLJ5UzsIlIv9qVI6p0jyMjMyzIzAAM2rzNCqtN0jx4zfeGLBFf/L3sBxBCJRA26vdgLXP2XVyTgsR2Y+YDSMPNpnzAAkfBj5dIxQ=",
    #                 "remember":"False"}
    #     return [FormRequest.from_response(response, body=json.dumps(formdata), method ='POST',headers=self.ahearder, callback=self.after_login)]
        #return [Request(url="https://passport.cnblogs.com/user/signin", body =json.dumps(formdata), method ='POST',headers=self.ahearder, callback=self.after_login)]

    def after_login(self, response):
        retdict = json.loads(response.text)
        #print("retdict=",retdict)
        if retdict["success"] == True:
            print("login succeed!")
            yield Request("https://home.cnblogs.com/u/sheng-jie",
                           headers=self.ahearder,
                           callback=self.parse_Author,
                            meta={'download_timeout': 5})
        else:
            print("login fail!")

    def parse_Article(self, response):
        print("article",response.url)
        aItem = CnblogsSpiderArticleItem()

        doc = pq(response.text)
        bodydoc = doc.find("div[id='cnblogs_post_body']")
        for it in bodydoc.items():
            contents = ""
            if len(it("p"))>0:
                contents += it("p").text()
            if len(it("span/text()")) > 0:
                contents += it("span/text()").text()
            if len(it("img")) > 0:
                contents += it("img").attr("src")
        #for idx in range(len(bodydoc.find())):

        # aItem["ArticleContent"] = contents;
        # aItem["ArticleUrl"]      = response.url;
        # aItem["AuthorAccountName"]  = response.url.split('/')[-3];
        yield aItem

    def parse_Author(self, response):
        # print("parse_Author",response.url)
        #print("response.text=", response.text)
        #print("author detail=",response.xpath('//*[@id="user_profile"]/li'))
        aitem = CnblogsSpiderAuthorItem()

        #print("text=",response.text)
        detaillist = response.xpath('//*[@id="user_profile"]/li')
        aitem["AuthorAccountName"] = response.url.split('/')[-1]
        aitem["AuthorAvatarExist"] = 0
        #如果不是默认的头像那么保存
        avatarUrl = response.xpath('//*[@id="user_profile_block"]//img/@src').extract()[0]
        if avatarUrl.find("avatar/simple_avatar.gif") == -1:
            aitem["AuthorAvatarExist"] = 1
            avatarItem = CnblogsSpiderAuthorAvatarItem()
            avatarItem["AuthorAccountName"] = aitem["AuthorAccountName"]
            avatarItem["AuthorPicUrl"] = avatarUrl
            # print("avatarUrl=",avatarUrl)
            yield avatarItem
        print("用户{}的头像{}存在".format(aitem["AuthorAccountName"],"不" if aitem["AuthorAvatarExist"]==0 else ""))
        #print("size = ",len(detaillist))
        for adetail in detaillist:
            alist = adetail.xpath("span")
            # print("alist len=",len(alist))
            # print("string=",adetail.extract())
            # print("text=", adetail.xpath("span/text()").extract())
            spannum = len(adetail.xpath("*/text()"))
            if spannum < 1:
                continue
            title = adetail.xpath("*/text()").extract()[0]
            if spannum == 2:
                value = adetail.xpath("*/text()").extract()[1]
            else:
                value = "" if len(adetail.xpath("text()").extract())==0 else adetail.xpath("text()").extract()[0]
            # print("title={},value={}".format(title, value))
            if title == "性别：":
                aitem["AuthorSexual"] = value
            elif title == "出生日期：":
                aitem["AuthorBrithday"] = value
            elif title == "家乡：":
                aitem["AuthorHometown"] = value
            elif title == "现居住地：":
                aitem["AuthorResidentialAddress"] = value
            elif title == "婚姻：":
                aitem["AuthorMarryState"] = value
            elif title == "职位：":
                aitem["AuthorJob"] = value
            elif title == "工作状态：":
                aitem["AuthorJobState"] = value
            elif title == "园龄：":
                aitem["AuthorJoinBlobDate"] = re.search(r'：(.+)', adetail.xpath("span/@title").extract()[0]).group(1)
            elif title == "博客：":
                aitem["AuthorBlobUrl"] = value
            elif title == "出生日期：":
                aitem["AuthorBrithday"] = value
            elif title == "感兴趣的技术：":
                aitem["AuthorTechInteresing"] = value
            elif title == "座右铭：":
                aitem["AuthorMotto"] = value
            elif title == "自我介绍：":
                aitem["AuthorIntroduce"] = value
            elif title == "单位：":
                aitem["AuthorCorporation"] = value
            elif title == "姓名：":
                aitem["AuthorRealName"] = value
            elif title == "QQ：":
                aitem["AuthorQQNo"] = value
        #一旦我们获取了一个人的，我们就发散，获取他所有的follower和follwee，这里组装下请求
        #https://home.cnblogs.com/u/sheng-jie/followers/
        yield aitem
        #组装request
        # WriteIntoFile.write_a_file("c://x.html", bytes(response.text, 'utf-8'))

        a_followers_cnt_str = response.xpath('//a[@id="follower_count"]/text()').extract()[0]
        a_followees_cnt_str = response.xpath('//a[@id="following_count"]/text()').extract()[0]
        a_followers_cnt = int(a_followers_cnt_str)
        a_followees_cnt = int(a_followees_cnt_str)
        tempstr = response.xpath("//head/script/text()").extract()[0]
        userid = re.search(r'currentUserId = "(.+)"', tempstr).group(1)
        followeesUrl = "https://home.cnblogs.com/u/{}/followees/".format(aitem["AuthorAccountName"])
        followersUrl = "https://home.cnblogs.com/u/{}/followers/".format(aitem["AuthorAccountName"])
        request_url = 'https://home.cnblogs.com/relation_users'

        # print("a_followees_cnt={},a_followees_cnt={}".format(a_followers_cnt, a_followees_cnt))
        myheader = self.ahearder.copy()

        pageCnt = math.ceil(a_followers_cnt/float(self.MAX_ACCOUNT_CNT_PER_PAGE))
        for pageno in range(1, pageCnt):
            formdata = {"uid": userid, "groupId": "00000000-0000-0000-0000-000000000000", "page": pageno,"isFollowes": 'false'}
            myheader['Referer'] = followersUrl
            yield Request(url=request_url,
                          method='post',
                          headers=self.ahearder,
                          body =json.dumps(formdata),
                          callback=self.parse_follow_page,
                          meta={'download_timeout': 5})

        pageCnt = math.ceil(a_followees_cnt/float(self.MAX_ACCOUNT_CNT_PER_PAGE))
        for pageno in range(1, pageCnt):
            formdata = {"uid": userid, "groupId": "00000000-0000-0000-0000-000000000000", "page": pageno,"isFollowes": 'true'}
            myheader['Referer'] = followeesUrl
            yield Request(url=request_url,
                          method='post',
                          headers=self.ahearder,
                          body =json.dumps(formdata),
                          callback=self.parse_follow_page,
                          meta={'download_timeout': 5})

    def parse_follow_page(self, response):
        anode = json.loads(response.text)
        for auser in anode["Users"]:
            #获取全部用户名，组装链接
            #去重，如果用户名存在，就不去Request了
            if mongodb_operate.IsAuthorAccountNameExist(auser["Alias"]) == 1:
                print("用户帐户{}已经爬取过了".format(auser["Alias"]))
            else:
                print("用户帐户{}开始抓取...".format(auser["Alias"]))
                yield Request("https://home.cnblogs.com/u/{}".format(auser["Alias"]),
                               headers=self.ahearder,
                               callback=self.parse_Author,
                                meta={'download_timeout': 5})




