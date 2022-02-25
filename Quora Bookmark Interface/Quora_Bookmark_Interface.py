from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from urllib import parse
from mypy import mywebpy as mwp
from bs4 import BeautifulSoup
import sqlite3 as sql
import threading


class QuoraQuestion:
    def __init__(self):
        self.title = None
        self.link = None
        self.answer_author_profile_link = None
        self.answer_author = None
        self.tags = []

    def print_attrs(self):
        print("PERGUNTA: " + self.title)
        print("LINK: " + self.link)
        print("AUTOR: " + self.answer_author)
        print("PERFIL: " + self.answer_author_profile_link)
        print()


class PageHeightChanged:
    def __init__(self, page_height_0):
        self.page_height_0 = page_height_0

    def __call__(self, driver):
        if self.page_height_0 == driver.execute_script("return document.body.scrollHeight"):
            return False
        else:
            return True


class MyAutoBrowser:
    def __init__(self, *, headless=True, idiom='en'):
        self.options = Options()
        self.options.headless = headless
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.browser = webdriver.Chrome(options=self.options)
        self.page_load_timeout = 10
        self.bookmark_load_timeout = 10
        self.can_scroll = None

        self.quora_url = "https://pt.quora.com/"
        self.idiom = idiom
        if idiom == 'en':
            self.bookmark_url = "https://www.quora.com/bookmarks"
        elif idiom == 'pt':
            self.bookmark_url = "https://pt.quora.com/bookmarks"
        else:
            raise RuntimeError("Language parameter must be 'en' or 'pt'")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def quit(self):
        self.browser.quit()

    def is_browser_open(self):
        try:
            aux = self.browser.title
            return True
        except:
            return False

    def access_quora_login_page(self):
        try:
            self.browser.get(self.quora_url)
        except:
            raise RuntimeError("Error in entering Quora's login page")

    def login(self, quora_email, quora_password):
        try:
            # login_class = self.browser.find_element_by_class_name("login")
            # email_field = login_class.find_element_by_name("email")
            # password_field = login_class.find_element_by_name("password")

            email_field = self.browser.find_element_by_name("email")
            password_field = self.browser.find_element_by_name("password")

            email_field.send_keys(quora_email)
            password_field.send_keys(quora_password)
            sleep(1)
            password_field.send_keys(Keys.ENTER)
            WebDriverWait(self.browser, self.page_load_timeout).until(EC.title_contains("Quora"))

        except:
            raise RuntimeError("Error in logging in on Quora")

    def access_bookmark(self):
        try:
            # Não sei se esse sleep era para ser necessário, mas sem ele o browser não está executando
            # o método get (teoricamente não seria necessário esperar para executar uma ação no browser
            # pois o método get anterior ja espera a página estar carregada para retornar)
            sleep(2)
            self.browser.get(self.bookmark_url)
            if self.idiom == 'en':
                WebDriverWait(self.browser, self.page_load_timeout).until(EC.title_contains("Bookmarks"))
            elif self.idiom == 'pt':
                WebDriverWait(self.browser, self.page_load_timeout).until(EC.title_contains("Favoritos"))
        except:
            raise RuntimeError("Error in entering Quora's bookmark page")

    def get_page_height(self):
        page_height = self.browser.execute_script("return document.body.scrollHeight")
        return page_height

    def scroll_to_bottom_of_page(self):
        aux = self.browser.find_element_by_tag_name("html")
        aux.send_keys(Keys.END)

    def scroll_down_until_time_out(self):
        can_scroll = True
        while can_scroll and self.is_browser_open():
            try:
                page_height = self.get_page_height()
                self.scroll_to_bottom_of_page()
                can_scroll = WebDriverWait(self.browser, self.bookmark_load_timeout).until(
                    PageHeightChanged(page_height))
                sleep(1)
            except:
                can_scroll = False

        if not self.is_browser_open():
            self.quit()

    def can_scroll_until_stop(self):
        user_input = input()
        if user_input == "stop":
            self.can_scroll = False

    def scroll_down(self):
        self.can_scroll = True

        stop_scrolling_thread = threading.Thread(target=self.can_scroll_until_stop)
        stop_scrolling_thread.start()

        while True:
            if self.can_scroll:
                self.scroll_to_bottom_of_page()
                sleep(1)
            else:
                while True:
                    user_input = input()
                    if user_input == "start":
                        self.can_scroll = True
                        stop_scrolling_thread.join()
                        stop_scrolling_thread = threading.Thread(target=self.can_scroll_until_stop)
                        stop_scrolling_thread.start()
                        break

    def expose_space_question_links(self):
        space_questions_super_tags_list = self.browser.find_elements_by_class_name("ejgusd")
        for e in space_questions_super_tags_list:
            try:
                e.click()
            except:
                pass

    def expose_space_question_links_only(self):
        questions_super_tags_list = self.browser.find_elements_by_class_name("q-box qu-pt--medium qu-pb--tiny")
        for e in questions_super_tags_list:
            is_space_question = True
            try:
                e.find_elements_by_class_name("spacing_log_answer_header")
                is_space_question = False
            except:
                is_space_question = True
            if is_space_question:
                questions_body_list = e.find_elements_by_class_name("ejgusd")
                for i in questions_body_list:
                    i.click()

    def get_page_questions_links(self):
        questions_titles_super_tags_list = self.browser.find_elements_by_class_name("jPnwvF")
        questions_titles_tags_list = []
        questions_titles_links_list = []

        for e in questions_titles_super_tags_list:
            question_title_tag = e.find_element_by_tag_name("a")
            questions_titles_tags_list.append(question_title_tag)
        for q in questions_titles_tags_list:
            question_link = q.get_attribute("href")
            if self.idiom == 'pt':
                question_link = parse.unquote(question_link)
            questions_titles_links_list.append(question_link)
        return questions_titles_links_list

    def get_questions_titles_list_by_link_list(self, links_list):
        questions_titles_list = []
        url_len_to_cut = 0
        if self.idiom == 'en':
            url_len_to_cut = 22
        elif self.idiom == 'pt':
            url_len_to_cut = 21
        for link in links_list:
            question_title = link[url_len_to_cut:]
            questions_titles_list.append(question_title)
        return questions_titles_list

    def get_page_answers_author_link(self):
        # A atribuição abaixo era:
        # answers_authors_super_tags_list = self.browser.find_elements_by_class_name("gqbGaA")
        # e foi substituida pela atual devido ao que deve ter sido uma atualização no site
        answers_authors_super_tags_list = self.browser.find_elements_by_class_name("spacing_log_answer_header")
        answers_authors_tags_list = []
        answers_authors_links_list = []
        for e in answers_authors_super_tags_list:
            answers_author_tag = e.find_element_by_tag_name("a")
            answers_authors_tags_list.append(answers_author_tag)
        for q in answers_authors_tags_list:
            answers_author_link = q.get_attribute("href")
            if self.idiom == 'pt':
                answers_author_link = parse.unquote(answers_author_link)
            answers_authors_links_list.append(answers_author_link)
        return answers_authors_links_list

    def get_answer_author_list_by_link_list(self, links_list):
        answers_authors_list = []
        url_len_to_cut = 0
        if self.idiom == 'en':
            url_len_to_cut = 30
        elif self.idiom == 'pt':
            url_len_to_cut = 29
        for link in links_list:
            answer_author = link[url_len_to_cut:]
            answers_authors_list.append(answer_author)
        return answers_authors_list

    def get_page_question_tags_by_question_link_list(self, questions_link_list):
        questions_topics_list = []
        for question_link in questions_link_list:
            question_topics_list = []
            raw_html = mwp.get_content(question_link)
            html = BeautifulSoup(raw_html, 'html.parser')

            if self.idiom == 'en':
                topic_tags = html.find_all('a', class_="topic_name")
                for topic_tag in topic_tags:
                    link = topic_tag['href']
                    topic = link[7:]
                    question_topics_list.append(topic)

            elif self.idiom == 'pt':
                a_with_links = []
                a_tags = html.find_all('a')
                for a in a_tags:
                    if a.has_attr('href'):
                        a_with_links.append(a)
                for a in a_with_links:
                    a_link = a['href']
                    if a_link.find("topic") != -1:
                        a_link = parse.unquote(a_link)
                        a_link = a_link[27:]
                        question_topics_list.append(a_link)
            questions_topics_list.append(question_topics_list)

        return questions_topics_list

    def build_quora_question_object_list(self, limit_question_title=False):
        question_list = []
        questions_gathered = 0
        limit_question_found = False
        load_not_timed_out = True
        page_question_links = None
        page_question_titles = None
        page_author_profile_links = None
        page_author_names = None
        while not limit_question_found and load_not_timed_out:
            page_height = self.get_page_height()
            page_question_links = self.get_page_questions_links()
            page_question_titles = self.get_questions_titles_list_by_link_list(page_question_links)
            page_author_profile_links = self.get_page_answers_author_link()
            page_author_names = self.get_answer_author_list_by_link_list(page_author_profile_links)

            if limit_question_title is not False:
                try:
                    limit_question_index = page_question_titles.index(limit_question_title)
                    limit_question_found = True
                    page_question_links = page_question_links[:limit_question_index]
                    page_question_titles = page_question_titles[:limit_question_index]
                    page_author_profile_links = page_author_profile_links[:limit_question_index]
                    page_author_names = page_author_names[:limit_question_index]
                except ValueError:
                    limit_question_found = False

            questions_gathered = len(page_question_links)
            if not limit_question_found:
                self.scroll_to_bottom_of_page()
                try:
                    load_not_timed_out = WebDriverWait(self.browser, self.bookmark_load_timeout).until(
                        PageHeightChanged(page_height))
                except:
                    load_not_timed_out = False

        print("TITLES: "+str(len(page_question_titles)))
        print("LINKS: " + str(len(page_question_links)))
        print("!!PROFILE LINKS: " + str(len(page_author_profile_links)))
        print("AUTHOR NAMES: " + str(len(page_author_names)))
        for i in range(questions_gathered):
            question = QuoraQuestion()
            question.title = page_question_titles[i]
            question.link = page_question_links[i]
            question.answer_author_profile_link = page_author_profile_links[i]
            question.answer_author = page_author_names[i]
            question_list.append(question)
        return question_list


