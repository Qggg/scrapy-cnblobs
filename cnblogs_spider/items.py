# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CnblogsSpiderArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ArticleUrl = scrapy.Field()
    AuthorAccountName = scrapy.Field()
    ArticleContent = scrapy.Field()
    pass


class CnblogsSpiderAuthorItem(scrapy.Item):
    # 昵称
    AuthorNickName = scrapy.Field()
    # 真实姓名
    AuthorRealName = scrapy.Field()
    # 账户名
    AuthorAccountName = scrapy.Field()
    # 性别
    AuthorSexual = scrapy.Field()
    # 生日
    AuthorBrithday = scrapy.Field()
    # 家乡
    AuthorHometown = scrapy.Field()
    # 常驻地址
    AuthorResidentialAddress = scrapy.Field()
    # 婚姻
    AuthorMarryState = scrapy.Field()
    # 职位
    AuthorJob = scrapy.Field()
    # 工作状态
    AuthorJobState = scrapy.Field()
    # 感兴趣技术
    AuthorTechInteresing = scrapy.Field()
    # 最近目标
    AuthorResentTarget= scrapy.Field()
    # 座右铭
    AuthorMotto = scrapy.Field()
    # 自我介绍
    AuthorIntroduce = scrapy.Field()
    # 园龄
    AuthorJoinBlobDate = scrapy.Field()
    # 链接
    AuthorBlobUrl = scrapy.Field()
    # 关注的人
    Followees = scrapy.Field()
    # 粉丝
    Followers = scrapy.Field()
    # 单位
    AuthorCorporation = scrapy.Field()
    # QQ
    AuthorQQNo = scrapy.Field()
    # 关注的人
    AuthorFollowee = scrapy.Field()
    # 粉丝
    AuthorFollower = scrapy.Field()
    # 是否存在头像
    AuthorAvatarExist = scrapy.Field()


class CnblogsSpiderAuthorAvatarItem(scrapy.Item):
    # 账户名
    AuthorAccountName = scrapy.Field()
    # 用户图片url
    AuthorPicUrl = scrapy.Field()
    # 用户图片本地绝对路径
    AuthorPicLocalPath = scrapy.Field()
