import functools
import inspect
import os
import ast
import traceback


def check(text):
	try:
		tree = ast.parse(text)
	except:
		return 'имеет синтаксические ошибки'

	# print(tree.body[0].body[0].value)

	for node in tree.body:
		if isinstance(node, ast.FunctionDef): continue
		if not isinstance(node, ast.ClassDef):
			return 'имеет глобальные переменные или вызовы функций'
		for node in node.body:
			if not isinstance(node, (ast.Assign, ast.FunctionDef, ast.ClassDef)):
				return f'имеет узел в глобальном классе, который не является переменной, функцией или классом: {node}'
			if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Call, ast.ListComp)):
				return 'имеет узел в глобальном классе, который является переменной с кодом'


def load(text):
	class Mod(dict):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)

		def __getattr__(self, key):
			return self[key]

		def __missing__(self, key):
			return None

		def __setattr__(self, key, value):
			self[key] = value

	g = {}
	exec(text, g)
	if 'info' not in g: return 'не имеет класс info'
	if type(g['info']) != type(Mod): return 'имеет объект info, который не является классом'
	if '__builtins__' in g: del g['__builtins__']
	info = g['info']

	mod_info_class = {
		'id': str, 
		'name': str, 
		'desc': str, 
		'depends': tuple, 
		'incompat': tuple, 
		'python': tuple, 
		'libs': dict
	}

	out = []
	for name, _type in mod_info_class.items():
		if not hasattr(info, name):
			out.append(f'не имеет переменную "{name}"'); continue
		value = getattr(info, name)
		# print(name, value, type(value))
		if type(value) != _type:
			out.append(f'имеет переменную "{name}", тип которой не равен {_type} ({type(value)})')
	if out:
		return out

	mod = Mod(g)
	# print(mod.keys())
	return mod


# data = {}
# for name in os.listdir():
# 	if not name.endswith('.mod.py'): continue
# 	with open(name, 'r', encoding='UTF-8') as file:
# 		pass
# 	names.append(name)

mods = {}
ids = []

# чтение модов
for filename in os.listdir():
	if not filename.endswith('.mod.py'): continue
	with open(filename, 'r', encoding='UTF8') as file:
		code = file.read()

	res = check(code)
	if res:
		print(f'Файл "{filename}": Ошибка: код {res}')
		continue

	mod = load(code)
	if type(mod) == str:
		mod = [mod]
	if type(mod) == list:
		for err in mod:
			print(f'Файл "{filename}": Ошибка: код {err}')
		continue
	if mod.info.id in mods:
		print(f'Файл "{filename}": Ошибка: файл пытался перезаписать id')
		continue

	print(f'Файл "{filename}": прочитан')
	mods[mod.info.id] = mod
	ids.append(mod.info.id)

print(ids)

# порядок модов
for id in tuple(ids):
	index = ids.index(id)
	ids[index] = None
	depends = mods[id].info.depends
	q = []
	for id2 in depends:
		if id2 in ids:
			q.append(ids.index(id2))
		else:
			print(f'Мод "{id}": Ошибка: нету мода "{id2}"')
	if len(q) < len(depends):
		del ids[index]
		del mods[id]
		print(f'Мод "{id}": Инфа: мод отключён')
		continue
	if not q:
		ids[index] = id
		continue
	q = max(q)+1
	ids.insert(q, id)
for index, id in enumerate(ids):
	if id == None: del ids[index]


print(ids)


# иницилязия модов
for index, id in enumerate(ids):
	# print(index, id)
	mod = mods[id]
	if not hasattr(mod, 'init'): continue
	if not callable(mod.init): continue
	try:
		mod.init()
	except:
		print(f'Мод "{id}": Ошибка:\n', traceback.format_exc())


exit()

def true_types(func):
	@functools.wraps(func)
	def wrapper(*f_args, **f_kwargs):
		f_args_new = []
		f_kwargs_new = {}

		def stc(_type, value):
			try: return _type(value)
			except: return value

		def check(name, value):
			if name not in func.__annotations__: return value
			_type = func.__annotations__[name]
			_type_v = type(value)
			if _type_v == str:
				if _type == int:
					new_value = stc(int, value)
					if new_value != value: return new_value
				elif _type == float:
					new_value = stc(float, value)
					if new_value != value: return new_value
			if _type_v != _type:
				raise TypeError(f'Неверный тип аргумента "{name}": {_type_v.__name__}, ожидался: {_type.__name__}')
			return value

		for name, value in zip(inspect.signature(test).parameters.keys(), f_args):
			f_args_new.append(check(name, value))
		for value in f_args[len(inspect.signature(test).parameters):]:
			f_args_new.append(value)
		for name, value in f_kwargs.items():
			f_kwargs_new[name] = check(name, value)

		return func(*f_args_new, **f_kwargs_new)
	return wrapper


# def dexec(text, **kwargs):
# 	null = lambda *args, **kwargs: None
# 	kwargs['true_types'] = true_types
# 	exec(text, kwargs)
# 	if ('main' not in kwargs) and (type(kwargs['main'] != Callable)):
# 		return null