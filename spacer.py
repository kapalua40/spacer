#!/usr/bin/env python
# coding: utf-8
import requests, json, logging, os, time, random
from optparse import OptionParser
from bs4 import BeautifulSoup
import config
import user_agent as ua
from tqdm import tqdm

formd = ' %(asctime)s - %(levelname)s - %(message)s' 
if config.debug == True:
    logging.basicConfig(level=logging.DEBUG, format = formd)
else:
    logging.basicConfig(level=logging.INFO, format = formd)

logging.debug('Начало')

###### Готовые ######

# 
def debug(text):
    logging.debug(text)
# 
def info(text):
    logging.info(text)
# 
def error(text):
    logging.error(text)

# Сбрасывает сообщение об ошибке на диск файлом
def error_dump(text):
    # 
    dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
    name = 'ERRORS.txt'
    with open(name, 'a') as f:
        f.write(f"{dt}: {text}\n\n")
        info(f"Сброшено на диск, в файл {name}")

# Получаем рандомный user-agent
def random_ua(k=1):
    return random.choices(list(ua.ua_pct['ua'].values()), list(ua.ua_pct['pct'].values()), k=k)

# Получить ссылку автовхода
def get_autolink(filename):
    
    arr = {}
    links = 0
    with open(filename, 'r') as f:
        links = f.readlines()
    
    for link in links:
        db = link.strip().split(';')
        arr[db[0]] = db[1]
    
    return arr

# Получаем сессию
def get_session(url_login):
    # Берём случайный user-agent
    global headers
    global stat
    headers = { 'User-Agent': random_ua()[0] }
    i = 0
    
    debug(headers)
    
    while i < config.limit:
        try:
            session = requests.Session()
            r = session.get(url_login, headers = headers)
            r.raise_for_status()
            session.headers.update({'Referer': url_login})

            stat['count_session'] += 1
            debug(f"headers: {headers}/referer: {url_login}")

            return session
        except requests.exceptions.BaseHTTPError as e:
            error(f"Error in get_session()")
            error_dump(e)
            stat['count_disconnect'] += 1
            i += 1
    

# НЕ готово!
# Поучает статус со страницы пользователя
def get_status_from_userpage(text_page):
    ###
    # 
    bs = BeautifulSoup(text_page, 'html.parser')
    t = bs.select(config.class_status_page)

    if len(t) > 0:
        return t[0].text
    else:
        return ''







# Достаёт анкету страницы юзера
def get_anketa_from_userpage(session, nick):
    ###
    url = f"{config.scheme}://{config.base_url}/anketa/index/{nick}/"
    res = aget(session, url)

    return res.text

### Готово!
# Получает страницу с аватаркой
def get_avatar_page(text):
    ###
    # аватарка
    bs = BeautifulSoup(text, 'html.parser')
    t = bs.select(config.class_avatar_page )
    b = t[0].select('a') if len(t) else ''
    href = b[0].attrs['href'] if len(b) > 0 else ''
    
    #print(href)
    res = aget(session, href)
    
    return res

# Готово!
# Получаем следующую страницу в папке
def get_next_page(text):
    b = BeautifulSoup(text, 'html.parser')
    arr = b.select(config.class_next_page)
    
    if len(arr) > 0:
        return arr[0].attrs['href']
    else:
        return 0

### Получаем следующую страницу в папке - без класса
def get_next_page2(text):
    bs = BeautifulSoup(text, 'html.parser')
    rs = bs.select('a')

    ret = 0
    for rrr in rs:
        if rrr.text.lower().__contains__(config.text_next.lower()):
            ret = rrr.attrs['href']
            break
    return ret


# Скачиваем аватар, его превьюхи и сохраняем
def get_avatar(session, text, stor):
    bs = BeautifulSoup(text, 'html.parser')
    # Получаем ссылку на страницу с аватаркой и ссылку на маленькое превью
    ff = bs.select(config.class_avatar[0])
    ff2 = bs.select(config.class_avatar[1])

    #Если аватарка есть
    if len(ff) > 0:
        url_ava_page = ff[0].attrs['href']
        # Скачиваем страницу с аватаркой
        r2 = aget(session, url_ava_page)

        # Получаем ссылку на файл аватара и дату публикации его на сервере
        url_ava = get_file_url(r2.text, 'pictures')
        dt_published = get_datePublished(r2.text)
        
        # Скачиваем файл аватара
        if len(url_ava) > 0:
            fn = os.path.basename(url_ava[0])
            save_file(f"{stor}{os.sep}{fn}", session, url_ava[0], dt_published)
        # Получаем превьюшки 600 и 800
        preview_files = get_prev_pic(r2.text)
        # Скачиваем их
        for pf in preview_files:
            fn = os.path.basename(pf)
            save_file(f"{stor}{os.sep}{fn}", session, pf, dt_published)

    # Если есть маленькое превью
    if len(ff2) > 0:
        preview_ava = ff2[0].attrs['data-s']
        fn = os.path.basename(preview_ava)
        save_file(f"{stor}{os.sep}{fn}", session, preview_ava, time='')

# Готово!
### Получаем закладки с одной страницы
def get_bookmarks_page(session, url, file):
    r = aget(session, url)
    bs = BeautifulSoup(r.text, 'html.parser')
    t = bs.select(config.class_bookmarks)

    with open(file, 'a') as f:
        for bk in t:
            print(f"{bk.get_text()}; {bk.attrs['href']}", file=f)









### Готово!
# Получает закладки со всех страниц
def get_bookmarks_all(session, file):

    url = f'{config.scheme}://{config.base_url}/bookmarks/'

    while url != 0:
        get_bookmarks_page(session, url, file)
        
        res = aget(session, url)
        url = get_next_page2( res.text )

# Готово!
# Получает ник пользователя под которым сидим на сайте
def get_nick(session):
    res = aget(session, f"{config.scheme}://{config.base_url}/mysite/")
    bs = BeautifulSoup(res.text, 'html.parser')
    t = bs.select(config.class_nickname)

    return t[0].text.strip() if len(t) > 0 else ''



### Обёртка над get для удобного перехвата исключений и обработки
def aget(session,url):
    ###
    i = 0
    time_sleep = config.time_sleep
    response = 0
    global stat
    
    debug(headers)
    
    while i < config.limit:
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code == requests.status_codes.codes.OK:
                break
            elif response.status_code == requests.status_codes.codes.forbidden:
                error(f"Forbidden, response.status_code: {response.status_code}")
                break
            else:
                error(f"response.status_code: {response.status_code}")
                error(f"Ждём {time_sleep} секунд и пробуем снова (#{i+1}/{config.limit})")
                i += 1
                
                session.close()
                time.sleep(time_sleep)
                session = get_session(url_login)
                stat['count_reconnect'] += 1
                debug('Новая сессия')
                
        except requests.exceptions.ConnectionError as e:
            if str(e).__contains__('Max retries exceeded'):
                error_dump(str(e))
                error(f"Ошибка {str(e)}\nЖдём {time_sleep} секунд и пробуем снова (#{i+1}/{config.limit})")
                time.sleep(time_sleep)
                raise BaseException(-1)
            else:
                error(f"Ошибка {str(e)}\nЖдём {time_sleep} секунд и пробуем снова (#{i+1}/{config.limit})")
                error_dump(str(e))
                i += 1
                stat['count_disconnect'] += 1
                session.close()
                time.sleep(time_sleep)
                session = get_session(url_login)
                stat['count_reconnect'] += 1
                debug('Новая сессия')
            

        except requests.exceptions.BaseHTTPError as e:
            stat['count_disconnect'] += 1
            error(f"Ошибка. Скинул сообщение на диск")
            error_dump(e)
        except Exception as e:
            stat['count_disconnect'] += 1
            i += 1
            error(f"Общая ошибка = {str(e)}")

    
    return response
        

