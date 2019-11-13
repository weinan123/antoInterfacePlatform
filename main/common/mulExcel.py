# -*- coding: utf-8 -*-
import xlrd,os,xlwt
from xlutils.copy import copy
class mulExcel():
    def __init__(self,filepath,sheetindex):
        self.workbook = xlrd.open_workbook(filepath,formatting_info=True)
        self.sheet = self.workbook.sheet_by_index(sheetindex)
    #获取某sheet页：
    def getSheet(self,name):
        sheet = self.workbook.sheet_by_name(name)
        return sheet
    #获取行数和列数
    def getRowsCols(self):
        nrows = self.sheet.nrows
        ncols = self.sheet.ncols
        return nrows,ncols
    #获某行数据
    def getRowsData(self,rownum):
        rowValues = self.sheet.row_values(rownum)
        return rowValues
    #获取某列数据
    def getColData(self,colnum):
        colValues = self.sheet.col_values(colnum)
        return colValues

    # 生成新execel表格
    def createExcel(self,):
        newWorkbook = copy(self.workbook)
        newsheet = newWorkbook.get_sheet(0)
        return newWorkbook,newsheet
    #写入某列数据
    def writeColData(self,colnum,list):
        newWorkbook,writesheet = self.createExcel()
        for i in range(0,len(list)):
            writesheet.write(colnum,i,list[i])
            newWorkbook.save("newexcel.xls")
    #写入某行数据
    def writeRowData(self,newWorkbook,writesheet,rownum, list,modelname):
        for i in range(0,len(list)):
            writesheet.write(rownum,i,list[i])
        filepath = os.path.dirname(os.path.dirname(__file__)) + "\\postfiles\\" + modelname + ".xls"
        newWorkbook.save(filepath)
if __name__=='__main__':
    filepath = r"D:\project\auto_interface\antoInterfacePlatform\main\postfiles\template.xls"
    mulExcel = mulExcel(filepath,0)
    newWorkbook, newsheet = mulExcel.createExcel()
    data = [[1,1,1],[2,2,2],[3,3,3],[4,4,4]]
    for i in range(0,len(data)):
        mulExcel.writeRowData(newsheet,i+8,data[i],"weinan")


