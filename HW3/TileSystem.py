import math

EarthRadius = 6378137
MinLat = -85.05112878
MaxLat = 85.05112878
MinLong = -180
MaxLong = 180

def clip(n, minval, maxval):
	return min(max(n, minval), maxval)

def mapSize(level):
	return 256 << level

def groundResolution(latitude, level):
	latitude = clip(latitude, MinLat, MaxLat)
	return math.cos(latitude*math.pi / 180) * 2 * math.pi * EarthRadius / mapSize(level)

def mapScale(latitude, level, dpi):
	return groundResolution(latitude, level) * dpi/0.0254 

def latLongToPixelXY(latitude, longitude, level):
	latitude = clip(latitude, MinLat, MaxLat)
	longitude = clip(longitude, MinLong, MaxLong)
	x = (longitude + 180) / 360
	sinLatitude = math.sin(latitude * math.pi / 180)
	y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)
	mapsize = mapSize(level)
	pixelX = int(clip(x * mapsize + 0.5, 0, mapsize - 1))
	pixelY = int(clip(y * mapsize + 0.5, 0, mapsize - 1))
	return pixelX, pixelY

def pixelXYToTileXY(pixelX, pixelY):
	tileX = int(pixelX / 256)
	tileY = int(pixelY / 256)
	return tileX, tileY

def tileXYToQuadKey(tileX, tileY, level):
	quadkey = ""
	for i in range(level, 0, -1):
		digit = '0'
		mask = 1 << (i-1)
		if ((tileX & mask) != 0):
			digit = chr(ord(digit) + 1)
		if ((tileY & mask) != 0):
			digit = chr(ord(digit) + 1)
			digit = chr(ord(digit) + 1)
		quadkey += digit
	return quadkey

def latLongToTileXY(latitude, longitude, level):
	pixelX, pixelY = latLongToPixelXY(latitude, longitude, level)
	tileX, tileY = pixelXYToTileXY(pixelX, pixelY)
	return tileX, tileY

