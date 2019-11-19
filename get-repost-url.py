import pyamf
import pyamf.amf3
import sys
import urllib.parse
import zlib


class DrawrPartialDecoder(pyamf.amf3.Decoder):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._objectDepth = 0

	def _readDynamic(self, class_def, obj):
		attr = self.readBytes()
		while attr:
			obj[attr] = self.readElement()
			if attr == b'1' and self._objectDepth == 1:
				break
			attr = self.readBytes()

	def readObject(self, *args, **kwargs):
		self._objectDepth += 1
		ret = super().readObject(*args, **kwargs)
		self._objectDepth -= 1
		return ret


dec = zlib.decompressobj()
with open(sys.argv[1], 'rb') as fp:
	try:
		data = dec.decompress(fp.read(1024))
	except zlib.error:
		sys.exit(1) # Decompression failed
if data[:3] != b'\x0a\x0b\x01':
	sys.exit(2) # Unexpected start sequence
o = DrawrPartialDecoder(pyamf.util.BufferedByteStream(data)).readElement()

if '1' not in o:
	sys.exit(3) # No "1" key
if o['1']['mode'] != 'repost':
	sys.exit(0) # Nothing to do

repost = o['1']['color']
if 'http://' in repost:
	sys.exit(4) # repost URL not supported yet
elif repost != 'undefined' and repost != '':
	repostArray = repost.split('!')
	repostArray[0] = int(repostArray[0])
	repostData = urllib.parse.unquote(repostArray[1])
	repostKey = repostData[:repostArray[0]]
	repostMasterArray = sorted(repostKey)
	repostPasswordMap = {}
	for i in range(len(repostMasterArray)):
		repostPasswordMap[repostKey[i]] = repostMasterArray[i]
	repostStr = repostData[repostArray[0] : repostArray[0] + len(repostData)]
	repostImg = ''.join(repostPasswordMap[repostStr[i]] if repostStr[i] in repostPasswordMap else repostStr[i] for i in range(len(repostStr)))
	print(repostImg)
