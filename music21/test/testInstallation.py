#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         testInstallation.py
# Purpose:      Controller for automated download, install, and testing.
#
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2009-2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------


# do not import music21; this does not rely on m21 code
import sys, os
import tarfile
import distutils.sysconfig

# define on or more directories to try to use as a scratch directory for download

SCRATCH = ['~/_download', '/_scratch']
M21_SOURCE = 'http://music21.googlecode.com/files/music21-0.2.5a4.tar.gz'
FORCE_DOWNLOAD = False
FORCE_EXTRACT = False

PY_BIN = ['python']


#-------------------------------------------------------------------------------
class InstallRunner:
    '''Base class for install runners. All methods in this class are cross platform. Platform specific code should be placed in subclasses.
    '''

    def __init__(self):
    
        self._fpScratch = None
        self._toClean = [] # store list of file paths to clean


    def _findScratch(self):
        for fp in SCRATCH:
            if os.path.exists(fp) and os.path.isdir(fp):
                return fp
        raise Exception('cannot find a valid scratch path')

    def download(self):
        pass

    def _extractTar(self, fp):
        # remove tar
        fpExtracted = fp.replace('.tar.gz', '')
        
        if not os.path.exists(fpExtracted) or FORCE_EXTRACT:
            tar = tarfile.open(fp)
            tar.extractall(path=self._fpScratch)
            tar.close()

        if not os.path.exists(fpExtracted):
            raise Exception('cannot find expected extaction: %s' % fpExtracted)
        return fpExtracted
        

    def install(self, fp):
        pass

    def test(self):
        pass

    def _getSitePackageDir(self):
        '''Get the music21 site package dir
        '''
        dir = distutils.sysconfig.get_python_lib()
        fp = os.path.join(dir, 'music21')
        if not os.path.exists(fp):
            raise Exception('cannot find music21 in site-packages: %s' % fp)
        return fp

    def _findSitePackagesToClean(self):
        found = []
        fp = distutils.sysconfig.get_python_lib()
        for fn in os.listdir(fp):
            if fn.startswith('music21'):
                found.append(os.path.join(fp, fn))
        return found
        
    def clean(self):
        pass

    def run(self):
        fpSource = self.download()
        # for now, just get the first py bin
        self.install(fpSource, PY_BIN[0])
        self.test(PY_BIN[0])
        self.clean()


#-------------------------------------------------------------------------------
class InstallRunnerNix(InstallRunner):
    '''Install runner for mac, linux, and unix machines.
    '''
    def __init__(self):
        InstallRunner.__init__(self)
        self._fpScratch = self._findScratch()


    def download(self):
        print('using download file path: %s' % self._fpScratch)
        junk, fn = os.path.split(M21_SOURCE)
        dst = os.path.join(self._fpScratch, fn)

        if not os.path.exists(dst) or FORCE_DOWNLOAD:
            cmd = 'wget -P %s %s' % (self._fpScratch, M21_SOURCE)
            os.system(cmd)
        # return resulting file name
        self._toClean.append(dst)
        return dst

    def install(self, fp, pyBin):
        # first, decompress
        fpExtracted = self._extractTar(fp)
        self._toClean.append(fpExtracted)

        fpSetup = os.path.join(fpExtracted, 'setup.py')
        if not os.path.exists(fpSetup):
            raise Exception('cannot find seutp.py: %s' % fpSetup)

        # create install command
        cmd = 'cd %s; sudo %s setup.py install' % (fpExtracted, pyBin)
        print('running setup.py: %s' % cmd)
        os.system(cmd)

        self._toClean += self._findSitePackagesToClean()


    def test(self, pyBin):
        testScript = os.path.join(self._getSitePackageDir(), 'test', 'test.py')
        cmd = '%s %s' % (pyBin, testScript)
        os.system(cmd)

    def clean(self):
        for fp in self._toClean:
            print('cleaning: %s' % fp)
            cmd = 'sudo rm -R %s' % fp
            os.system(cmd)





if __name__ == '__main__':
    
    ir = InstallRunnerNix()
    ir.run()