# Готово!
### Берёт файл логинами юзеров и отдаёт их список
def get_users(file_users):
    ###
    li = 0
    with open(file_users, 'r') as f:
        li= f.readlines()

    users = []
    if type(li) == list:
        for user in li:
            users.append(user.strip())
    
    return users

####################

### По нику и указанному разделу формирует ссылку
def get_url(nick, section):
    
    if section == 'guestbook':
        return f'{config.scheme}://{config.base_url}/guestbook/index/{nick}/'
    elif section == 'bookmarks':
        return f'{config.scheme}://{config.base_url}/bookmarks/'
    elif section == 'pictures' or section == 'files':
        return f'{config.scheme}://{config.base_url}/{part}/user/{user}/list/-/'

# Ищет страницы с файлами
def get_file_page(text, part):
    ####
    pages = []
    #f_page.attrs['href'])
    bs = BeautifulSoup(text, 'html.parser')
    if part == 'pictures':
        pages = [c.attrs['href'] for c in bs.select(config.class_pictures['page'])]
    elif part == 'pic_top':
        pages = [c.attrs['href'] for c in bs.select(config.class_pic_top['page'])]
    elif part == 'music':
        pages = [c.attrs['href'] for c in bs.select(config.class_music['page'])]
    elif part == 'video':
        pages = [c.attrs['href'] for c in bs.select(config.class_video['page'])]
    elif part == 'files':
        pages = [c.attrs['href'] for c in bs.select(config.class_files['page'])]
        
    return pages

# Ищет ссылки на файлы и картинки
def get_file_url(text, part):
    ####
    files = []
    bs = BeautifulSoup(text, 'html.parser')
    if part == 'pictures':
        files = [c.attrs['href'] for c in bs.select(config.class_pictures['file'])]
        if len(files) == 0:
            files = [el.attrs['href'] for el in bs.select('a[class="gview_link"][href][g]')]

    elif part == 'music':
        files = [c.attrs['href'] for c in bs.select(config.class_music['file'])]
    elif part == 'video':
        files = [c.attrs['href'] for c in bs.select(config.class_video['file'])]
    elif part == 'files':
        files = [c.attrs['href'] for c in bs.select(config.class_files['file'])]
    
    return files

# Ищет ссылки на папки
def get_dir_page(text, part):
    ####
    dirs = []
    bs = BeautifulSoup(text, 'html.parser')
    if part == 'pictures':
        dirs = [(c.text.strip().replace(os.sep, '_'), c.attrs['href']) for c in bs.select(config.class_pictures['dir'])]
    elif part == 'music':
        dirs = [(c.text.strip().replace(os.sep, '_'), c.attrs['href']) for c in bs.select(config.class_music['dir'])]
    elif part == 'video':
        dirs = [(c.text.strip().replace(os.sep, '_'), c.attrs['href']) for c in bs.select(config.class_video['dir'])]
    elif part == 'files':
        dirs = [(c.text.strip().replace(os.sep, '_'), c.attrs['href']) for c in bs.select(config.class_files['dir'])]
    
    return dirs


#
def guestbook2(session, url, file):
    r = aget(session, url)

    while url != 0:

        bs = BeautifulSoup(r.text, 'html.parser')
        t = bs.select(class_guestbook['comment'])

        for dd1 in t:    
            text = dd1.select('span[itemprop~="text"]')
            text = str(text[0]) if len(text) > 0 else str(text)

            dt = dd1.select('span[class="comment_date"]')
            date = dt[0].text.strip() if len(dt) > 0 else '???'

            name = dd1.select('b[itemprop="name"]')
            name = name[0].text if len(name) > 0 else '???'

            print(f"{name}\n{date}\n{text}\n")

        url = get_next_page2( r.text )

class_guestbook = { 'text': 'div[itemprop="text"]', 
                   'comment': 'div[class="comm shdw text cf"]',
                  'date': 'a[class="inl-link"]',
                   'text2': 'span[itemprop="text"]'}

# TODO
### Вытаскиваем всё из гостевой
def guestbook(session, url, file):
    # гостевая
    while url != 0:
        #div itemprop="text"
        res = aget(session, url)
        bs = BeautifulSoup(res.text, 'html.parser')
        t = bs.select(class_guestbook['text'])

        bs = BeautifulSoup(res.text, 'html.parser')
        a = bs.select(class_guestbook['2'])

        for cc in a:
            ### Дата коммента
            pre_dt = cc.select(class_guestbook['date'])
            dt = pre_dt[0].text if len(pre_dt) > 0 else ''

            ### Коммент
            pre_cc = cc.select(class_guestbook['3'])
            text = pre_cc[0].text if len(pre_cc) else ''

            with open(file, 'a') as f:
                print(f"{dt};{text}", file=f)
            
        url = get_next_page2( res.text )


# Принимает страницу с аватаром, отдает ссылку на сам аватар
def get_avatar_url(text):
    bs = BeautifulSoup(res.text, 'html.parser')
    tag = bs.select('meta[property="og:image"]')
    return tag[0].attrs['content'] if len(tag) > 0 else ''

def get_tags_class(text, class_):
    bs = BeautifulSoup(text, 'html.parser')
    t = bs.select('a[class="gview_link"]')

# Получаем превьюшки 600 и 800
def get_prev_pic(text):
    bs = BeautifulSoup(text, 'html.parser')
    cl1 = 'a[class~="gview_link"]'
    t = bs.select(cl1)
   
    if len(t) == 0:
        error('800-600 error')
        rr = bs.select('img[class="preview"]')
        
        if len(rr)>0:
            return (rr[0].attrs['src'])
        else:
            return ()
    else:
        g = t[0].attrs['g']
        g2 = g.split('||')[-3]

    # Фотки с размером 600 и 800, без подписи
    url_800 = g2.split('|')[-1]
    url_600 = g2.split('|')[-2]
    
    return (url_600, url_800)

###
def exit(s):
    s.get(f'{config.scheme}://{config.base_url}/logout/')
    s.close()

#### ??????????????
def get(text, cl):
    b = BeautifulSoup(text, 'html.parser')
    
    # Костыль чтобы лишний раз не парсить файл для времени заливки файла
    ctime = ''
    arr = 0
    
    if (cl == config.class_pictures["file"]) or (cl== config.class_files['file']) \
    or (cl== config.class_files['file_alt']) or (cl== config.class_music['file']):
        mt = b.select('meta[itemprop="datePublished"]')
        
        if (len(mt) > 0) and ('content' in mt[0].attrs.keys()):
            ctime = mt[0].attrs['content']
        else:
            ctime = ''
        
        urls = b.select(cl)
        arr = [ [ctime, url.attrs['href']] for url in urls]
    else:
        urls = b.select(cl)
        arr = [ [url.text.strip().replace(os.sep, '_'), url.attrs['href']] for url in urls]

    return arr

# Написать!!!!!111
# Получаем куки из файла
def get_cookie_from_file(name_file):

    with open(name_file, 'r') as f:
        js = f.read()
    js2 = json.loads(js) if js is not None else ''

    cook = requests.cookies.cookiejar_from_dict(js2[0])

# Устанавливаем новую дату на файл
def set_time_for_file(file_name, ctime):

    # '2017-10-11T09:50:03+03:00'
    t = time.strptime(ctime, "%Y-%m-%dT%H:%M:%S%z")
    #  "%a %b %d %H:%M:%S %Y".
    count_sec = time.mktime(t) 
    
    os.utime(file_name, times = (count_sec, count_sec))

### Добавляет к названию файла цифру, если такие файлы уже есть
def enter_name_file(file_name):
    while os.path.exists(file_name) == True:
        filename, file_extension = os.path.splitext(file_name)
            
        ####
        t = filename.split('_')
        if len(t) > 1:
            base_name = '_'.join( t[:-1] )
            num = t[-1]
            if num.isnumeric() == True:
                num = str( int(num) + 1 )
                filename = base_name + '_' + num
            else:
                filename += '_1'
        else:
            filename += '_1'

        file_name = filename + file_extension 
    
    return file_name

