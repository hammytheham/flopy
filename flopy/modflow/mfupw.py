import sys
import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d,util_3d
from flopy.modflow.mfpar import ModflowPar as mfpar


class ModflowUpw(Package):
    'Upstream weighting package class\n'
    def __init__(self, model, laytyp=0, layavg=0, chani=1.0, layvka=0, laywet=0, iupwcb = 53, hdry=-1E+30, iphdry = 0,\
                 hk=1.0, hani=1.0, vka=1.0, ss=1e-5, sy=0.15, vkcb=0.0, noparcheck=False,        \
                 extension='upw', unitnumber = 31):
        Package.__init__(self, model, extension, 'UPW', unitnumber) # Call ancestor's init to set self.parent, extension, name and unit number
        self.heading = '# UPW for MODFLOW-NWT, generated by Flopy.'
        self.url = 'upw_upstream_weighting_package.htm'
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # item 1
        self.iupwcb = iupwcb # Unit number for file with cell-by-cell flow terms
        self.hdry = hdry # Head in cells that are converted to dry during a simulation
        self.npupw = 0 # number of UPW parameters
        self.iphdry = iphdry
        self.laytyp = util_2d(model,(nlay,),np.int,laytyp,name='laytyp')
        self.layavg = util_2d(model,(nlay,),np.int,layavg,name='layavg')
        self.chani = util_2d(model,(nlay,),np.int,chani,name='chani')
        self.layvka = util_2d(model,(nlay,),np.int,layvka,name='vka')
        self.laywet = util_2d(model,(nlay,),np.int,laywet,name='laywet')

        self.options = ' '
        if noparcheck: self.options = self.options + 'NOPARCHECK  '

        self.hk = util_3d(model,(nlay,nrow,ncol),np.float32,hk,name='hk',locat=self.unit_number[0])
        self.hani = util_3d(model,(nlay,nrow,ncol),np.float32,hani,name='hani',locat=self.unit_number[0])
        self.vka = util_3d(model,(nlay,nrow,ncol),np.float32,vka,name='vka',locat=self.unit_number[0])
        self.ss = util_3d(model,(nlay,nrow,ncol),np.float32,ss,name='ss',locat=self.unit_number[0])
        self.sy = util_3d(model,(nlay,nrow,ncol),np.float32,sy,name='sy',locat=self.unit_number[0])
        self.vkcb = util_3d(model,(nlay,nrow,ncol),np.float32,vkcb,name='vkcb',locat=self.unit_number[0])
        self.parent.add_package(self)

    def write_file(self):
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f_upw = open(self.fn_path, 'w')
        # Item 0: text
        f_upw.write('%s\n' % self.heading)
        # Item 1: IBCFCB, HDRY, NPLPF        
        f_upw.write('{0:10d}{1:10.3G}{2:10d}{3:10d}{4:s}\n'.format(self.iupwcb,self.hdry,self.npupw,self.iphdry,self.options))
        # LAYTYP array
        f_upw.write(self.laytyp.string);
        # LAYAVG array
        f_upw.write(self.layavg.string);
        # CHANI array
        f_upw.write(self.chani.string);
        # LAYVKA array
        f_upw.write(self.layvka.string)
        # LAYWET array
        f_upw.write(self.laywet.string);
        # Item 7: WETFCT, IWETIT, IHDWET
        iwetdry = self.laywet.sum()
        if iwetdry > 0:
            raise Exception('LAYWET should be 0 for UPW')
        transient = not self.parent.get_package('DIS').steady.all()
        for k in range(nlay):           
            f_upw.write(self.hk[k].get_file_entry())
            if self.chani[k] < 1:                
                f_upw.write(self.hani[k].get_file_entry())            
            f_upw.write(self.vka[k].get_file_entry())
            if transient == True:                
                f_upw.write(self.ss[k].get_file_entry())
                if self.laytyp[k] !=0:                                        
                    f_upw.write(self.sy[k].get_file_entry())
            if self.parent.get_package('DIS').laycbd[k] > 0:                
                f_upw.write(self.vkcb[k].get_file_entry())
            if (self.laywet[k] != 0 and self.laytyp[k] != 0):               
                f_upw.write(self.laywet[k].get_file_entry())
        f_upw.close()

    @staticmethod
    def load(f, model, ext_unit_dict=None):
        """
        Load an existing package.

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ext_unit_dict : dictionary, optional
            If the arrays in the file are specified using EXTERNAL,
            or older style array control records, then `f` should be a file
            handle.  In this case ext_unit_dict is required, which can be
            constructed using the function
            :class:`flopy.utils.mfreadnam.parsenamefile`.

        Returns
        -------
        dis : ModflowUPW object
            ModflowLpf object.

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> lpf = flopy.modflow.ModflowUpw.load('test.upw', m)

        """

        if model.verbose:
            sys.stdout.write('loading upw package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')
        #dataset 0 -- header
        while True:
            line = f.readline()
            if line[0] != '#':
                break
        # determine problem dimensions
        nrow, ncol, nlay, nper = model.get_nrow_ncol_nlay_nper()
        # Item 1: IBCFCB, HDRY, NPLPF - line already read above
        if model.verbose:
            print('   loading IUPWCB, HDRY, NPUPW, IPHDRY...')
        t = line.strip().split()
        iupwcb, hdry, npupw, iphdry = int(t[0]), float(t[1]), int(t[2]), int(t[3])
        if iupwcb != 0:
            model.add_pop_key_list(iupwcb)
            iupwcb = 53
        # options
        noparcheck = False
        if len(t) > 3:
            for k in range(3,len(t)):
                if 'NOPARCHECK' in t[k].upper():
                    noparcheck = True
        # LAYTYP array
        if model.verbose:
            print('   loading LAYTYP...')
        line = f.readline()
        t = line.strip().split()
        laytyp = np.array((t[0:nlay]),dtype=np.int)
        # LAYAVG array
        if model.verbose:
            print('   loading LAYAVG...')
        line = f.readline()
        t = line.strip().split()
        layavg = np.array((t[0:nlay]),dtype=np.int)
        # CHANI array
        if model.verbose:
            print('   loading CHANI...')
        line = f.readline()
        t = line.strip().split()
        chani = np.array((t[0:nlay]),dtype=np.float32)
        # LAYVKA array
        if model.verbose:
            print('   loading LAYVKA...')
        line = f.readline()
        t = line.strip().split()
        layvka = np.array((t[0:nlay]),dtype=np.int)
        # LAYWET array
        if model.verbose:
            print('   loading LAYWET...')
        line = f.readline()
        t = line.strip().split()
        laywet = np.array((t[0:nlay]),dtype=np.int)
        # Item 7: WETFCT, IWETIT, IHDWET
        wetfct,iwetit,ihdwet = None,None,None
        iwetdry = laywet.sum()
        if iwetdry > 0:
            raise Exception('LAYWET should be 0 for UPW')

        # get parameters
        par_types = []
        if npupw > 0:
            par_types, parm_dict = mfpar.load(f, nplpf, model.verbose)

        # get arrays
        transient = not model.get_package('DIS').steady.all()
        hk = [0] * nlay
        hani = [0] * nlay
        vka = [0] * nlay
        ss = [0] * nlay
        sy = [0] * nlay
        vkcb = [0] * nlay
        for k in range(nlay):
            if model.verbose:
                print('   loading hk layer {0:3d}...'.format(k+1))
            if 'hk' not in par_types:
                t = util_2d.load(f, model, (nrow,ncol), np.float32, 'hk',
                                 ext_unit_dict)
            else:
                line = f.readline()
                t = mfpar.parameter_fill(model, (nrow, ncol), 'hk', parm_dict, findlayer=k)
            hk[k] = t
            if chani[k] < 1:
                if model.verbose:
                    print('   loading hani layer {0:3d}...'.format(k+1))
                if 'hani' not in par_types:
                    t = util_2d.load(f, model, (nrow,ncol), np.float32, 'hani',
                                     ext_unit_dict)
                else:
                    line = f.readline()
                    t = mfpar.parameter_fill(model, (nrow, ncol), 'hani', parm_dict, findlayer=k)
                hani[k] = t
            if model.verbose:
                print('   loading vka layer {0:3d}...'.format(k+1))
            if 'vka' not in par_types and 'vani' not in par_types:
                t = util_2d.load(f, model, (nrow,ncol), np.float32, 'vka',
                                 ext_unit_dict)
            else:
                line = f.readline()
                t = mfpar.parameter_fill(model, (nrow, ncol), 'vka', parm_dict, findlayer=k)
            vka[k] = t
            if transient:
                if model.verbose:
                    print('   loading ss layer {0:3d}...'.format(k+1))
                if 'ss' not in par_types:
                    t = util_2d.load(f, model, (nrow,ncol), np.float32, 'ss',
                                     ext_unit_dict)
                else:
                    line = f.readline()
                    t = mfpar.parameter_fill(model, (nrow, ncol), 'ss', parm_dict, findlayer=k)
                ss[k] = t
                if laytyp[k] != 0:
                    if model.verbose:
                        print('   loading sy layer {0:3d}...'.format(k+1))
                    if 'sy' not in par_types:
                        t = util_2d.load(f, model, (nrow,ncol), np.float32, 'sy',
                                         ext_unit_dict)
                    else:
                        line = f.readline()
                        t = mfpar.parameter_fill(model, (nrow, ncol), 'sy', parm_dict, findlayer=k)
                    sy[k] = t
            if model.get_package('DIS').laycbd[k] > 0:
                if model.verbose:
                    print('   loading vkcb layer {0:3d}...'.format(k+1))
                if 'vkcb' not in par_types:
                    t = util_2d.load(f, model, (nrow,ncol), np.float32, 'vkcb',
                                     ext_unit_dict)
                else:
                    line = f.readline()
                    t = mfpar.parameter_fill(model, (nrow, ncol), 'vkcb', parm_dict, findlayer=k)
                vkcb[k] = t

        # create upw object
        upw = ModflowUpw(model, iupwcb=iupwcb, iphdry=iphdry, hdry=hdry,
                         noparcheck=noparcheck,
                         laytyp=laytyp, layavg=layavg, chani=chani,
                         layvka=layvka, laywet=laywet,
                         hk=hk, hani=hani, vka=vka, ss=ss, sy=sy, vkcb=vkcb)

        # return upw object
        return upw

    def plot(self):

        try:
            import pylab as plt
        except Exception as e:
            print("error importing pylab: " + str(e))
            return

        #get the bas for ibound masking
        bas = self.parent.bas6
        if bas is not None:
            ibnd = bas.getibound()
        else:
            ibnd = np.ones((self.parent.nlay, self.parent.nrow,
                            self.parent.ncol), dtype=np.int)

        cmap = plt.cm.winter
        cmap.set_bad('w', 1.0)
        fs = 5

        nlay = self.parent.nlay

        #the width and height of each subplot
        delt = 2.0

        props = [self.hk.array, self.vka.array, self.ss.array, self.sy.array]
        names = ["hk", "vk", "ss", "sy"]
        shape = (len(names), nlay+1)
        fig = plt.figure(figsize=(delt+(nlay*delt), delt * len(names)))
        for k in range(nlay):
            for iname, name in enumerate(names):
                ax = plt.subplot2grid(shape, (iname, k), aspect="equal")
                p = props[iname][k]
                p = np.ma.masked_where(ibnd[k] == 0, p)
                ax.imshow(p, cmap=cmap, alpha=0.7,
                          interpolation="none")
                ax.set_title(name + " of layer {0:d} - max,min : {1:G},{2:G}"
                             .format(k+1, p.max(), p.min()), fontsize=fs)
                if k == 0:
                    ax.set_ylabel("row", fontsize=fs)
                    ax.set_yticklabels(ax.get_yticks(), fontsize=fs)
                else:
                    ax.set_yticklabels([])
                if iname == len(names)-1:
                    ax.set_xticklabels(ax.get_xticks(), fontsize=fs)
                    ax.set_xlabel("column", fontsize=fs)
                else:
                    ax.set_xticklabels([])
        plt.tight_layout()
        plt.show()

