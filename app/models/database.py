import pymysql
from app.config import config, get_config_value


class Database:
    def __init__(self):
        # Support both config file and environment variables
        self.host = get_config_value("mysql", "host", "localhost")
        self.port = int(get_config_value("mysql", "port", "3306"))
        self.user = get_config_value("mysql", "username", "root")
        self.password = get_config_value("mysql", "password", "")
        self.db = get_config_value("mysql", "dbname", "news_db")
        self.__connect__()

    def __connect__(self):
        self.con = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
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

    def save_article(self, title: str, content: str) -> int:
        """
        Save article to database and return the article ID.

        Args:
            title: Article title
            content: Article content

        Returns:
            int: The ID of the inserted article
        """
        sql = "INSERT INTO news_articles (article_title, article_content) VALUES (%s, %s)"
        self.cur.execute(sql, (title, content))
        article_id = self.cur.lastrowid
        self.con.commit()
        self.__disconnect__()
        return article_id

    def save_vocabularies(self, article_id: int, vocabularies: list):
        """
        Save vocabularies to database.

        Args:
            article_id: The article ID to associate vocabularies with
            vocabularies: List of vocabulary dictionaries with keys: german, english, chinese, sentence
        """
        sql = """INSERT INTO article_vocabularies (article_id, german, english, chinese, sentence)
                 VALUES (%s, %s, %s, %s, %s)"""

        for vocab in vocabularies:
            self.cur.execute(sql, (
                article_id,
                vocab.get('german', ''),
                vocab.get('english', ''),
                vocab.get('chinese', ''),
                vocab.get('sentence', '')
            ))

        self.con.commit()
        self.__disconnect__()

    def get_article_by_title(self, title: str):
        """
        Get article and its vocabularies by title.

        Args:
            title: Article title

        Returns:
            dict: Article with vocabularies or None if not found
        """
        # Get article
        sql_article = "SELECT id, article_title, article_content, created_at FROM news_articles WHERE article_title = %s"
        self.cur.execute(sql_article, (title,))
        article = self.cur.fetchone()

        if not article:
            self.__disconnect__()
            return None

        # Get vocabularies
        sql_vocabs = """SELECT german, english, chinese, sentence
                        FROM article_vocabularies
                        WHERE article_id = %s"""
        self.cur.execute(sql_vocabs, (article['id'],))
        vocabularies = self.cur.fetchall()

        article['vocabularies'] = vocabularies
        self.__disconnect__()
        return article