### 
def save_file(file_name, session, url, time = ''):
    '''Скачиваем файл по ссылке и сохраняем на диск по указанному пути'''
    
    OK = 200
    k = 100
    batch = config.batch
    i = 0
    
    # Скачиваю файл
    info('='*k)
    debug(f"Скачиваю файл {file_name}")
    response = aget(session, url)
        
    if response != 0:
        if response.status_code == OK:
            debug(f'Скачал файл:\n {url}')

            #
            file_name = enter_name_file(file_name)
            #
            if os.path.exists(file_name) != True:
                try:
                    with open(file_name, 'wb') as f:
                        h = response.headers
                        leng = 0
                        total_it = 0
                        if 'Accept-Ranges' in h.keys() and 'Content-Length' in h.keys():
                            if h['Accept-Ranges'] == 'bytes' and h['Content-Length'].isnumeric():
                                leng = int(h['Content-Length'])
                                total_it = leng//batch + 1
                        for chunk in tqdm(response.iter_content(batch), total=total_it):
                            f.write(chunk)

                    info(f"OK --> {file_name} сохранен!")
                    info(time)
                    info(url)
                except Exception as e:
                    error(f'Ошибка создания файла {file_name} = {e.args}')
                    
                    if i > config.limit:
                        exit(0)
                    else:
                        i += 1

            else:
                error(f'Файл существует! ШТО??? {file_name}')

            if time != '':
                try:
                    set_time_for_file(file_name, time)
                    debug('Установил время')
                except ValueError as e:
                    error(f"Ошибка с парсингом даты: {e.args}")
        else:
            error(f'Ошибка = {response.status_code}')
    else:
        error(f"response = {response};{url}")
        
    info(f"{'='*k}\n")

# Указываем тип искомого объекта (файл, папка, страница с файлом ) и раздел в котором ищем (pictures, music, video, files)
# Получаем строку для поиска записей о данном типе
def get_class(tp, part):

    if part == 'pictures':
        return config.class_pictures[tp]
    elif part == 'files':
        return config.class_files[tp]
    elif part == 'music':
        return config.class_files[tp]
    elif part == 'video':
        return config.class_video[tp]
    else:
        return config.class_pictures[tp]
        

### Написать новый сборщик файлов - коллектор
# Можно ли обойтись без рекурсии? Только на циклах
def collecter(session, url, part, dirr):
    
    # Грузим страницу
    text = aget(session, url).text

    # Ищем ссылки на папки
    cl = get_class('dir', part)
    dirs = get(text, cl)
        
    # Ищем ссылки на страницы файлов
    cl = get_class('page', part)
    pages = get(text, cl)

    for pg in pages:
        text = aget(session, pg).text
        file_url = get_file_url(text, part)
            #
        save_file(file_url)
        
    # Ищем следующую страницу
    url = get_next_page2()
    
    if url != 0:
        collecter(session, url, part, dirr)
    else:
        for dir_url in dirs:
            collecter(session, dir_url, part, dirr)


# 
def start(session, url, part = '', dirr = ''):
    
    info(f'Грузим страницу {url}')
    text = aget(session, url).text
    
    debug('Собираем ссылки на страницы')
    # собираю ссылки на страницы с файлами
    class_ = get_class("page", part)
    arr1 = get(text, class_)
        
    info(f"Кол-во файлов на странице в папке = {len(arr1)}")
    
    debug('Собираем ссылки на папки')
    # собирают ссылки на папки
    class_ = get_class("dir", part)
    arr2 = get(text, class_)
    
    info(f"Кол-во папок на странице в папке = {len(arr2)}")
    
    if len(arr2) > 0:
        info(f"Папки ==> { '; '.join( [a[0].strip() for a in arr2] ) }")
    
    # если есть ссылки на страницы с файлам, то для каждой ссылки забираем ссылку на файл
    if len(arr1) > 0:
        debug('Забираем ссылки на файлы')
        for a in arr1:
            class_ = get_class("file", part)
            text2 = aget(session, a[1]).text
            
            ret = get( text2, class_)
            
            # Фотки размеров 800 и 600
            ret800 = get_prev_pic(text2)
            
            #debug(f"ret = {ret}")
            if part == 'files':
                ret2 = get( text2, config.class_files['file_alt'] ) 
                ret = ret + ret2
                #debug(f"ret2 = {ret2}")
            
            if len(ret) > 0:
                # Скачиваем файл и сохраняем в папке dirr под именем
                ctime = ret[0][0]
                url_file = ret[0][1]
                name_file = os.path.basename(url_file)
                
                #
                url_file600 = ret800[0]
                url_file800 = ret800[1]
                #
                name_file600 = os.path.basename(url_file600)
                name_file800 = os.path.basename(url_file800)
                
                prev = 'prev'
                if prev not in os.listdir(dirr):
                    os.mkdir(dirr + os.sep + prev)
                
                save_file(dirr + os.sep + name_file, url_file, ctime)
                save_file(dirr + os.sep + prev + os.sep + name_file600, url_file600, ctime)
                save_file(dirr + os.sep + prev + os.sep + name_file800, url_file800, ctime)
                
                #info(name_file)

    # Ищем след страницу
    next_page = get_next_page2(text)
    # Если есть следующая страница, то запускаем эту же функцию рекурсивно на ней
    if next_page != 0:
        info(f'Переходим на страницу {next_page} и ищем там')
        start(session, next_page, part=part, dirr=dirr)
    else:
        debug('След страницы нет')
       
    # Если есть папки в папке, то в цикле рекурсивно запускаем эту же функцию
    if len(arr2) > 0:
        debug('Есть папки. Смотрим их')
        for dir1 in arr2:
            
            name_dir = dir1[0].strip().replace(os.sep, '_')
            url_dir = dir1[1]
            
            info(f"Смотрим папку \"{ name_dir }\" " )
            
            if name_dir not in os.listdir(dirr):
                os.mkdir(dirr + os.sep + name_dir)
                
            start(session, url_dir, part=part, dirr = dirr + os.sep + name_dir )

# Старая точка входа
def main_old():
    ###
    info('Погнали\nПодключаюсь к учетке')
    session = get_session(url_login)

    for user in users:
        for part in parts:
            url = f'{config.scheme}://{config.base_url}/{part}/user/{user}/list/-/'
            #
            info(f'Смотрим юзера "{user}", раздел "{part}" ==> {url}')

            if user not in os.listdir():
                os.mkdir(user)

            if part not in os.listdir(user):
                os.mkdir(user + os.sep + part)
            # Собираем ссылки, папки и проч
            start(session, url, part = part, dirr=user + os.sep + part)

            info(f'Раздел {part} юзера {user} завершен!')
        info(f'Просмотр разделов юзера {user} завершен!')

    session.close()
    info('Работа завершена!')
    info(f"Просмотренные юзеры: { '; '.join(users) }")
    info(f"Просмотренные разделы: { '; '.join(parts) }")



### Удаляем все комменты из гости
def delete_comment(s, url, time_wait):
    
    class_delete = 'a[data-action="comment_delete"]'

    r = aget(s, url)

    i = 1
    while url != 0:
        bs = BeautifulSoup(r.text, 'html.parser')
        ttt = bs.select(class_delete)

        url = ttt[0].attrs['href'] if len(ttt) > 0 else 0
        if url != 0:
            print(f"{i}; D--->{url}")
            r = aget(s, url)
            i += 1
            time.sleep(time_wait)



