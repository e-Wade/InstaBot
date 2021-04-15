import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from data import users_settings_dict, direct_users_list
from selenium.webdriver.chrome.options import Options
import time
import random
import os
import json


# создаем класс для лаконичности
class InstagramBot():

    def __init__(self, username, password):

        self.username = username
        self.password = password
        options = Options()
        # options.add_argument(f'--window-size={window_size}')
        # options.add_argument('--headless')
        self.browser = webdriver.Chrome('../chromedriver/chromedriver', options=options)

    # метод для закрытия браузера
    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    def login(self):

        browser = self.browser
        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(10)

    def like_photo_by_hashtag(self, hashtag):

        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(5)

        # иммитируем скролл страницы
        for i in range(1, 4):
            browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.randrange(3, 5))

        # соберем ссылки на все посты со страницы, чтобы мы могли по ним переходить
        hrefs = browser.find_elements_by_tag_name('a')

        # сохряняем посты в список, если содержит /p/
        posts_urls = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

        # проставляем лайки каждому посту
        for url in posts_urls:
            try:
                browser.get(url)  # переходим на пост
                time.sleep(3)  # задержка для загрузки страницы

                # ссылка на кнопку
                like_button = browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button').click()

                # чтобы не палится и проставлять лайки раз в 80-100 сек
                time.sleep(random.randrange(80, 100))
            except Exception as ex:
                print(ex)
                self.close_browser()

    # проверяем по xpath существует ли элемент на странице
    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    # ставим лайк на пост по прямой ссылке
    def put_exactly_like(self, userpost):

        browser = self.browser
        browser.get(userpost)
        time.sleep(2)

        wrong_userpage = '/html/body/div[1]/section/main/div/h2'
        if self.xpath_exists(wrong_userpage):
            print('Такого поста не существует, проверьте URL')
            self.close_browser()
        else:
            print('Пост успешно найден, ставим лайк!')
            time.sleep(2)

            like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button'
            browser.find_element_by_xpath(like_button).click()
            time.sleep(2)

            print(f'Лайк на пост: {userpost} поставлен!')
            self.close_browser()

    # метод собирает ссылки на все посты юзера
    def get_all_posts_urls(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)

        wrong_userpage = '/html/body/div[1]/section/main/div/h2'
        if self.xpath_exists(wrong_userpage):
            print('Такого пользователя не существует, проверьте URL')
            self.close_browser()
        else:
            print('Пользователь успешно найден, ставим лайки!')
            time.sleep(2)

            # находим колво постов юзера и опредяляем, сколько нужно сделать прокруток
            amount_of_posts = '/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span'
            posts_count = int(browser.find_element_by_xpath(amount_of_posts).text)
            loops_count = int(posts_count / 12)
            print(loops_count)

            # собераем ссылки в список
            posts_urls = []
            for i in range(loops_count):
                hrefs = browser.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(2, 4))
                print(f'Итерация #{i}')

            # определяем имя юзера
            file_name = userpage.split('/')[-2]

            # сохраняем ссылки в текстовый файл
            with open(f'{file_name}.txt', 'a') as file:
                for post_url in posts_urls:
                    file.write(post_url + '\n')

            # удаляем дубликаты ссылок
            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            # сохраняем уникальный список ссылок в новый файл
            with open(f'{file_name}_set.txt', 'a') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')

    # ставим лайки по ссылке на аккаунт пользователя
    def put_many_likes(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        # открываем файл с ссылками
        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            # ставим лайки на каждый пост
            for post_url in urls_list[0:6]:
                try:
                    browser.get(post_url)
                    time.sleep(2)

                    like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button'
                    browser.find_element_by_xpath(like_button).click()
                    # time.sleep(random.randrange(80, 100))
                    time.sleep(2)

                    print(f'Лайк на пост: {post_url} успешно поставлен!')
                except Exception as ex:
                    print(ex)
                    self.close_browser()

        self.close_browser()

    # скачиваем контент со страницы пользователя
    def download_userpage_content(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        # создаем папку с именем пользователя для чистоты проекта
        if os.path.exists(f'{file_name}'):
            print('Папка уже существует!')
        else:
            os.mkdir(file_name)

        img_and_video_src_urls = []
        # открываем файл с ссылками
        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            # ставим лайки на каждый пост
            for post_url in urls_list:
                try:
                    browser.get(post_url)
                    time.sleep(4)

                    img_src = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img'
                    video_src = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/div/div/video'

                    post_id = post_url.split('/')[-2]

                    if self.xpath_exists(img_src):
                        img_src_url = browser.find_element_by_xpath(img_src).get_attribute('src')
                        img_and_video_src_urls.append(img_src_url)

                        # сохраняем изображение
                        get_img = requests.get(img_src_url)
                        with open(f'{file_name}/{file_name}_{post_id}_img.jpg', 'wb') as img_file:
                            img_file.write(get_img.content)

                    elif self.xpath_exists(video_src):
                        video_src_url = browser.find_element_by_xpath(video_src).get_attribute('src')
                        img_and_video_src_urls.append(video_src_url)

                        # сохраняем видео
                        get_video = requests.get(video_src_url, stream=True)
                        with open(f'{file_name}/{file_name}_{post_id}_video.mp4', 'wb') as video_file:
                            for chunk in get_video.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    video_file.write(chunk)
                    else:
                        print('Упс! Что-то пошло не так')
                        img_and_video_src_urls.append(f'{post_url}, нет ссылки')
                    print(f'Контент из поста {post_url} успешно скачан!')
                except Exception as ex:
                    print(ex)
                    # self.close_browser()
                    # break

            self.close_browser()

        with open(f'{file_name}/{file_name}_img_and_video_src_urls.txt', 'a') as file:
            for i in img_and_video_src_urls:
                file.write(i + '\n')

    # метод подписки на всех подписчиков переданного аккаунта
    def get_all_followers(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split('/')[-2]

        # создаем папку с именем пользователя для чистоты проекта
        if os.path.exists(f'{file_name}'):
            print(f'Папка {file_name} уже существует!')
        else:
            print(f'Создаем папку юзера {file_name}.')
            os.mkdir(file_name)

        wrong_userpage = '/html/body/div[1]/section/main/div/h2'
        if self.xpath_exists(wrong_userpage):
            print(f'Пользователя {file_name} не существует, проверьте URL')
            self.close_browser()
        else:
            print(f'Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!')
            time.sleep(2)

            # определяем колво подписчиков
            # followers_count = followers_button.text
            # followers_count = int(''.join(followers_count.split()[:-1]))
            followers_span = '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span'
            followers_count = browser.find_element_by_xpath(followers_span).get_attribute('title')
            followers_count = int(followers_count.replace(' ', ''))
            print(f'Колличество подписчиков: {followers_count}')
            time.sleep(2)

            # определяем колво скроллов
            loops_count = int(followers_count / 12 / 10)
            print(f'Число итераций: {loops_count}')
            time.sleep(4)

            # открываем окно с  подписчиками и выбираем его ul со списком подписчиков
            followers_button = browser.find_element_by_xpath(
                '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a')
            followers_button.click()
            time.sleep(4)
            followers_ul = browser.find_element_by_xpath('/html/body/div[5]/div/div/div[2]')

            try:
                followers_urls = []
                # прокручиваем до самого конца окно с подписчиками
                for i in range(1, loops_count + 1):
                    browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', followers_ul)
                    time.sleep(random.randrange(2, 4))
                    print(f'Итерация №{i}')

                # список с подписчиками завернут в тег 'li',
                # поэтому находим все элементы с этим тегом и достаем имя юзера
                all_urls_div = followers_ul.find_elements_by_tag_name('li')

                for url in all_urls_div:
                    url = url.find_element_by_tag_name('a').get_attribute('href')
                    followers_urls.append(url)

                # сохраняем всех подписчиков пользователя в файл
                with open(f'{file_name}/{file_name}.txt', 'a') as text_file:
                    for link in followers_urls:
                        text_file.write(link + '\n')

                # открываем файл с подписчиками и сохраняем всех юзеров в список
                with open(f'{file_name}/{file_name}.txt') as text_file:
                    users_urls = text_file.readlines()

                    # берем по одному юзеру и проверяем на условия
                    for user in users_urls:
                        try:
                            # проверяем, подписаны ли мы уже на юзера,
                            # для этого открываем файл с юзерами, на которых мы уже подписались
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()
                                    if user in lines:
                                        print(f'Мы уже подписаны на {user}, переходим к следующему юзеру!')
                                        continue

                            except Exception as ex:
                                print('Файл со ссылками еще не создан!')
                                # print(ex)

                            # открываем страницу юзера
                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split('/')[-2]

                            edit_button = '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/a'
                            subscribe_check = '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button/div/span'

                            # проверяем, наш ли это профиль по кнопке "edit"
                            if self.xpath_exists(edit_button):
                                print('Это наш профиль, уже подписан, пропускаем итерацию!')

                            # проверка, если мы уже подписаны на юзера
                            elif self.xpath_exists(subscribe_check):
                                print(f'Уже подписаны на {page_owner}, пропускаем итерацию!')

                            else:
                                # т.к. в инсте кнопки подписки для открытого и приватного акка различны, то надо
                                # проверить, на какой акк мы перешли

                                private_acc_checker = '/html/body/div[1]/section/main/div/div/article/div[1]/div/h2'
                                time.sleep(random.randrange(4, 8))

                                # проверка акка на приватность
                                if self.xpath_exists(private_acc_checker):
                                    try:
                                        # кнопка запроса на подписку
                                        follow_button_req = '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button'
                                        browser.find_element_by_xpath(follow_button_req).click()
                                        print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)
                                # если аккаунты открытые
                                else:
                                    try:
                                        # проверяем кнопку подписки и нажимаем на нее
                                        follow_button = '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button'
                                        if self.xpath_exists(follow_button):
                                            browser.find_element_by_xpath(follow_button).click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)

                                # записываем данные в файл для ссылок всех подписок,
                                # если файла нет, создаем, если есть - дополняем
                                with open(f'{file_name}/{file_name}_subscribe_list.txt', 'a') as subscribe_list_file:
                                    subscribe_list_file.write(user)

                                # пауза между подписками. рекомендованно подписываться не более на 20-30 чел в час
                                time.sleep(random.randrange(120, 180))

                        except Exception as ex:
                            print(ex)

            except Exception as ex:
                print(ex)

        self.close_browser()

    # метод отправки сообщения в директ
    def send_direct_message(self, usernames='', message='', img_path=''):

        browser = self.browser
        time.sleep(random.randrange(2, 4))

        direct_button = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a'

        # проверка наличия кнопки. если есть, нажимаем на нее
        if not self.xpath_exists(direct_button):
            print("Кнопка отправки сообщений не найдена!")
            self.close_browser()
        else:
            print('Отправляем сообщение...')
            direct_message = browser.find_element_by_xpath(direct_button).click()
            time.sleep(random.randrange(2, 4))

        # отключаем всплывающее окно
        notification_window = '/html/body/div[5]/div/div/div/div[3]'
        not_now_button = '/html/body/div[5]/div/div/div/div[3]/button[2]'
        if self.xpath_exists(notification_window):
            browser.find_element_by_xpath(not_now_button).click()
        time.sleep(random.randrange(2, 4))

        # нажимаем на кнопку "отправить сообщение"
        send_message_button = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/div[3]/div/button'
        browser.find_element_by_xpath(send_message_button).click()

        # отправка сообщения нескольким пользователям
        for user in usernames:
            # вводим получателя
            input_field = '/html/body/div[5]/div/div/div[2]/div[1]/div/div[2]/input'
            to_input = browser.find_element_by_xpath(input_field)
            to_input.send_keys(user)
            time.sleep(random.randrange(2, 4))

            # выбираем получателя из списка
            users_list = '/html/body/div[5]/div/div/div[2]/div[2]'
            browser.find_element_by_xpath(users_list).find_element_by_tag_name('button').click()
            time.sleep(random.randrange(2, 4))

        # нажимаем кнопку "Далее"
        next_button = '/html/body/div[5]/div/div/div[1]/div/div[2]/div/button'
        browser.find_element_by_xpath(next_button).click()
        time.sleep(random.randrange(2, 4))

        # отправляем текстовое сообщение
        if message:
            message_area = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea'
            text_message_area = browser.find_element_by_xpath(message_area)
            text_message_area.clear()
            text_message_area.send_keys(message)
            time.sleep(random.randrange(2, 4))
            text_message_area.send_keys(Keys.ENTER)
            print(f'Сообщение для {usernames} отправлено!')
            time.sleep(random.randrange(2, 4))

        # отправка изображения
        if img_path:
            img_input = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/form/input'
            send_image_input = browser.find_element_by_xpath(img_input)
            send_image_input.send_keys(img_path)
            print(f'Изображение для {usernames} успешно отправлено!')
            time.sleep(random.randrange(2, 4))

        self.close_browser()

    # метод отписки от всех пользователей

    def unsubscribe_for_all_users(self, userpage):

        browser = self.browser
        browser.get(f'https://www.instagram.com/{userpage}/')
        time.sleep(random.randrange(3, 6))

        following_button_xpath = '/html/body/div[1]/section/main/div/header/section/ul/li[3]/a'
        following_button = browser.find_element_by_xpath(following_button_xpath)
        following_count = following_button.find_element_by_tag_name('span').text
        followers_count = int(following_count.replace(' ', ''))

        print(f'Количество подписок: {followers_count}')

        time.sleep(random.randrange(2, 4))

        # будем за раз отписываться от 10 пользователей, после этого перезагружать страницу
        loops_count = int(following_count / 10) + 1
        print(f'Количество перезагрузок страницы: {loops_count}')

        following_users_dict = dict()

        for loop in range(1, loops_count + 1):

            count = 10
            browser.get(f'https://www.instagram.com/{userpage}/')
            time.sleep(random.randrange(3, 6))

            # кликаем/вызываем меню подписок
            following_button.click()
            time.sleep(random.randrange(3, 6))

            # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
            following_div_block_xpath = '/html/body/div[5]/div/div/div[2]/ul/div'
            following_div_block = browser.find_element_by_xpath(following_div_block_xpath)
            following_users = following_div_block.find_elements_by_tag_name('li')
            time.sleep(random.randrange(3, 6))

            for user in following_users:

                if not count:
                    break

                user_url = user.find_element_by_tag_name('a').get_attribute('href')
                user_name = user_url.split('/')[-2]

                # добавляем в словарь пару имя_пользователя: ссылка на аккаунт, на всякий
                following_users_dict[user_name] = user_url

                following_button = user.find_element_by_tag_name('button').click()
                time.sleep(random.randrange(3, 6))
                unfollow_button = browser.find_element_by_xpath('/html/body/div[6]/div/div/div/div[3]/button[1]').click()

                print(f'Итерация #{count} >>> Отписался от пользователя {user_name}')
                count -= 1

                # time.sleep(random.randrange(120, 130))
                time.sleep(random.randrange(2, 4))

        with open('following_users_dict.txt', 'w', encoding='utf-8') as file:
            json.dump(following_users_dict, file)

        self.close_browser()


for user, user_data in users_settings_dict.items():
    username = user_data['login']
    password = user_data['password']
    # window_size = user_data['window_size']

    my_bot = InstagramBot(username, password)
    my_bot.login()
    # my_bot.close_browser()
    # my_bot.send_direct_message(direct_users_list, 'Это снова я тестирую бота)', 'C:\Python projects\InstaBot\lesson_7\IMG_20190221_220805.jpg')
    # my_bot.get_all_followers('https://www.instagram.com/paulamanzz/')
    # time.sleep(random.randrange(4, 8))
    my_bot.unsubscribe_for_all_users('just_awade')

# my_bot = InstagramBot(username, password)
# my_bot.login()
# my_bot.send_direct_message(direct_users_list, 'Привет! Это сообщение отправлено с бота)', 'C:\Python projects\InstaBot\lesson_6\IMG_20181212_135537.jpg')
# my_bot.get_all_followers('https://www.instagram.com/python2day/')
# my_bot.download_userpage_content('https://www.instagram.com/python2day/')
