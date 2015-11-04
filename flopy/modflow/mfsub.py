"""
mfsub module.  Contains the ModflowSub class. Note that the user can access
the ModflowSub class as `flopy.modflow.ModflowSub`.

Additional information for this MODFLOW package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/sub.htm>`_.

"""
import sys
import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d, util_3d, read1d


class ModflowSub(Package):
    """
    MODFLOW SUB Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modflow.mf.Modflow`) to which
        this package will be added.
    isubcb : int
        isubcb is a flag and unit number to which cell-by-cell flow terms will
        be written. (default is 0).
    isuboc : int
        isuboc is a flag used to control output of information generated by the
        SUB Package. (default is 0).
    idsave : int
        idsave is a flag and a unit number on which restart records for delay
        interbeds will be saved at the end of the simulation. (default is 0).
    idrest : int
        idrest is a flag and a unit number on which restart records for delay
        interbeds will be read in at the start of the simulation (default is 0).
    nndb : int
        nndb is the number of systems of no-delay interbeds. (default is 1).
    ndb : int
        ndb is the number of systems of delay interbeds. (default is 1).
    nmz : int
        nmz is the number of material zones that are needed to define the
        hydraulic properties of systems of delay interbeds. Each material zone
        is defined by a combination of vertical hydraulic conductivity, elastic
        specific storage, and inelastic specific storage. (default is 1).
    nn : int
        nn is the number of nodes used to discretize the half space to approximate
        the head distributions in systems of delay interbeds. (default is 20).
    ac1 : float
        ac1 is an acceleration parameter.  This parameter is used to predict the
        aquifer head at the interbed boundaries on the basis of the head change
        computed for the previous iteration. A value of 0.0 results in the use
        of the aquifer head at the previous iteration. Limited experience indicates
        that optimum values may range from 0.0 to 0.6. (default is 0).
    ac2 : float
        ac2 is an acceleration parameter. This acceleration parameter is a multiplier
        for the head changes to compute the head at the new iteration. Values
        are normally between 1.0 and 2.0, but the optimum is probably closer to 1.0
        than to 2.0. However this parameter also can be used to help convergence of
        the iterative solution by using values between 0 and 1. (default is 0.2).
    itmin : int
        ITMIN is the minimum number of iterations for which one-dimensional equations
        will be solved for flow in interbeds when the Strongly Implicit Procedure (SIP)
        is used to solve the ground-water flow equations. If the current iteration
        level is greater than ITMIN and the SIP convergence criterion for head
        closure (HCLOSE) is met at a particular cell, the one-dimensional equations
        for that cell will not be solved. The previous solution will be used. The value
        of ITMIN is not used if a solver other than SIP is used to solve the
        ground-water flow equations. (default is 5).
    ln : int or array of ints (nndb)
        ln is a one-dimensional array specifying the model layer assignments for each
        system of no-delay interbeds. (default is 0).
    ldn : int or array of ints (ndb)
        ldn is a one-dimensional array specifying the model layer assignments for each
        system of delay interbeds.(default is 0).
    rnb : float or array of floats (ndb, nrow, ncol)
        rnb is an array specifying the factor nequiv at each cell for each system of
        delay interbeds. The array also is used to define the areal extent of each
        system of interbeds. For cells beyond the areal extent of the system of
        interbeds, enter a number less than 1.0 in the corresponding element of
        this array. (default is 1).
    hc : float or array of floats (nndb, nrow, ncol)
        hc is an array specifying the preconsolidation head or preconsolidation stress
        in terms of head in the aquifer for systems of no-delay interbeds. For any
        model cells in which specified HC is greater than the corresponding value of
        starting head, the value of HC will be set to that of starting head.
        (default is 100000).
    sfe : float or array of floats (nndb, nrow, ncol)
        sfe is an array specifying the dimensionless elastic skeletal storage
        coefficient for systems of no-delay interbeds. (default is 1.e-4).
    sfv : float or array of floats (nndb, nrow, ncol)
        sfv is an array specifying the dimensionless inelastic skeletal storage
        coefficient for systems of no-delay interbeds. (default is 1.e-3).
    com : float or array of floats (nndb, nrow, ncol)
        com is an array specifying the starting compaction in each system of
        no-delay interbeds. Compaction values computed by the package are added to
        values in this array so that printed or stored values of compaction and land
        subsidence may include previous components. Values in this array do not
        affect calculations of storage changes or resulting compaction. For simulations
        in which output values are to reflect compaction and subsidence since the start
        of the simulation, enter zero values for all elements of this array. (default is 0).
    dp : list or array of floats (nmz, 3)
        Data item includes nmz records, each with a value of vertical hydraulic
        conductivity, elastic specific storage, and inelastic specific storage.
        (default is [1.e-6, 6.e-6, 6.e-4]).
    dstart : float or array of floats (ndb, nrow, ncol)
        dstart is an array specifying starting head in interbeds for systems of delay
        interbeds. For a particular location in a system of interbeds, the starting head
        is applied to every node in the string of nodes that approximates flow in half
        of a doubly draining interbed. (default is 1).
    dhc : float or array of floats (ndb, nrow, ncol)
        dhc is an array specifying the starting preconsolidation head in interbeds for
        systems of delay interbeds. For a particular location in a system of interbeds,
        the starting preconsolidation head is applied to every node in the string of
        nodes that approximates flow in half of a doubly draining interbed. For any
        location at which specified starting preconsolidation head is greater than the
        corresponding value of the starting head, Dstart, the value of the starting
        preconsolidation head will be set to that of the starting head. (default is 100000).
    dcom : float or array of floats (ndb, nrow, ncol)
        dcom is an array specifying the starting compaction in each system of delay interbeds.
        Compaction values computed by the package are added to values in this array so that
        printed or stored values of compaction and land subsidence may include previous
        components. Values in this array do not affect calculations of storage changes or
        resulting compaction. For simulations in which output values are to reflect compaction
        and subsidence since the start of the simulation, enter zero values for all elements
        of this array. (default is 0).
    dz : float or array of floats (ndb, nrow, ncol)
        dz is an array specifying the equivalent thickness for a system of delay interbeds.
        (default is 1).
    nz : int or array of ints (ndb, nrow, ncol)
        nz is an array specifying the material zone numbers for systems of delay interbeds.
        The zone number for each location in the model grid selects the hydraulic conductivity,
        elastic specific storage, and inelastic specific storage of the interbeds.
        (default is 1).
    ids15 : list or array of ints (12)
        Format codes and unit numbers for subsidence, compaction by model layer, compaction
        by interbed system, vertical displacement, no-delay preconsolidation, and delay
        preconsolidation will be printed. If ids15 is None and isuboc>0 then print code 0
        will be used for all data which is output to the binary subsidence output file
        (unit=1051). The 12 entries in ids15 correspond to ifm1, iun1, ifm2, iun2, ifm3,
        iun3, ifm4, iun4, ifm5, iun5, ifm6, and iun6 variables. (default is None).
    ids16 : list or array of ints (isuboc, 17)
        Stress period and time step range and print and save flags used to control printing
        and saving of information generated by the SUB Package during program execution. Each
        row of ids16 corresponds to isp1, isp2, its1, its2, ifl1, ifl2, ifl3, ifl4, ifl5,
        ifl6, ifl7, ifl8, ifl9, ifl10, ifl11, ifl12, and ifl13 variables for isuboc entries.
        isp1, isp2, its1, and its2 are stress period and time step ranges. ifl1 and ifl2
        control subsidence printing and saving. ifl3 and ifl4 control compaction by model
        layer printing and saving. ifl5 and ifl6 control compaction by interbed system
        printing and saving. ifl7 and ifl8 control vertical displacement printing and
        saving. ifl9 and ifl10 control critical head for no-delay interbeds printing and saving.
        ifl11 and ifl12 control critical head for delay interbeds printing and saving. ifl13
        controls volumetric budget for delay interbeds printing. If ids16 is None and isuboc>0
        then all available subsidence output will be printed and saved to the binary
        subsidence output file (unit=1051). (default is None).

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----
    Parameters are supported in Flopy only when reading in existing models.
    Parameter values are converted to native values in Flopy and the
    connection to "parameters" is thus nonexistent. Parameters are not supported in the SUB Package.

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()
    >>> sub = flopy.modflow.ModflowSub(m)

    """

    def __init__(self, model, isubcb=0, isuboc=0, idsave=0, idrest=0,
                 nndb=1, ndb=1, nmz=1, nn=20, ac1=0., ac2=0.2, itmin=5,
                 ln=0, ldn=0, rnb=1,
                 hc=100000., sfe=1.e-4, sfv=1.e-3, com=0., dp=[1.e-6, 6.e-6, 6.e-4],
                 dstart=1., dhc=100000., dcom=0., dz=1., nz=1,
                 ids15=None, ids16=None,
                 extension='sub', unit_number=32):
        """
        Package constructor.

        """
        extensions = [extension]
        name = ['SUB']
        units = [unit_number]
        extra = ['']

        if isuboc > 0:
            extensions.append('bud')
            name.append('DATA(BINARY)')
            units.append(2051)
            extra.append('REPLACE')
        if idsave > 0:
            extensions.append('rst')
            name.append('DATA(BINARY)')
            units.append(2052)
            extra.append('REPLACE')

        Package.__init__(self, model, extension=extensions, name=name, unit_number=units,
                         extra=extra)  # Call ancestor's init to set self.parent, extension, name and unit number

        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.heading = '# Subsidence (SUB) package file for {}, generated by Flopy.'.format(model.version)
        self.url = 'sub.htm'

        self.isubcb = isubcb
        self.isuboc = isuboc
        self.idsave = idsave
        self.idrest = idrest
        self.nndb = nndb
        self.ndb = ndb
        self.nmz = nmz
        self.nn = nn
        self.ac1 = ac1
        self.ac2 = ac2
        self.itmin = itmin
        # no-delay bed data
        self.ln = None
        self.hc = None
        self.sfe = None
        self.sfv = None
        if nndb > 0:
            self.ln = util_2d(model, (nndb,), np.int, ln, name='ln')
            self.hc = util_3d(model, (nndb, nrow, ncol), np.float32, hc, name='hc',
                              locat=self.unit_number[0])
            self.sfe = util_3d(model, (nndb, nrow, ncol), np.float32, sfe, name='sfe',
                               locat=self.unit_number[0])
            self.sfv = util_3d(model, (nndb, nrow, ncol), np.float32, sfv, name='sfv',
                               locat=self.unit_number[0])
            self.com = util_3d(model, (nndb, nrow, ncol), np.float32, com, name='com',
                               locat=self.unit_number[0])
        # delay bed data
        self.ldn = None
        self.rnb = None
        self.dstart = None
        self.dhc = None
        self.dz = None
        self.nz = None
        if ndb > 0:
            self.ldn = util_2d(model, (ndb,), np.int, ldn, name='ldn')
            self.rnb = util_3d(model, (ndb, nrow, ncol), np.float32, rnb, name='rnb',
                               locat=self.unit_number[0])
            self.dstart = util_3d(model, (ndb, nrow, ncol), np.float32, dstart, name='dstart',
                                  locat=self.unit_number[0])
            self.dhc = util_3d(model, (ndb, nrow, ncol), np.float32, dhc, name='dhc',
                               locat=self.unit_number[0])
            self.dcom = util_3d(model, (ndb, nrow, ncol), np.float32, dcom, name='dcom',
                                locat=self.unit_number[0])
            self.dz = util_3d(model, (ndb, nrow, ncol), np.float32, dz, name='dz',
                              locat=self.unit_number[0])
            self.nz = util_3d(model, (ndb, nrow, ncol), np.int, nz, name='nz',
                              locat=self.unit_number[0])
        # material zone data
        if isinstance(dp, list):
            dp = np.array(dp)
        self.dp = dp

        # output data
        if isuboc > 0:
            if ids15 is None:
                ids15 = np.zeros(12, dtype=np.int)
            else:
                if isinstance(ids15, list):
                    ids15 = np.array(ids15)
            # make sure the correct unit is specified
            for i in range(1, 12, 2):
                ids15[i] = 2051
            self.ids15 = ids15
            if ids16 is None:
                self.isuboc = 1
                # save and print everything
                ids16 = np.ones((1, 17), dtype=np.int)
                ids16[0, 0] = 0
                ids16[0, 1] = nper - 1
                ids16[0, 2] = 0
                ids16[0, 3] = 9999
            else:
                if isinstance(ids16, list):
                    ids16 = np.array(ids16)
            if len(ids16.shape) == 1:
                ids16 = numpy.reshape(ids16, (1, ids16.shape[0]))
            self.ids16 = ids16

        # add package to model
        self.parent.add_package(self)

    def __repr__(self):
        return 'Subsidence (SUB) package class'

    def write_file(self):
        """
        Write the package input file.

        """
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f = open(self.fn_path, 'w')
        # First line: heading
        f.write('{}\n'.format(self.heading))
        # write dataset 1
        f.write('{} {} {} {} {} {}'.format(self.isubcb, self.isuboc, self.nndb,
                                           self.ndb, self.nmz, self.nn))

        f.write('{} {} {} {} {}\n'.format(self.ac1, self.ac2,
                                          self.itmin, self.idsave, self.idrest))
        t = self.ln.array
        for tt in t:
            f.write('{} '.format(tt + 1))
        f.write('\n')
        t = self.ldn.array
        for tt in t:
            f.write('{} '.format(tt + 1))
        f.write('\n')

        # write dataset 4
        if self.ndb > 0:
            for k in range(self.ndb):
                f.write(self.rnb[k].get_file_entry())

        # write dataset 5 to 8
        if self.nndb > 0:
            for k in range(self.nndb):
                f.write(self.hc[k].get_file_entry())
                f.write(self.sfe[k].get_file_entry())
                f.write(self.sfv[k].get_file_entry())
                f.write(self.com[k].get_file_entry())

        # write dataset 9
        if self.ndb > 0:
            for k in range(self.nmz):
                f.write('{:15.6g} {:15.6g} {:15.6g}    #material zone {} data\n'.format(self.dp[k, 0], self.dp[k, 1],
                                                                                        self.dp[k, 2], k + 1))
        # write dataset 10 to 14
        if self.ndb > 0:
            for k in range(self.ndb):
                f.write(self.dstart[k].get_file_entry())
                f.write(self.dhc[k].get_file_entry())
                f.write(self.dcom[k].get_file_entry())
                f.write(self.dz[k].get_file_entry())
                f.write(self.nz[k].get_file_entry())

        # write dataset 15 and 16
        if self.isuboc > 0:
            # dataset 15
            for i in self.ids15:
                f.write('{} '.format(i))
            f.write('  #dataset 15\n')

            # dataset 16
            for k in range(self.isuboc):
                t = self.ids16[k, :]
                t[0:4] += 1
                for i in t:
                    f.write('{} '.format(i))
                f.write('  #dataset 16 isuboc {}\n'.format(k + 1))

        # close sub file
        f.close()

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
        swi2 : ModflowSwi2 object

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> sub = flopy.modflow.ModflowSub.load('test.sub', m)

        """

        if model.verbose:
            sys.stdout.write('loading sub package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')
        # dataset 0 -- header
        while True:
            line = f.readline()
            if line[0] != '#':
                break
        # determine problem dimensions
        nrow, ncol, nlay, nper = model.get_nrow_ncol_nlay_nper()

        # read dataset 1
        if model.verbose:
            sys.stdout.write('  loading sub dataset 1\n')
        t = line.strip().split()
        isubcb, isuboc, nndb, ndb, nmz, nn = int(t[0]), int(t[1]), int(t[2]), int(t[3]), int(t[4]), int(t[5])
        ac1, ac2 = float(t[6]), float(t[7])
        itmin, idsave, idrest = int(t[8]), int(t[9]), int(t[10])

        if isubcb > 0:
            isubcb = 53
        if idsave > 0:
            idsave = 2052
        if idrest > 0:
            ext_unit_dict[2053] = ext_unit_dict.pop(idrest)
            idrest = 2053

        ln = None
        if nndb > 0:
            if model.verbose:
                sys.stdout.write('  loading sub dataset 2\n')
            ln = np.empty((nndb), dtype=np.int)
            ln = read1d(f, ln) - 1
        ldn = None
        if ndb > 0:
            if model.verbose:
                sys.stdout.write('  loading sub dataset 3\n')
            ldn = np.empty((ndb), dtype=np.int)
            ldn = read1d(f, ldn) - 1
        rnb = None
        if ndb > 0:
            if model.verbose:
                sys.stdout.write('  loading sub dataset 4\n')
            rnb = [0] * ndb
            for k in range(ndb):
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'rnb delay bed {}'.format(k + 1),
                                 ext_unit_dict)
                rnb[k] = t
        hc = None
        sfe = None
        sfv = None
        com = None
        if nndb > 0:
            hc = [0] * nndb
            sfe = [0] * nndb
            sfv = [0] * nndb
            com = [0] * nndb
            for k in range(nndb):
                kk = ln[k] + 1
                # hc
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 5 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'hc layer {}'.format(kk),
                                 ext_unit_dict)
                hc[k] = t
                # sfe
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 6 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'sfe layer {}'.format(kk),
                                 ext_unit_dict)
                sfe[k] = t
                # sfv
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 7 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'sfv layer {}'.format(kk),
                                 ext_unit_dict)
                sfv[k] = t
                # com
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 8 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'com layer {}'.format(kk),
                                 ext_unit_dict)
                com[k] = t

        # dp
        dp = None
        if ndb > 0:
            dp = np.zeros((nmz, 3), dtype=np.float32)
            for k in range(nmz):
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 9 for material zone {}\n'.format(k + 1))
                line = f.readline()
                t = line.strip().split()
                dp[k, :] = float(t[0]), float(t[1]), float(t[2])

        dstart = None
        dhc = None
        dcom = None
        dz = None
        nz = None
        if ndb > 0:
            dstart = [0] * ndb
            dhc = [0] * ndb
            dcom = [0] * ndb
            dz = [0] * ndb
            nz = [0] * ndb
            for k in range(ndb):
                kk = ldn[k] + 1
                # dstart
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 10 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'dstart layer {}'.format(kk),
                                 ext_unit_dict)
                dstart[k] = t
                # dhc
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 11 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'dhc layer {}'.format(kk),
                                 ext_unit_dict)
                dhc[k] = t
                # dcom
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 12 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'dcom layer {}'.format(kk),
                                 ext_unit_dict)
                dcom[k] = t
                # dz
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 13 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.float32, 'dz layer {}'.format(kk),
                                 ext_unit_dict)
                dz[k] = t
                # nz
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 14 for layer {}\n'.format(kk))
                t = util_2d.load(f, model, (nrow, ncol), np.int, 'nz layer {}'.format(kk),
                                 ext_unit_dict)
                nz[k] = t

        ids15 = None
        ids16 = None
        if isuboc > 0:
            # dataset 15
            if model.verbose:
                sys.stdout.write('  loading sub dataset 15 for layer {}\n'.format(kk))
            ids15 = np.empty(12, dtype=np.int)
            ids15 = read1d(f, ids15)
            for k in range(1, 12, 2):
                model.add_pop_key_list(ids15[k])
                ids15[k] = 2051  # all subsidence data sent to unit 2051
            # dataset 16
            ids16 = [0] * isuboc
            for k in range(isuboc):
                if model.verbose:
                    sys.stdout.write('  loading sub dataset 16 for isuboc {}\n'.format(k + 1))
                t = np.empty(17, dtype=np.int)
                t = read1d(f, t)
                t[0:4] -= 1
                ids16[k] = t

        # close file
        f.close()

        # create sub instance
        sub = ModflowSub(model, isubcb=isubcb, isuboc=isuboc, idsave=idsave, idrest=idrest,
                         nndb=nndb, ndb=ndb, nmz=nmz, nn=nn, ac1=ac1, ac2=ac2, itmin=itmin,
                         ln=ln, ldn=ldn, rnb=rnb,
                         hc=hc, sfe=sfe, sfv=sfv, com=com, dp=dp,
                         dstart=dstart, dhc=dhc, dcom=dcom, dz=dz, nz=nz,
                         ids15=ids15, ids16=ids16)
        # return sub instance
        return sub