# Получаем данные о странице
def get_metadata(text, stor):
    
    bs = BeautifulSoup(text, 'html.parser')

    url_autor = bs.select('a[itemprop="url"][class="mysite-link"]')
    autor = url_autor[0].text if len(url_autor) > 0 else ''
    url_a = url_autor[0].attrs['href'] if len(url_autor) > 0 else ''

    desc = bs.select('meta[content][itemprop="description"]')
    cont = desc[0].attrs['content'] if len(desc) > 0 else ''

    dp = bs.select('meta[content][itemprop="datePublished"]')
    dp_c = dp[0].attrs['content'] if len(dp) > 0 else ''

    ud = bs.select('meta[content][itemprop="uploadDate"]')
    ud_c = ud[0].attrs['content'] if len(ud) > 0 else ''

    cs = bs.select('meta[content][itemprop="contentSize"]')
    cs_c = cs[0].attrs['content'] if len(cs) > 0 else ''

    tmp = bs.select('div[class~="pad_t_a"] span[class="break-word"]')
    des1 = tmp[0].text if len(tmp)>0 else ''

    tmp = bs.select('div[class~="pad_t_a"] a[class~="link-stnd"]')
    des2 = tmp[0].attrs['href'] if len(tmp)>0 else ''
    des3 = tmp[0].text if len(tmp)>0 else ''

    tmp = bs.select('div[class="pad_t_a break-word"]')
    desc_text = tmp[0].text if len(tmp)>0 else ''

    meta = str(bs.select('meta'))

    all_text = f"Автор: {autor}\n"\
    f"Ссылка на автора: {url_a}\n"\
    f"Описание файла: {cont}\n"\
    f"Дата публикации: {dp_c}\n"\
    f"Дата загрузки: {ud_c}\n"\
    f"Размер файла: {cs_c}\n"\
    f"Папка: {des3}\n"\
    f"Ссылка на папку: {des2}\n"\
    f"Описание: {desc_text}\n"\
    f"META:\n{meta}"
    
    
    tmp = bs.select('meta[content][property="og:image"]')
    fff = tmp[0].attrs['content'] if len(tmp)>0 else 'tmp'
    filename = os.path.basename(fff) + '.metadata'
    
    if 'metadata' not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}metadata")
    
    filename = enter_name_file(f"{stor}{os.sep}metadata{os.sep}{filename}")
    with open(filename, 'a') as f:
        print(all_text + '\n', file=f)
        
    file_html = enter_name_file(f"{stor}{os.sep}metadata{os.sep}{os.path.basename(fff)}.html")
    with open(file_html, 'w') as f2:
        f2.write(text)











def delete_bookmarks2(s, url_s):
    i = 1
    while url_s != 0:
        r = aget(s, url_s)
        url_s = get_next_page2(r.text)
        bs = BeautifulSoup(r.text, 'html.parser')
        tt1 = bs.select('a[class="arrow_link"]')

        for ts in tt1:
            r = aget(s, ts.attrs['href'])
            bs = BeautifulSoup(r.text, 'html.parser')
            tt = bs.select('a[class~="light_service_link"]')

            for t in tt:
                url = t.attrs['href']
                r = aget(s, url)
                bs = BeautifulSoup(r.text, 'html.parser')

                urls_del = bs.select('a[class="arrow_link"]')
                if len(urls_del)>0:
                    url =urls_del[0].attrs['href']
                    aget(s, url)
                    info(f"{i}: {url}"); i+=1






# 
def delete_bookmarks(s, url):
    
    tt1 = [1, 3]
    i = 1

    while len(tt1) > 0:
        r = aget(s, url)
        bs = BeautifulSoup(r.text, 'html.parser')
        tt1 = bs.select('a[class="arrow_link"]')


        tt_new = tt1[0].attrs['href'] if len(tt1)>0 else 0
        if tt_new != 0:
            r = aget(s, url)
            bs = BeautifulSoup(r.text, 'html.parser')
        else:
            return

        ttt = bs.select('a[class~="light_service_link"]')

        for t in ttt:
            u = t.attrs['href']
            r = aget(s, u)
            bs = BeautifulSoup(r.text, 'html.parser')

            dd = bs.select('a[class="arrow_link"]')
            url_delete = dd[0].attrs['href'] if len(dd)>0 else 0

            if url_delete != 0:
                print(f"{i}: {url_delete}")
                aget(s, url_delete)
                i += 1





# Получаем список читателей с одной страницы
def get_readers_one(text):
    ns = BeautifulSoup(text, 'html.parser')
    ttt = ns.select('div[class~="list-link__wrap"] a[href]')

    for t in ttt:
        url = t.attrs['href']

        print(url)

# Достаём из страницы с файлом дату и время публикации
def get_datePublished(text):
    bs = BeautifulSoup(text, 'html.parser')
    dt = bs.select('meta[itemprop="datePublished"][content]')
    
    if len(dt) > 0:
        return dt[0].attrs['content']
    else:
        return ''

### Получаем обложку музыкального трека
def get_cover_track(text):
    bs = BeautifulSoup(text, 'html.parser')
    ret = bs.select(config.class_music_cover)
    
    if len(ret) > 0:
        return ret[0].attrs['href']
    else:
        return ''



def get_save_pic(s, res, part, stor):
    # Дата публикации
    dt = get_datePublished(res.text)
    # Основной файл
    file_urls = get_file_url(res.text, part)
    for file_url in file_urls:
        
        if file_url.__contains__('/cs06.spac.me/'):
            raise BaseException(-1)

        ### Сам файл
        name_file = stor + os.sep + os.path.basename(file_url)
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {file_url}")
        save_file(name_file, s, file_url, dt)

    # Сдвинул этот блок на 1 таб влево
    # Превьюхи
    if 'prev' not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}prev")
    ff = get_prev_pic(res.text)
    for f1 in ff:
        name_file = f"{stor}{os.sep}prev{os.sep}{os.path.basename(f1)}"
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {f1}")
        save_file(name_file, s, f1, dt)
    # Прочие данные
    if config.meta == True:
        get_metadata(res.text, stor)



def get_save_music(s, res, part, stor):
    file_urls = get_file_url(res.text, part)
    dt = get_datePublished(res.text)

    for file_url in file_urls:
        
        if file_url.__contains__('/cs06.spac.me/'):
            raise BaseException(-1)
            
        ### Сам файл
        name_file = stor + os.sep + os.path.basename(file_url)
        name_file = enter_name_file(name_file)
        info(f"{name_file} <-- {file_url}")
        save_file(name_file, s, file_url, dt)

        if 'cover' not in os.listdir(stor):
            os.mkdir(f"{stor}{os.sep}cover")

    # Обложки, Подвинул блок
    ff = get_cover_track(res.text)
    if ff != '':
        name_file = f"{stor}{os.sep}cover{os.sep}{os.path.basename(ff)}"
        name_file = enter_name_file(name_file)

        debug(f"{name_file} <-- {ff}")
        save_file(name_file, s, ff, dt)
        
        # Превьюхи
    if 'prev' not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}prev")
    ff = get_prev_pic(res.text)
    for f1 in ff:
        name_file = f"{stor}{os.sep}prev{os.sep}{os.path.basename(f1)}"
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {f1}")
        save_file(name_file, s, f1, dt)

    # Прочие данные
    if config.meta == True:
        get_metadata(res.text, stor)

def get_save_files(s, res, part, stor):
    file_urls = get_file_url(res.text, part)
    dt = get_datePublished(res.text)

    for file_url in file_urls:
        
        if file_url.__contains__('/cs06.spac.me/'):
            raise BaseException(-1)
        
        ### Сам файл
        name_file = stor + os.sep + os.path.basename(file_url)
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {file_url}")
        save_file(name_file, s, file_url, dt)
        
    # Превьюхи
    if 'prev' not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}prev")
    ff = get_prev_pic(res.text)
    for f1 in ff:
        name_file = f"{stor}{os.sep}prev{os.sep}{os.path.basename(f1)}"
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {f1}")
        save_file(name_file, s, f1, dt)

    # Прочие данные
    if config.meta == True:
        get_metadata(res.text, stor)

