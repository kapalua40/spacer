#!/bin/bash

make
# Логин
u=my_login
# Список автовходов
f=autolinks.txt
# Скрипт
e=spacer.py
# Питон
p=python3
# Адрес сайта
baseurl=spcs.pro

# Список логинов
users=(user1 user2 user3 user4)

for user in ${users[@]}
do
	# Главная страница пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/mysite/index/$user/"
	# Анкета пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/anketa/index/$user/"
	# Страница из дневника пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/diary/view/user/$user/"
	# Скачиваем страницу с подарками пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/gifts/user_list/$user/"
	# Страница списка тем форума пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/forums/search_user/?query=$user"
	# Список комментариев пользователя в форуме пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/forums/search_user/?Comment=1&query=$user"
	# Читатели пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/lenta/readers/?user=$user"
	# Сообщества пользователя $user
	$p $e -A $f -I $u -0 "https://$baseurl/comm/list/user/$user/"
	# Скачиваем всё из дневника пользователя $user
	$p $e -A $f -I $u --diary $user
	# Скачиваем из гостевой пользователя $user
	$p $e -A $f -I $u --guestbook $user

	# Скачиваем аватарку пользователя $user 
	$p $e -A $f -I $u -a $user
	# Картинки пользователя $user
	$p $e -A $f -I $u -P $user
	# Коллекции картинок пользователя $user
	$p $e -A $f -I $u  -p $user
	# Скачиваем файлы пользователя $user
	$p $e -A $f -I $u -F $user
	# Коллекции файлов пользователя $user
	$p $e -A $f -I $u -f $user
	# Скачиваем видео пользователя $user
	$p $e -A $f -I $u -V $user
	# Коллекции видео пользователя $user 
	$p $e -A $f -I $u -v $user
	# Музыка пользователя $user
	$p $e -A $f -I $u -M $user


done

