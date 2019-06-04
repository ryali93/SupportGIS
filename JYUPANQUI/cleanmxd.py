import zipfile
import pythonaddins
import errno
from shutil import copyfile, copy, copytree, make_archive, rmtree
from consulting_siz import *
from settings_siz import*
from msg_siz import *
from multiprocessing import Pool


ruta_ini = r'D:\JORGE_YUPANQUI\PRUEBAS\tercer_prod\ruta_ini'
ruta_fin = r'D:\JORGE_YUPANQUI\PRUEBAS\tercer_prod\ruta_fin'
#ruta gdb static
ruta_gdb = os.path.join(GDB_DIR,"gdbzip.gdb")
decorador = os.path.join(IMG_DIR, 'loader.exe')


# ruta_ini = r'D:\JORGE_YUPANQUI\PRUEBAS\tercer_prod\ruta_ini\abc'


def decorator_loader(func):
    def decorator(*args):
        import subprocess
        import signal
        import os
        p = subprocess.Popen(decorador)
        func(*args)
        os.kill(p.pid, signal.SIGTERM)
    return decorator

class Exporting(object):

    def __init__(self):
        self.rutaIn  = ruta_ini
        self.rutaOut = ruta_fin
        self.lista   = []
        self.gdb     = ruta_gdb
        self.choice  = "SI"

    def listar(self):
        for path, dirs, files in os.walk(self.rutaIn):
            for file in files:
                if file.endswith('.mxd'):
                    self.lista.append(os.path.join(path, file))

    def copytreex(self,src, dst):
        try:
            copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno == errno.ENOTDIR:
                copy(src, dst)
            else:
                raise

    def copy(self,file):
        self.mxd = arcpy.mapping.MapDocument(file)

        ruta2 = file.replace(self.rutaIn,self.rutaOut)
        [x,base] = os.path.split(ruta2)
        folder = base.split('.')[0]
        dirName = os.path.join(x,folder)

        try:
            if os.path.exists(dirName):
                rmtree(dirName)
            os.makedirs(dirName)
        except:
            pass

        rutamxd = os.path.join(dirName,base)
        copyfile(file,rutamxd)
        salida = os.path.join(dirName,"GDB","gdbMG.gdb")
        pdf    = os.path.join(dirName,"PDF","{}.pdf".format(folder))
        self.copytreex(self.gdb,salida)
        self.mxd2 = arcpy.mapping.MapDocument(rutamxd)
        self.gdb2 = salida
        self.pdf2 = pdf
        self.dirName = dirName

    def replacePath(self,mxd,gdb):
        self.gdbold1=  u'{}.gdb'.format(arcpy.mapping.ListLayers(mxd,'*IGN_CULTU*')[0].dataSource.split('.gdb')[0])
        self.gdbold2=  u'{}.gdb'.format(arcpy.mapping.ListLayers(mxd,'*_Pog*')[0].dataSource.split('.gdb')[0])

        mxd.replaceWorkspaces(self.gdbold1, "FILEGDB_WORKSPACE", gdb, "FILEGDB_WORKSPACE", True)
        mxd.replaceWorkspaces(self.gdbold2, "FILEGDB_WORKSPACE", gdb, "FILEGDB_WORKSPACE", True)
        mxd.save()

    def exportPDF(self,mxd,pdf):
        dir = os.path.dirname(pdf)
        if os.path.exists(dir):
            pass
        else:
            os.mkdir(dir)
        arcpy.mapping.ExportToPDF(mxd, pdf)


    def zipping(self,name,zip = "SI"):
        if zip == "SI":
            zipf = zipfile.ZipFile('{}.zip'.format(name),'w',zipfile.ZIP_DEFLATED)
            lenDirPAth = len(name)
            for root, dirs, files in os.walk(name):
                for file in files:
                    if not file.endswith('.lock'):
                        rt = os.path.join(root,file)
                        zipf.write(rt,rt[lenDirPAth:])
            zipf.close()
        else:
            pass

    # def runThread(self,i):
    #     # Vista 1
    #     pythonaddins.MessageBox("copy", "titleError")
    #     self.copy(i)
    #     # Vista 2
    #     pythonaddins.MessageBox("Consulting", "titleError")
    #     lyrAp = Consulting(self.mxd2, self.gdb2)
    #     lyrAp.main()
    #     pythonaddins.MessageBox("replacePath", "titleError")
    #     self.replacePath(self.mxd2, self.gdb2)
    #     pythonaddins.MessageBox("exportPDF", "titleError")
    #     self.exportPDF(self.mxd2, self.pdf2)
    #     pythonaddins.MessageBox("zipping", "titleError")
    #     self.zipping(self.dirName, zip=self.choice)

    def cleanMxd(self):
        mxd = arcpy.mapping.MapDocument("current")
        df = mxd.activeDataFrame
        lyr = arcpy.mapping.ListLayers(mxd,'fc1',df)[0]
        arcpy.mapping.RemoveLayer(df,lyr)
        del mxd, df, lyr


    @decorator_loader
    def runProcess(self):
        self.listar()
        if len(self.lista)==0:
            pythonaddins.MessageBox(nls().inicio().error, nls().titleError)
        else:
            # pool = Pool(processes=4)
            # pool.map(self.runThread, self.lista)

            for i in self.lista:
                self.copy(i)
                lyrAp = Consulting(self.mxd2,self.gdb2)
                lyrAp.main()
                self.replacePath(self.mxd2,self.gdb2)
                self.exportPDF(self.mxd2,self.pdf2)
                self.zipping(self.dirName, zip = self.choice)

    def main(self):
        self.runProcess()
        self.cleanMxd()