def get_save_video(s, res, part, stor):
    file_urls = get_file_url(res.text, part)
    dt = get_datePublished(res.text)

    for file_url in file_urls:
        
        if file_url.__contains__('/cs06.spac.me/'):
            raise BaseException(-1)
        
        ### Сам файл
        name_file = stor + os.sep + os.path.basename(file_url)
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {file_url}")
        save_file(name_file, s, file_url, dt)
        
    # Превьюхи
    if 'prev' not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}prev")
    ff = get_prev_pic(res.text)
    for f1 in ff:
        name_file = f"{stor}{os.sep}prev{os.sep}{os.path.basename(f1)}"
        name_file = enter_name_file(name_file)
        debug(f"{name_file} <-- {f1}")
        save_file(name_file, s, f1, dt)

    # Прочие данные
    if config.meta == True:
        get_metadata(res.text, stor)

### Сборщик
def coll(s, url, part, stor, limit = None):
    # Получаем страницу
    r = aget(s, url)
    text = r.text
    
    # Получаем папки и файлы на странице
    dirs = get_dir_page(text, part)
    files_page= get_file_page(text, part)
    count_files = len(files_page)
    
    info(f"Папок: {len(dirs)}")
    info(f"Файлов в папке: {count_files}")

    for dd1 in dirs:
        if len(dd1) > 1:
            info(f"{dd1[0]} ===> {dd1[1]}")
        else:
            error(f"ERROR ? {dd1}")
    
    i = 0
    # для каждой страницы файла
    for f_page in files_page:
        i += 1
        info(f"Страница #{i}/{count_files} -- {f_page}")

        while True:
            res = aget(s, f_page)
            ts = random.randint(0, config.time_s2)
            info(f"Спим {ts} секунды")
            time.sleep(ts)
            ##################
            if part == 'pictures':
                try:
                    get_save_pic(s, res, part, stor)
                    break
                except BaseException as e:
                    error('Вот она!')
            ##############
            if part == 'pic_top':
                try:
                    get_save_pic(s, res, 'pictures', stor)
                    break
                except BaseException as e:
                    error('Вот она!')
            ##############
            elif part == 'music':
                try:
                    get_save_music(s, res, part, stor)
                    break
                except BaseException as e:
                    error('Вот она!')
            ##############  
            elif part == 'files':
                try:
                    get_save_files(s, res, part, stor)
                    break
                except BaseException as e:
                    error('Вот она!')
            ##############
            elif part == 'video':
                try:
                    get_save_video(s, res, part, stor)
                    break
                except BaseException as e:
                    error('Вот она!')

    if (limit == None) or (limit > 0):
        url_new = get_next_page2(text)
        if url_new != 0:
            info(f"Следующая страница --> {url_new}")
            if limit == None:
                coll(s, url_new, part, stor)
            elif limit > 0:
                coll(s, url_new, part, stor, limit-1)
        
    for dir1 in dirs:
        if len(dir1) == 2:
            name_dir = dir1[0].replace(os.sep, '_')
            url_dir  = dir1[1]
            if name_dir not in os.listdir(stor):
                os.mkdir(stor +os.sep+ name_dir)
            
            info(f"Захожу в папку {name_dir}")
            coll(s, url_dir, part, stor + os.sep + name_dir)
        else:
            error(f"ERROR --> {dir1}")

def ssstart(user_target, part):
    links = get_autolink('autolinks.txt')
    login_url = links['Pussy__Riot']

    session = get_session(login_url)

    url_target = f'https://spcs.pro/{part}/user/{user_target}/list/-/'

    if config.base_url not in os.listdir():
        os.mkdir(config.base_url)
    if user_target not in os.listdir(config.base_url):
        os.mkdir(f"{config.base_url}{os.sep}{user_target}")
    if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
        os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")

    stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"
    coll(session, url_target, part, stor)
    exit(session)



### 'div[class~="__adv_download"] a[href]'
### 'a.gview_link[href]'
### dev[class="att_wrap"] a[href]
def get_file_from_post(s, text, stor, select, part):

    bs = BeautifulSoup(text, 'html.parser')
    urls = bs.select(select)

    for url in urls:
        url_ = url['href']
        if url_.__contains__('https://') or url_.__contains__('http://'):
            info(url_)
            
            i = 0
            while i < 10:
                name = os.path.basename(url_)
                name = enter_name_file(f"{stor}{os.sep}{name}")
                try:
                    save_file(name, s, url_, '')
                    i = 13
                except BaseException as e:
                    error(f'Проблема 6 сервера: {str(e)}'); i+=1

### На странице находим ссылки на страницы с фотографиями и скачиваем фотки
#  dev[class="att_wrap"] a[href]
# 'a.gview_link[href]'
def get_pics_from_post(s, text, stor, select, part):

    bs = BeautifulSoup(text, 'html.parser')
    all_pic = bs.select(select)

    for pic in all_pic:
        url_pic = pic['href']
        
        if not (url_pic.__contains__('https://') or url_pic.__contains__('http://')):
            error('Не ссылка')
            return
        
        if url_pic.__contains__('/video/'):
            part = 'video'
            
        print(url_pic)

        i = 0
        while i < 10:
            r = aget(s, url_pic)
            dt = get_datePublished(r.text)
            urls_save = get_file_url(r.text, part)
            prevs = get_prev_pic(r.text)

            for p in prevs:
                name = os.path.basename(p)
                name = enter_name_file(f"{stor}{os.sep}{name}")
                try:
                    save_file(name, s, p, dt)
                except BaseException as e:
                    error(f'Проблема 6 сервера: {str(e)}'); i+=1

            for url_save in urls_save:
                name = os.path.basename(url_save)
                name = enter_name_file(f"{stor}{os.sep}{name}")
                try:
                    save_file(name, s, url_save, dt)
                    i = 13
                except BaseException as e:
                    error(f'Проблема 6 сервера: {str(e)}'); i += 1

#
def get_title_page(text):
    bs = BeautifulSoup(text, 'html.parser')
    ss = bs.select('title')
    title = ss[0].get_text().strip().replace(':', '_').replace(' ', '_').replace(os.sep, ';') if len(ss) > 0 else 'tmp'
    
    return str(title)[:40]

# Вытаскиваем теги с атрибутом src, достаём из него ссылки и скачиваем
def get_src_post(s, html, dir_d):
    bs = BeautifulSoup(html, 'html.parser')
    # Сохраняем картинки из тегов img
    tt = bs.select('[src]')
    
    for t in tt:
        # src который поменяем на локальный путь
        url_old = t.attrs['src']
        if url_old.__contains__('https://') or url_old.__contains__('http://'):
            # картинка которую скачиваем
            url_pic = url_old
            tag_old = t
            # название картинки
            namefile = os.path.basename(url_pic)
            #Путь по которому будет лежать скачанная картинка
            url_save = enter_name_file(f"{dir_d}{os.sep}{namefile}")
            url_new = f"{url_save.split(os.sep)[-2]}{os.sep}{url_save.split(os.sep)[-1]}"
            
            tag_new = str(tag_old).replace(url_old, url_new)
            t.replace_with(BeautifulSoup(tag_new, 'html.parser'))
            
            save_file(url_save, s, url_pic)

            debug(f"Скачиваем картинку {url_pic}")
            debug(f"Называем скачанную картинку как {url_save}")
            debug(f"Переименовываем {url_old} ===> {url_new}")

        else:
            debug('else')
            # Нужно сформировать новый тег, где старый src нужно заменить на локальную ссылку скачанного из data-s файла
            # Картинка, которую скачиваем
            url_pic = t.attrs['data-s']
            tag_old = t
            
            # Название картинки которую скачаем
            namefile = os.path.basename(url_pic)
            # путь, по которому будет лежать скачанная картинка
            url_save = enter_name_file(f"{dir_d}{os.sep}{namefile}")
            url_new = f"{url_save.split(os.sep)[-2]}{os.sep}{url_save.split(os.sep)[-1]}"
            # Заменяем старый путь на локальный
            tag_new = str(tag_old).replace(url_old, url_new)
            t.replace_with(BeautifulSoup(tag_new, 'html.parser'))
            
            save_file(url_save, s, url_pic)

            debug(f"Скачиваем картинку {url_pic}")
            debug(f"Называем скачанную картинку как {url_save}")
            debug(f"Переименовываем {url_old} ===> {url_new}")
            
    return str(bs)

