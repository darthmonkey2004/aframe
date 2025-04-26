from aframe import Preview
import sys

try:
	url = sys.argv[1]
except:
	url = 'https://192.168.1.151/gps.html'
p = Preview(url=url)
