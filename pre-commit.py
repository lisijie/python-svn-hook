#! /usr/bin/env python
# -*- coding: utf-8 -*- 
"""
SVN提交前检查钩子
功能：
	1、强制填写提交注释，内容10字节以上
	2、强制注释格式为：xxx:xxx
	3、提交文件检查，过滤不允许提交的文件

作者: 李思杰 <lsj86@qq.com> <2012/04/28>
"""

import sys
import os
import re

def main(argv):
	(repos, txn) = argv
	badlist = (".*config\.php$", ".*/php/cache", ".*test", "config\.js$","^.*\.db$")
	message = "".join(os.popen("/usr/bin/svnlook log '%s' -t '%s'" % (repos, txn)).readlines()).strip()
	if len(message) < 10:
		sys.stderr.write("请输入本次提交的修改内容，10字节以上。");
		sys.exit(1)
	if message.find(':') < 1:
		sys.stderr.write("请按规范填写注释，格式为：功能名: 修改说明。");
		sys.exit(1)

	changelist = os.popen("/usr/bin/svnlook changed '%s' -t '%s'" % (repos, txn)).readlines()
	for line in changelist:
		for pattern in badlist:
			if re.search(pattern, line):
				sys.stderr.write("请不要把 %s 加入版本库。" % line[1:].strip());
				sys.exit(1)
	sys.exit(0)

if __name__ == "__main__":
	main(sys.argv[1:])