# -*- coding: utf-8 -*-
import logging
# Define your item pipelines here
from twisted.enterprise import adbapi
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from doubancomment.items import DoubancommentItem


class DoubancommentPipeline(object):


    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''init connection string'''
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
            cp_reconnect=True)
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):

        query = self.dbpool.runInteraction(self._conditional_insert, item,spider)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item


    def _conditional_insert(self,conn,item,spider):

        print('Pipeline is starting...')
        conn.execute("""replace into douban_comment 
               (title,author,comment_time,grade,
               votes,movieId,authorId,comment,ctime)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                     (
                     item['title'], item['author'], item['comment_time'], item['grade'], item['votes'], item['movieId'],
                     item['authorId'], item['comment'],item['ctime']))
        #logging.info("Item updated in db: %s %r" % (item['title'], item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)