class DataBaseManager:
    def __init__(self):
        self.database = sql.connect("Quora_Bookmark_Interface.db")
        self.cursor = self.database.cursor()

    @staticmethod
    def quora_question_list_to_tuple_list(quora_question_list):
        tuple_list = []
        for question in quora_question_list:
            title, author, link, author_link = (question.title, question.answer_author,
                                                question.link, question.answer_author_profile_link)
            tuple_list.append((title, author, link, author_link))
        return tuple_list

    def create_bookmark_table(self):
        create_question_table = """
        CREATE TABLE IF NOT EXISTS bookmark(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            link TEXT NOT NULL,
            author_profile_link TEXT,
            tags NULL
        );
        """
        self.cursor.execute(create_question_table)

    def insert_bookmarks_in_table(self, quora_questions_list):
        insert_bookmark = """
        INSERT INTO
            bookmark (title, author, link, author_profile_link)
        VALUES
            (?,?,?,?);
        """
        questions_list = self.quora_question_list_to_tuple_list(quora_questions_list)
        self.cursor.executemany(insert_bookmark, questions_list)
        self.database.commit()

    def close(self):
        self.database.close()


if __name__ == "__main__":
    with MyAutoBrowser(headless=False, idiom='pt') as browser:
        browser.bookmark_load_timeout = 10
        browser.access_quora_login_page()
        browser.login("Email", "Password")
        browser.access_bookmark()

        question_list = browser.build_quora_question_object_list()
        for question in question_list:
            question.print_attrs()

        data_base_manager = DataBaseManager()
        data_base_manager.create_bookmark_table()
        data_base_manager.insert_bookmarks_in_table(question_list)
        data_base_manager.close()

        wait = input()
