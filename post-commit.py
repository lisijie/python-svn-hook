#! /usr/bin/env python
# -*- coding: utf-8 -*- 
"""
SVN提交后处理钩子
功能说明: 
	开发人员提交文件到SVN后，SVN会执行该钩子程序，该程序负责将更新的文件拷贝到web目录下，实现自动更新

作者: 李思杰 <lsj86@qq.com> <2012/04/28>
"""
import os
import sys
import shutil

reload(sys)
sys.setdefaultencoding('utf-8')

def main(argv):
	'''
	+======================================================
	+ 使用方法: post-commit /data/svn/test 11
	+ SVN调用钩子时会传2个参数，1:SVN仓库路径 2:当前版本号
	+======================================================
	'''
	(repos, txn) = argv
	servers = {}
	servers["zh_CN"] = ("trunk", "/data/www/zh_CN", "/data/svnupdate/zh_CN")
	servers["zh_TW"] = ("branches/zh_TW", "/data/www/zh_TW", "/data/svnupdate/zh_TW")

	logs = []
	
	svninfo = os.popen("/usr/bin/svnlook info '%s'" % repos).readlines()
	logs.append("提交人: %s\r\n提交时间: %s\r\n当前版本: %s\r\n提交说明: %s" % (svninfo[0], svninfo[1], svninfo[2], svninfo[3]))
	logs.append("===============================================")

	logs.append("\r\n改变文件列表: ")
	changelist = os.popen("/usr/bin/svnlook changed '%s'" % repos).readlines()
	logs.append("/usr/bin/svnlook changed '%s'" % repos)
	logs.append("".join(changelist))
	
	logs.append("\r\n改变目录列表: ")
	changedirs = os.popen("/usr/bin/svnlook dirs-changed %s" % repos).readlines()
	logs.append("/usr/bin/svnlook dirs-changed %s" % repos)
	logs.append("".join(changedirs))
	
	logs.append("\r\n执行svnupdate版本更新: ")
	version = ''
	for d in changedirs:
		if version == '':
			for k, v in servers.items():
				if len(d) > len(v[0]) and d[:len(v[0])] == v[0]:
					version = k
					offset  = len(v[0])
					break
		if version == '':
			return
		os.system("/usr/bin/svn update %s%s" % (servers[version][2], d[offset:]))
		logs.append("/usr/bin/svn update %s%s" % (servers[version][2], d[offset:]))

	logs.append("\r\n将文件拷贝到WEB目录:")
	
	for line in changelist:
		op   = line[:1]
		line = line[1:].strip()[offset:]
		src  = servers[version][2] + line
		dst  = servers[version][1] + line
		
		if op == "D": #删除文件
			os.system("rm -f %s" % dst);
			logs.append("rm -f %s" % dst)
			continue
		if op == "A": #增加文件
			if not os.path.exists(os.path.dirname(dst)):
				os.system("mkdir -p %s" % os.path.dirname(dst))
				logs.append("mkdir -p %s" % os.path.dirname(dst))
		if os.path.isfile(src):
			os.system("cp -f %s %s" % (src, dst))
			logs.append("cp -f %s %s" % (src, dst))
	
	logs.append("\r\n")
	fp = open("/data/www/logs/%s_%s.log" % (version, txn), "wb")
	fp.write("\r\n".join(logs))
	fp.close()

	print "全部更新完成，详细信息请查看: /data/www/logs/%s_%s.log" % (version, txn)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print main.__doc__
	else:
		main(sys.argv[1:])