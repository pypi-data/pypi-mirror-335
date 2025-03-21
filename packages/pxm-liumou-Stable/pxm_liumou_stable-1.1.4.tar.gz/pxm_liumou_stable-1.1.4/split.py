from loguru import logger

from src.pxm_liumou_Stable.read import Read

r = Read(filename="xls/demo.xlsx")
r.read_all()
r.split_data(3)
for i in r.DataSplit:
	logger.info(i)
