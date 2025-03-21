# 2025.03.12 Python clear command. by Ebenezer
#clear.py



import os
import sys

def clear():
	if os.name in('posix', 'nt'):
		os.system('clear' if os.name == 'posix' else 'cls')
	else:
		print("\033c", end="", file=sys.stdout)