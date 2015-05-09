#!/usr/bin/python
# encoding: utf-8
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.
#

from Components.config import config

MinCacheLimit = 10

class EMCFileCache():
	def __init__(self):
		self.cacheDirectoryList = {}
		self.cacheFileList = {}
		self.cacheCountSizeList = {}

	def addCountSizeToCache(self, path, count, size):
#		print "EMC addCountSizeToCache", path
		if self.cacheCountSizeList.has_key(path):
			lastcount, lastsize = self.cacheCountSizeList[path]
			if lastcount != count or lastsize != size:
				del self.cacheCountSizeList[path]
				self.cacheCountSizeList[path] = count, size
		else:
			self.cacheCountSizeList[path] = count, size
#		print "EMC addCountSizeToCache", self.cacheCountSizeList

	def getCountSizeFromCache(self, path):
		if self.cacheCountSizeList.has_key(path):
			return self.cacheCountSizeList[path]
		else:
			return None
#		print "EMC getCountSizeFromCache", self.cacheCountSizeList

	def delcacheCountSizeList(self):
		self.cacheCountSizeList = {}
		print "EMC delete cacheCountSizeList", self.cacheCountSizeList

	def delcacheCountSizeListEntriesOnFileOp(self,source_path,dest_path):
		#print "EMC delcacheCountSizeListEntriesOnFileOp",source_path,dest_path
		rescanPaths = []
		for path in [source_path,dest_path]:
			if path:
				for k in self.cacheCountSizeList.keys():
					if (k+"/").startswith(path+"/") or (path+"/").startswith(k+"/"): # drop dirs containing path, but not "a/bc" when path is "a/bcd/e", therefore append "/"
						del self.cacheCountSizeList[k]
						rescanPaths.append(k)
						#print "EMC delcacheCountSizeListEntriesOnFileOp IS  deleting",k," due to OP on path ",path
					#else:
						#print "EMC delcacheCountSizeListEntriesOnFileOp NOT deleting",k," due to OP on path ",path
		return rescanPaths

	def IsPathInCountSizeList(self, path):
		if self.cacheCountSizeList.has_key(path):
			return True
		else:
			return False

	def addPathToCache(self, path, subdirlist, filelist):
		print "EMC addPathToCache", path
		if config.EMC.files_cache.value:
			if (len(subdirlist)>MinCacheLimit) or (len(filelist)>MinCacheLimit):
				self.cacheDirectoryList[path] = subdirlist
				self.cacheFileList[path] = filelist
			else:
				if self.cacheDirectoryList.has_key(path):
					del self.cacheDirectoryList[path]
				if self.cacheFileList.has_key(path):
					del self.cacheFileList[path]
#		print "EMC DirectoryCache", self.cacheDirectoryList
#		print "EMC FileCache", self.cacheFileList

	def addPathWithDirsToCache(self, path, subdirlist):
		if config.EMC.files_cache.value:
			if len(subdirlist)>MinCacheLimit:
				self.cacheDirectoryList[path] = subdirlist
			else:
				if self.cacheDirectoryList.has_key(path):
					del self.cacheDirectoryList[path]

	def addPathWithFilesToCache(self, path, filelist):
		if config.EMC.files_cache.value:
			if len(filelist)>MinCacheLimit:
				self.cacheFileList[path] = filelist
			else:
				if self.cacheFileList.has_key(path):
					del self.cacheFileList[path]

	def addRecToCacheFileList(self, path, rec):
		if config.EMC.files_cache.value:
			if self.cacheFileList.has_key(path):
				filelist = self.cacheFileList[path]
				filelist.append(rec)
				del self.cacheFileList[path]
				self.cacheFileList[path] = filelist

	def getCacheForPath(self, path):
		print "EMC getCacheForPath", path
		if config.EMC.files_cache.value and self.cacheDirectoryList.has_key(path) and self.cacheFileList.has_key(path):
			subdirlist = self.cacheDirectoryList[path]
			filelist = self.cacheFileList[path]
#			print "EMC DirectoryCache", self.cacheDirectoryList
#			print "EMC FileCache", self.cacheFileList
			return subdirlist, filelist
		else:
			return None, None

	def getDirsFromCacheForPath(self, path):
		if config.EMC.files_cache.value and self.cacheDirectoryList.has_key(path):
			subdirlist = self.cacheDirectoryList[path]
			return subdirlist
		else:
			return None

	def getFilesFromCacheForPath(self, path):
		if config.EMC.files_cache.value and self.cacheFileList.has_key(path):
			filelist = self.cacheFileList[path]
			return filelist
		else:
			return None

	def IsPathInCache(self, path):
		if config.EMC.files_cache.value and self.cacheDirectoryList.has_key(path) and self.cacheFileList.has_key(path):
			return True
		else:
			return False

	def IsPathWithDirsInCache(self, path):
		if config.EMC.files_cache.value and self.cacheDirectoryList.has_key(path):
			return True
		else:
			return False

	def IsPathWithFilesInCache(self, path):
		if config.EMC.files_cache.value and self.cacheFileList.has_key(path):
			return True
		else:
			return False

	def delPathFromCache(self, path):
		if len(path)>1 and path[-1]=="/":
			path = path[:-1]
		print "EMC delPathFromCache", path
		if self.cacheDirectoryList.has_key(path):
			del self.cacheDirectoryList[path]
		if self.cacheFileList.has_key(path):
			del self.cacheFileList[path]
#		print "EMC DirectoryCache", self.cacheDirectoryList
#		print "EMC FileCache", self.cacheFileList

	def delPathFromDirCache(self, path):
		if len(path)>1 and path[-1]=="/":
			path = path[:-1]
		if self.cacheDirectoryList.has_key(path):
			del self.cacheDirectoryList[path]

	def delPathFromFileCache(self, path):
		if len(path)>1 and path[-1]=="/":
			path = path[:-1]
		if self.cacheFileList.has_key(path):
			del self.cacheFileList[path]

movieFileCache = EMCFileCache()
