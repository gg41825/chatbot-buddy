import pymysql
from app import config


class Database:
    def __init__(self):
        self.host = config.MYSQL_HOST
        self.port = int(config.MYSQL_PORT)
        self.user = config.MYSQL_USERNAME
        self.password = config.MYSQL_PASSWORD
        self.charset = "utf8mb4",
        self.db = config.MYSQL_DBNAME
        self.__connect__()

    def __connect__(self):
      self.con = pymysql.Connection(
          host=self.host,
          user=self.user,
          password=self.password,
          database=self.db,
          cursorclass=pymysql.cursors.DictCursor
      )
      self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetchone(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchone()
        self.__disconnect__()
        return result

    def fetchall(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def execute(self, sql):
        self.cur.execute(sql)

    def commit(self):
        self.con.commit()
        self.__disconnect__()

    def save_vocabularies(self, vocabularies: list):
        """
        Save vocabularies to database.

        Args:
            article_id: The article ID to associate vocabularies with
            vocabularies: List of vocabulary dictionaries with keys: german, english, chinese, sentence
        """
        sql = """INSERT INTO vocabularies (german, english, chinese, sentence)
                 VALUES (%s, %s, %s, %s)"""

        for vocab in vocabularies:
            self.cur.execute(sql, (
                vocab.get('german', ''),
                vocab.get('english', ''),
                vocab.get('chinese', ''),
                vocab.get('sentence', '')
            ))

        self.con.commit()
        self.__disconnect__()