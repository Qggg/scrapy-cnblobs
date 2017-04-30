#!/usr/bin/python3

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from cnblogs_spider.items import CnblogsSpiderArticleItem,CnblogsSpiderAuthorItem,CnblogsSpiderAuthorAvatarItem
from cnblogs_spider.mongodb_pipelines.mongodb_operate import mongodb_operate
from scrapy.exceptions import DropItem

class Mongodb_Pipelines(object):
    #这个是个普通的pipeline,不支持下载用户头像的
    def process_item(self, item, spider):
        if isinstance(item,  CnblogsSpiderAuthorItem):
            #组装一个DICT
            # print("keys={}".format(item.keys()))
            # print("type=",type(item.items()))
            auser = {}
            for akey in item.keys():
                auser[akey] = item[akey]
            print("auser=",auser)
            if mongodb_operate.IsAuthorAccountNameExist(item["AuthorAccountName"]) == 0:
                mongodb_operate.InsertAccount(auser)
            raise DropItem("在第一个pipeline终止")
        else:
            return item

class Images_Pipelines(ImagesPipeline):
    #这个是imagepipeline
    def get_media_requests(self, item, info):
        if isinstance(item, CnblogsSpiderAuthorAvatarItem):
            picurl = 'http:'+ item['AuthorPicUrl']
            # print('picurl=',picurl)
            yield Request(picurl)
        else:
            return item

    def item_completed(self, results, item, info):
        if isinstance(item, CnblogsSpiderAuthorAvatarItem):
            item['AuthorPicLocalPath'] = [x['path'] for ok, x in results if ok]
            if len(item['AuthorPicLocalPath']) == 0:
                print("用户{}的头像下载失败，地址：{}".format(item['AuthorAccountName'], item['AuthorPicUrl']))
            else:
                #写入数据库
                print("用户{}的头像下载成功，地址：{}".format(item['AuthorAccountName'], item['AuthorPicUrl']))
                auser = {}
                for akey in item.keys():
                    auser[akey] = item[akey]
                mongodb_operate.InsertAccountAvatar(auser)
            raise DropItem("在第二个pipeline终止")
        else:
            return item