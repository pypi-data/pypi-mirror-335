from src.pxm_liumou_Stable.read import Read
from src.pxm_liumou_Stable.write import Write

w = Write(filename="xls/demoW.xlsx")
data = [
	["1", "1", "2"],
	["2", "2", "3"],
	["4", "2", "3"]
]
w.write_cover_lists(lists=data, index=True)
w.write_lists(lists=data)

r = Read(filename="xls/demoW.xlsx")
r.read_all()
for i in r.DataR:
	print(i)