#
def delete_diary(session, url):

    i = 1
    while True:
        r = aget(session, url)
        bs = BeautifulSoup(r.text, 'html.parser')
        ttt = bs.select('a[class~="tdn"]')

        for t in ttt:
            lol = t.attrs['href'].split('/')[7]
            id_ = 0
            if len(lol.split('-')) > 1:
                id_ = lol.split('-')[1]
            else:
                id_ = lol

            url_del = f"{config.scheme}://{config.base_url}/diary/delete/?id={id_}"
            rrr = aget(session, url_del)
            bs2 = BeautifulSoup(rrr.text)
            ddd = bs2.select('a.stnd-link.list-link-blue.c-blue')
            url_del = ddd[0].attrs['href']
            aget(session, url_del)
            info(f"{i}: {url_del}"); i+=1

        #url = get_next_page2(r.text)









### Скачиваем одну страницу с сайта с картинками и сохраняем
def download_one_page(s, url, time_st, number_page, stor):
    r = aget(s, url)
    html = r.text
    bs = BeautifulSoup(html, 'html.parser')
    # Название страницы
    title = f"{get_title_page(html)}_{time_st}"
    dir_d = enter_name_file(f"{stor}{os.sep}{title}{os.sep}page_{number_page}_files")
    dir_d1 = dir_d.split('/')[-1]
    
    if title not in os.listdir(stor):
        os.mkdir(f"{stor}{os.sep}{title}")
    if dir_d not in os.listdir(f"{stor}{os.sep}{title}"):
        os.mkdir(dir_d)

    ############################

    # Скачиваем превьюшки, переписываем теги
    html = get_src_post(s, html, dir_d)
    #
    ################################
    # Сохраняем страницу
    with open(f"{stor}{os.sep}{title}{os.sep}page_{number_page}.html", 'w') as f:
        f.write(html)
        
    # Страницы с раскрытыми сообщениями (если есть свёрнутые)
    desc_tt = bs.select('a[class="splr_item js-message_show"][href]')
    for desc_t in desc_tt:
        url_desc = desc_t['href']
        fdesc = enter_name_file(f"{dir_d}{os.sep}{number_page}_desc.html")
        if "desc" not in os.listdir(dir_d):
            os.mkdir(f"{dir_d}{os.sep}desc")
        
        r_n = aget(s, url_desc)
        r_nt = get_src_post(s, r_n.text, f"{dir_d}{os.sep}desc")

        with open(fdesc, 'w') as f:
            f.write(r_nt)

        if "test" not in os.listdir(f"{dir_d}{os.sep}desc"):
            os.mkdir(f"{dir_d}{os.sep}desc{os.sep}test")
        get_pics_from_post(s, r_n.text, f"{dir_d}{os.sep}desc{os.sep}test", 'a.gview_link[href]', 'pictures')
   

    if "test" not in os.listdir(dir_d):
        os.mkdir(f"{dir_d}{os.sep}test")

    get_pics_from_post(s, r.text, f"{dir_d}/test", 'a.gview_link[href]', 'pictures')
    get_pics_from_post(s, r.text, f"{dir_d}/test", 'div[class="att_wrap"] a[href][class~="link-stnd"]', 'files')
    get_file_from_post(s, r.text, f"{dir_d}/test", 'div[class~="__adv_download"] a[href]', 'music')

####
def download_one_elem(session, url, stor):
    time_st = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
    k = 1
    while url != 0:
        info(f"Страница #{k}")
        download_one_page(session, url, time_st, k, stor)
        r = aget(session, url)
        url = get_next_page2(r.text)
        k += 1











parser = OptionParser()

# Сервисные
parser.add_option("-i", "--input", dest="input", help="Файл с логинами", metavar="FILE")
parser.add_option("-A", "--auto-links", dest="al", help="Брать автовходы из файла", metavar="FILE")
parser.add_option("-I", "--into-account", dest="into", help="Войти в аккаунт", metavar="LOGIN")
parser.add_option("-R", "--rotation-al", dest="rotation", action="store_true",default=False, help="Ротация автовходов")
parser.add_option("-c", "--comm", dest="community", action="store_true",default=False, help="Скачиваем из сообщества (По умолчанию - пользователь)")

# Лёгкие
parser.add_option("-n", "--nick", dest="nick", action="store_true",default=False, help="Посмотреть никнэйм")
parser.add_option('-s', '--status', dest='status', action='store_true', default=False, help='Получить статус')
parser.add_option('-a', '--avatar', dest='avatar', action='store_true', default=False, help='Скачать аватар, new')
parser.add_option("-b", "--bookmarks", dest="bookmarks", action="store_true",default=False, help="Собрать закладки, new")
parser.add_option('-g', '--guestbook', dest='guestbook', action='store_true', default=False, help='Всё забрать из гостевой')
parser.add_option('',   '--post', dest='post', action='store_true', default=False, help='Всё забрать из почты')
parser.add_option('',   '--diary', dest='diary', action='store_true', default=False, help='Всё забрать из дневника')
parser.add_option("-0", "--one-element-html", dest="one_element", help="hhh", metavar="url")

# Основные - файловые
parser.add_option('-P', '--pictures', dest='pictures', action='store_true', default=False, help='Забираем фотографии, new')
parser.add_option("-M", "--music", dest="music", action='store_true', default=False, help='Забираем музыку, new')
parser.add_option("-V", "--video", dest="video", action='store_true', default=False, help='Забираем видео, new')
parser.add_option('-F', '--files', dest='files', action='store_true', default=False, help='Забираем файлы, new')

# Коллекции основных
parser.add_option('-p', '--pictures_collection', dest='pictures_collection', action='store_true', default=False, help='Собрать из коллекций фотографий, new')
parser.add_option('-v', '--video_collection', dest='video_collection', action='store_true', default=False, help='Собрать из коллекций видео, new')
parser.add_option('-f', '--files_collection', dest='files_collection', action='store_true', default=False, help='Собрать из коллекций файлов, new')

# Скачиваем отдельную папку из раздела картинки
parser.add_option('-1', '--pictures_dir', dest='pictures_dir', action='store_true', default=False, help='Забрать отдельную папку с подпапками из раздела pictures, new')
# Скачиваем отдельную папку из раздела файлы
parser.add_option('-2', '--files_dir', dest='files_dir', action='store_true', default=False, help='Забрать отдельную папку с подпапками из раздела files, new')
# Скачиваем отдельную папку из раздела видео
parser.add_option('-3', '--video_dir', dest='video_dir', action='store_true', default=False, help='Забрать отдельную папку с подпапками из раздела video, new')
# Скачиваем отдельную папку из раздела музыка
parser.add_option('-4', '--music_dir', dest='music_dir', action='store_true', default=False, help='Забрать отдельную папку с подпапками из раздела music, new')
#
parser.add_option('', '--pictures_top', dest='pic_top', action='store_true', default=False, help='Фотографии с главной. Лимит страниц указывается аргументом')


# Прочее
parser.add_option('-r', '--readers', dest='readers', action='store_true', default=False, help='Забираем читателей')
parser.add_option('-H', '--history_login', dest='history_login', action='store_true', default=False, help='Смотрим историю входов на аккаунте')
parser.add_option('-l', '--likes', dest='likes', action='store_true', default=False, help='Список того, что вы лайкали')
parser.add_option('-C', '--comm-list', dest='comm_list', action='store_true', default=False, help='Список сообществ пользователей заданных списком аргументов')
parser.add_option('', '--delete-bookmarks', dest='del_bookmarks', action='store_true', default=False, help='Удаляем закладки')
parser.add_option('', '--delete-comment-guestbook', dest='del_comm', action='store_true', default=False, help='Удаляем комменты из гостевой')


