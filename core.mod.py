
class info:
	name = 'Ядро'
	id = 'core'
	desc = 'Этот модуль является ядром для других модулей'
	depends = ()
	incompat = ()

	python = ((3, 10, 0), (3, 10, 999))
	libs = {'pygame': None}

def init():
	import pygame