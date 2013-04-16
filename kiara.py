#!/usr/bin/env python3

import os.path
import sys
import argparse
import socket

# Default confg values.
config = {
	'host': 'api.anidb.net',
	'port': '9000',
	'session': '~/.kiara.session',
	'database': '~/.kiara.db',
}

def config_items(file):
	for line in map(lambda s: s.strip(), file.readlines()):
		if line.startswith('#') or not line:
			continue
		yield line.split(None, 1)

parser = argparse.ArgumentParser(
	description='Do stuff with anime files and anidb.')
parser.add_argument('-w', '--watch',
	action='store_true', dest='watch',
	help='Mark all the files watched.')
parser.add_argument('-o', '--organize',
	action='store_true', dest='organize',
	help='Organize ALL THE FILES _o/')
parser.add_argument('-c', '--config',
	action='store', dest='config', type=argparse.FileType('r'),
	help='Alternative config file to use.')
parser.add_argument('files',
	metavar='FILE', type=argparse.FileType('rb'), nargs='*',
	help='a file to do something with')

args = parser.parse_args()

# Read config.
try:
	with open('/etc/kiararc', 'r') as fp:
		config.update(config_items(fp))
except: pass
try:
	with open(os.path.expanduser('~/.kiararc'), 'r') as fp:
		config.update(config_items(fp))
except: pass
if args.config:
	config.update(config_items(args.config))

config_err = False
for key in 'host port user pass database session'.split():
	if not key in config:
		print('ERROR: Missing config variable:', key)
		config_err = True
if config_err:
	sys.exit(-1)

def send(msg):
	client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	client.connect(os.path.expanduser(config['session']))
	client.sendall(bytes(msg, 'UTF-8'))
	data = ''
	while True:
		data += str(client.recv(1024), 'UTF-8')
		if data == '---end---':
			client.close()
			return
		if '\n' in data:
			item, data = data.split('\n', 1)
			yield item

wah = False
for l in send('ping'):
	print(l)
	wah = l == 'pong'
assert wah

# OK, run over the files.
for file in args.files:
	# Load file info.
	q = 'a'
	if args.watch:
		q += 'w'
	
	if args.organize:
		q += 'o'
	
	for line in send(q + ' ' + file.name):
		print(line)