#parser.add_option('-m', '--main_old', dest='main_old', action='store_true', default=False, help='Запустить старую точку входа')
#oparser.add_option("-h", "--help", dest="hel", action="store_true",default=False, help="Справка")

(options, args) = parser.parse_args()







# Берём случайный user-agent
headers = { 'User-Agent': random_ua()[0] }
# Если автовход не задан - заходим на сайт как гость
url_login = f"{config.scheme}://{config.base_url}/"
links = []
login = ''
# Статистика подключений
stat = {'count_session': 0, 'count_disconnect': 0, 'count_reconnect': 0}

############# Точки входа #############

############ Автовходы ###############
# Если задан файл со списоком автовходов
if options.al is not None:
    file = str(options.al)
    # Словарь {логин: автовход}
    links = get_autolink(file)
    
    # Если задан нужный логин из списка - выбираем его
    if options.into is not None:
        login = str(options.into)
        
        if login in links.keys():
            url_login = links[login]
        else:
            error('Нет такого автовхода')
        
    # Если логин не задан - выбираем по умолчанию первый
    else:
        for login in links.keys():
            url_login = links[login]
            break
       
    session = get_session(url_login)
    info(f"Захожу по аккаунтом {login}: {url_login}")

############ Ник ###################################
if options.nick == True:
    debug('Смотрим никнэйм')
    #
    #session = get_session(url_login)
    nick = get_nick(session)
    print(nick)
    
    #exit(session)

############ Аватар #################################
if options.avatar == True:
    debug('avatar')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
    
    #session = get_session(url_login)
    for user in users:
        url = f"{config.scheme}://{config.base_url}/mysite/index/{user}/"
        r = aget(session, url)

        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user}")
        if 'avatar' not in os.listdir(f"{config.base_url}{os.sep}{user}"):
            os.mkdir(f"{config.base_url}{os.sep}{user}{os.sep}avatar")
        stor = f"{config.base_url}{os.sep}{user}{os.sep}avatar"

        get_avatar(session, r.text, stor)
    
    #exit(session)
############# Статус ################################
if options.status == True:
    debug('status')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
    
    #session = get_session(url_login)
    for user in users:
        url = f"{config.scheme}://{config.base_url}/mysite/index/{user}/"
        res = aget(session, url)
        status = get_status_from_userpage(res.text)
        print(f"{user};{status}")
        
    #exit(session)
############# Анкета ##################################

############# Гостевая #################################
if options.guestbook == True:
    debug('Гостевая')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
    
    for user in users:
        info(user)

        part = 'guestbook'
        #
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user}")
        stor = f"{config.base_url}{os.sep}{user}"
        if part not in os.listdir(stor):
            os.mkdir(f"{stor}{os.sep}{part}")
        stor = f"{stor}{os.sep}{part}"
        
        url = f'{config.scheme}://{config.base_url}/{part}/index/{user}/'
        info(f'Гостевая {user}\n')
        
        download_one_elem(session, url, stor)
        
        info(f"Всё вывел")
        
        #exit(session)
############## Блог ####################################

############## Собираем закладки #########################
if options.bookmarks == True and options.al is not None:
    debug('Собираем закладки')
        
    if config.base_url not in os.listdir():
        os.mkdir(config.base_url)
    dirr = f"{config.base_url}{os.sep}{login}"
    if login not in os.listdir(config.base_url):
        os.mkdir(dirr)

    #session = get_session(url_login)
    dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
    file = f"{dirr}{os.sep}bookmarks_{login}_{dt}.txt"
    get_bookmarks_all(session, file)
    info(f"-->{file}")
    
    #exit(session)
##################### Фотографии ###################### new
if options.pictures == True:
    info('Собираем картинки')
    
    users = []
    
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    type_site = 'user'
    if options.community == True:
        type_site = 'comm' 

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'pictures'
        url_target = f'{config.scheme}://{config.base_url}/{part}/{type_site}/{user_target}/list/-/'

        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"

        coll(session, url_target, part, stor)
        
        #exit(session)
################# Фотографии/Коллекции ####################### new
if options.pictures_collection == True:
    info('Собираем коллекции фотографий')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'pictures'
        url_target = f'{config.scheme}://{config.base_url}/{part}/collections/{user_target}/'
        
        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"
        if 'collection' not in os.listdir(stor):
            os.mkdir(f"{stor}{os.sep}collection")
        stor = f"{stor}{os.sep}collection"

        coll(session, url_target, part, stor)
        
        #exit(session)
#################### Музыка ################## new
if options.music == True:
    info('Собираем музыку')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    type_site = 'user'
    if options.community == True:
        type_site = 'comm'
    
    for user_target in users:
        #session = get_session(url_login)
        
        part = 'music'
        url_target = f'{config.scheme}://{config.base_url}/{part}/{type_site}/{user_target}/list/-/'

        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"

        coll(session, url_target, part, stor)
        
        #exit(session)

############ Видео ############## new
if options.video == True:
    info('Собираем видео')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    type_site = 'user'
    if options.community == True:
        type_site = 'comm'        

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'video'
        url_target = f'{config.scheme}://{config.base_url}/{part}/{type_site}/{user_target}/list/-/'

        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"

        coll(session, url_target, part, stor)
        
        #exit(session)

############# Видео, коллекции ############# new 
if options.video_collection == True:
    info('Собираем коллекции видео')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'video'
        url_target = f'{config.scheme}://{config.base_url}/{part}/collections/{user_target}/'
        
        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"
        if 'collection' not in os.listdir(stor):
            os.mkdir(f"{stor}{os.sep}collection")
        stor = f"{stor}{os.sep}collection"

        coll(session, url_target, part, stor)
        
        #exit(session)
############# Файлы ############# new
if options.files == True:
    info('Собираем файлы')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    type_site = 'user'
    if options.community == True:
        type_site = 'comm'        

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'files'
        url_target = f'{config.scheme}://{config.base_url}/{part}/{type_site}/{user_target}/list/-/'

        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"

        coll(session, url_target, part, stor)
        
        #exit(session)
############## Файлы/Коллекции ############ new
if options.files_collection == True:
    info('Собираем коллекции файлов')
    
    users = []
    if len(args) > 0:
        users = args
    elif options.input is not None:
        users = get_users(options.input)
    else:
        error("Задайте пользователя")
        exit(0)

    for user_target in users:
        #session = get_session(url_login)
        
        part = 'files'
        url_target = f'{config.scheme}://{config.base_url}/{part}/collections/{user_target}/'
        
        info(url_target)
        
        if config.base_url not in os.listdir():
            os.mkdir(config.base_url)
        if user_target not in os.listdir(config.base_url):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}")
        if part not in os.listdir(f"{config.base_url}{os.sep}{user_target}"):
            os.mkdir(f"{config.base_url}{os.sep}{user_target}{os.sep}{part}")
        stor = f"{config.base_url}{os.sep}{user_target}{os.sep}{part}"
        if 'collection' not in os.listdir(stor):
            os.mkdir(f"{stor}{os.sep}collection")
        stor = f"{stor}{os.sep}collection"

        coll(session, url_target, part, stor)
        
        #exit(session)
#############  Скачивание отдельных папок ################
# Отдельная папка из картинок
if options.pictures_dir == True:
    info('Скачиваем отдельную папку с подпапками из картинок')
    
    links = []
    if len(args) > 0:
        links = args
    else:
        error("Задайте URL папки")
        exit(0)

    for link in links:
        #session = get_session(url_login)
        part = 'pictures'
        dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
        stor = f"{part}_{dt}"
        info(f"{stor} <-- {link}")
        
        if stor not in os.listdir():
            os.mkdir(stor)

        coll(session, link, part, stor)
        
        #exit(session)

