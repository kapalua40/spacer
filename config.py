#!/usr/bin/env python
# coding: utf-8


# Адрес сайта для первого входа
base_url = 'spcs.pro'
scheme = 'https'
 
# Почта
email = 'name@site.com'
# Лимит подключений при сбоях
limit = 10
# Ожидание после сбоя (секунд)
time_sleep = 10
# Ожидание случайного кол-ва секунд до данного значения, между загрузками
time_s2 = 2
# Показать дебаг
debug=False
meta=True
# По 1 мегабайту
batch = 1024*1024

########## Дальше лучше не трогать ничего если не знаешь
cl1 = 'div[id="main_content"] div[class~="widgets-group"] a[class~="list-link"][class~="bb0"]'
cl2 = 'div[id="main_content"] a[class~="list-link"][class~="list-link-blue"]:not([class~="list-link_bg-yellow"])'
cl3 = 'div[id="main_content"] a[class~="__adv_download"]'


# Селекторы для выбора тегов
class_pictures = 		{	'page': 		'div[id="main_content"] div[id="sz_gallery_loader"] a'																				, 	
							'dir': 			'div[id="main_content"] div[class="widgets-group widgets-group_top bb0"] a'																				, 	
							'file': 		'div[id="main_content"] a[class~="__adv_download"]'  																										}

class_files = 			{	'page': '		div[class="main"] div[id="main_content"] div[class~="widgets-group_top"] div[id="sz_gallery_loader"] div[class~="list-item"] div[class="oh"] a[class~="strong_link"]', 		
							'dir': 			'div[class="main"] div[class~="widgets-group_top"] a[class~="list-link"]'														,						
							'file': 			f":is({cl1},{cl2},{cl3})"																												}

class_music = 			{	'page': 		'div[id="main_content"] div[id="sz_gallery_loader"] a[class~="arrow_link"]'													, 		
							'dir': 			'div[id="main_content"] div[class~="widgets-group"] a[class~="list-link"]:not([class~="list-link-grey"])'																					, 					
							'file': 		'div[id="main_content"] div[class~="widgets-group"] a[class~="__adv_download"]'											}

class_video = 			{'page': 		'div[id="main_content"] div[id="sz_gallery_loader"] a'																				, 	
							'dir': 		'div[id="main_content"] div[class~="widgets-group"] a[class~="list-link"]:not([class~="list-link-grey"])'																					,	
							'file': 	'div[id="main_content"] a[class~="list-link"][class~="list-link-blue"]:not([class~="list-link_bg-yellow"])'					}


class_pic_top = {	'page': 			'div[id="main_content"] div[class~="tiled_item"] div[class~="bb0"] div[class~="tiled-preview"] a',
					'dir': 				'div[id="main_content"] div[class="widgets-group widgets-group_top bb0"] a'	,
					'file': 			'div[id="main_content"] a[class~="__adv_download"]'							}



class_next_page = 'a[class~="pgn__link_next"]'
#class_next_page = 'a[class="pgn__link pgn__link_hover pgn__link_next"]'

class_avatar_page = 'div[class="user__ava_big"]'
class_status_page = 'div[class="user__status"]'
class_bookmarks = 'div[class="bookmark"] a[href]'
text_next = 'Вперёд'
class_nickname = 'span[itemprop="name"]'
class_music_cover = 'a[class~="gview_link"]'
class_avatar = ['div[class~="user__ava"] a[href]'  ,  'div[class~="user__ava"] img[class~="preview"][data-s]']


