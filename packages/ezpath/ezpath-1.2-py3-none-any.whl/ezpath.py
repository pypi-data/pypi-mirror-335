
import os
import sys
import inspect

def get_abs_path(rel_path="", follow_links=False):

	getpath = os.path.realpath if follow_links else os.path.abspath

	current_file = getpath(__file__)
	stack = inspect.stack()
	for frame in stack:
		caller = getpath(frame.filename)
		if caller != current_file:
			break

	file_path = os.path.dirname(getpath(caller))
	file_path = os.path.join(file_path, rel_path)
	return getpath(file_path)

def add_abs_path(abs_path):
	if abs_path not in sys.path:
		sys.path += [abs_path]

def add_rel_path(rel_path, follow_links=False):
	add_abs_path(get_abs_path(rel_path, follow_links))