# Отдельная папка из файлов
if options.files_dir == True:
    info('Скачиваем отдельную папку с подпапками из файлов')
    
    links = []
    if len(args) > 0:
        links = args
    else:
        error("Задайте URL папки")
        exit(0)

    for link in links:
        #session = get_session(url_login)
        part = 'files'
        dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
        stor = f"{part}_{dt}"
        info(f"{stor} <-- {link}")
        
        if stor not in os.listdir():
            os.mkdir(stor)

        coll(session, link, part, stor)
        
        #exit(session)        
        
# Отдельная папка из видео
if options.video_dir == True:
    info('Скачиваем отдельную папку с подпапками из видео')
    
    links = []
    if len(args) > 0:
        links = args
    else:
        error("Задайте URL папки")
        exit(0)

    for link in links:
        #session = get_session(url_login)
        part = 'video'
        dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
        stor = f"{part}_{dt}"
        info(f"{stor} <-- {link}")
        
        if stor not in os.listdir():
            os.mkdir(stor)

        coll(session, link, part, stor)
        
        #exit(session)

# Отдельная папка из музыки
if options.music_dir == True:
    info('Скачиваем отдельную папку с подпапками из музыки')
    
    links = []
    if len(args) > 0:
        links = args
    else:
        error("Задайте URL папки")
        exit(0)

    for link in links:
        #session = get_session(url_login)
        part = 'music'
        dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
        stor = f"{part}_{dt}"
        
        info(f"{stor} <-- {link}")
        
        if stor not in os.listdir():
            os.mkdir(stor)

        coll(session, link, part, stor)
        
        #exit(session)

######################## Сообщества ######################
if options.comm_list == True:
    
    info('Список сообществ')

    users = []
    if len(args) > 0:
        users = args
    else:
        error("Задайте целевого пользователя")
        exit(0)
    
    #session = get_session(url_login)

    for user in users:
        url = f"{config.scheme}://{config.base_url}/comm/list/user/{user}/"

        print(f"{user}:\n")
        
        while url != 0:
            r = aget(session, url)
            bs = BeautifulSoup(r.text, 'html.parser')
            items = bs.select('div[class~="content-item3"] a[class~="tdn"][href]')

            for i, item in enumerate(items):
                text = item.text.strip()
                href = item.attrs['href']
                print(f"{i+1}: {text};{href}")

            url = get_next_page2(r.text)

    #exit(session)
###########################################################
# Друзья
######################### Читатели #######################
if options.readers == True:
    info('Смотрим читателей')
    
    users = []
    if len(args) > 0:
        users = args
    else:
        error("Задайте целевого пользователя")
        exit(0)

    #session = get_session(url_login)
    
    for user in users:
        url = f"{config.scheme}://{config.base_url}/lenta/readers/?user={user}"

        print(f"{user}:\n")

        while url != 0:
            r = aget(session, url)
            get_readers_one(r.text)
            url = get_next_page2(r.text)
    
    #exit(session)
##########################################################
# Подарки
# Форум
# Почта
#################### Лайки ###################
if options.likes == True:
    info('Список того, что понравилось')

    #session = get_session(url_login)
    url = f"{config.scheme}://{config.base_url}/bookmarks/likes/"

    i = 1
    while url != 0:
        r = aget(session, url)
        bs = BeautifulSoup(r.text, 'html.parser')
  
        t1 = 'div[class~="list_item"]'
        t2 = 'div[class~="content-item3"]'
        items = bs.select(f'div[id="main"] :is({t1},{t2}) a[href]')

        for item in items:
            text = item.text
            href = item.attrs['href']
            print(f"{i}: {text};{href}")
            i += 1

        url = get_next_page2(r.text)

    #exit(session)
######################### История входов ######################
if options.history_login == True:
    info("Смотрим историю входов")
    
    #session = get_session(url_login)
    url = f'{config.scheme}://{config.base_url}/mysite/loghist/'

    while url != 0:
        r = aget(session, url)
        bs = BeautifulSoup(r.text, 'html.parser')
        items = bs.select('div[class="content"] div[class~="content-item3"]')

        for i, item in enumerate(items):
            print(f"{i+1}:\n{item.text}")

        url = get_next_page2(r.text)

    #exit(session)
#############################################################
if options.del_bookmarks == True:

    url = f"{config.scheme}://{config.base_url}/bookmarks/"
    info('Удаляем закладки')
    delete_bookmarks2(session, url)
#############################################################
if options.del_comm == True:

    url = f"{config.scheme}://{config.base_url}/guestbook/"
    info('Комменты в гостевой')
    delete_comment(session, url, 0)
##############################################################
if options.post == True:
    info("Скачиваем всё из почты")
    
    user = login
    stor = config.base_url
    info(f"{stor}/{user}/")

    if user not in os.listdir(stor):
        stor = f"{stor}{os.sep}{user}"
        os.mkdir(stor)
    else:
        stor = f"{stor}{os.sep}{user}"
    
    if 'post' not in os.listdir(stor):
        stor = f"{stor}{os.sep}post"
        os.mkdir(stor)
    else:
        stor = f"{stor}{os.sep}post"

    url_start = f"{config.scheme}://{config.base_url}/mail/?List=3"
    
    while url_start != 0:
        r = aget(session, url_start)
        text = r.text
        bs = BeautifulSoup(r.text, 'html.parser')
        tt = bs.select('a[class~="mail__msg"][href]')

        for i, t in enumerate(tt):
            info(f"{i+1}: {t.attrs['href']}")
            url = t.attrs['href']
            
            download_one_elem(session, url, stor)

        url_start = get_next_page2(text)

##############################################################
if options.diary == True:
    info("Скачиваем всё из дневника")
    
    users = []
    if len(args) > 0:
        users = args
    else:
        error("Задайте целевого пользователя")
        exit(0)
    
    for user in users:
        #user = login
        stor = config.base_url
        info(f"{stor}/{user}/diary")

        if user not in os.listdir(stor):
            stor = f"{stor}{os.sep}{user}"
            os.mkdir(stor)
        else:
            stor = f"{stor}{os.sep}{user}"

        if 'diary' not in os.listdir(stor):
            stor = f"{stor}{os.sep}diary"
            os.mkdir(stor)
        else:
            stor = f"{stor}{os.sep}diary"

        url = f"{config.scheme}://{config.base_url}/diary/view/user/{user}/"
        #url = 'https://spcs.pro/bookmarks/index/'
        i = 1
        while url != 0:
            r = aget(session, url)
            bs = BeautifulSoup(r.text, 'html.parser')
            sel2 = 'div[class~="stnd-block"] a[href][class~="tdn"]'
            #sel2 = 'div[class~="wbg"] a[href][class~="list-link"]'
            ttt = bs.select(sel2)
            
            for t in ttt:
                info(f"Страница {i}: {t.attrs['href']}")
                url_d = t.attrs['href']
                ###
                download_one_elem(session, url_d, stor)
                i+=1

            url = get_next_page(r.text)

############################################################## 
if options.one_element is not None:
    url = str(options.one_element)
    stor = '.'
    download_one_elem(session, url, stor)
##############################################################
if options.pic_top == True:
    info('Собираем картинки с главной')

    limit = None
    if (len(args) > 0) and (str(args[0]).isnumeric()):
        limit = int(args[0])
        
    #https://spcs.global/sz/foto-i-kartinki/
    #https://spcs.global/sz/foto-i-kartinki/month/
    #https://spcs.global/sz/foto-i-kartinki/all/

    part = 'pic_top'
    url_target = f"{config.scheme}://{config.base_url}/sz/foto-i-kartinki/"
    session = get_session(url_target)
    
    info(url_target)

    dt = time.strftime('%Y-%m-%d_%H-%M-%S_%z')
    
    if config.base_url not in os.listdir():
        os.mkdir(config.base_url)
    if f"{part}_{dt}" not in os.listdir(config.base_url):
        os.mkdir(f"{config.base_url}{os.sep}{part}_{dt}")
    stor = f"{config.base_url}{os.sep}{part}_{dt}"

    coll(session, url_target, part, stor, limit)
##############################################################
# Сбрасываем статистику подключений
exit(session)
info(stat)



















