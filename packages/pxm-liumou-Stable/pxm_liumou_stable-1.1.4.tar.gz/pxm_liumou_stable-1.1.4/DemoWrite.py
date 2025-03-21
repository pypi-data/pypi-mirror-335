#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   demo.py
@Time    :   2023-02-17 23:36
@Author  :   坐公交也用券
@Version :   1.0
@Contact :   faith01238@hotmail.com
@Homepage : https://liumou.site
@Desc    :   当前文件作用
"""
from plbm_liumou_Stable import ColorLogger

from src.pxm_liumou_Stable import Write


class DemoRead:
	def __init__(self, filename="xls/DemoWww.xlsx"):
		"""

		:param filename:
		"""
		self.filename = filename
		self.logger = ColorLogger(class_name=self.__class__.__name__)
		self.w = Write(filename=self.filename, create=False)  # 读取文件
		self.w.set()  # 设置Sheet索引值1（也就是第二个Sheet)

	def AddLine(self):
		data = ["姓名", "年龄"]
		if self.w.write_add_line(data):
			self.logger.info("添加标题成功")
		else:
			self.logger.error("添加标题失败")
		for i in [["刘某", 18], ["刘某", 18], ["刘某", 18]]:
			if self.w.write_add_line(i):
				self.logger.info("添加人员成功")
			else:
				self.logger.error("添加人员失败")

	def DeleteLine(self):
		self.w.delete_line(index=1, row=2)
		if self.w.Err is None:
			self.logger.info("删除成功")
		else:
			self.logger.error("删除失败")

	def AddList(self):
		"""
		添加二层嵌套列表数据
		:return:
		"""
		data = [["1", "2"], [3, 4]]
		self.w.write_lists(lists=data)
		self.w.set_center(whole=False, lines=[1, 2, 3])

	def start(self):
		self.AddLine()
		self.DeleteLine()
		self.AddList()


if __name__ == "__main__":
	d = DemoRead()
	d.start()
