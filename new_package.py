#-*- coding: UTF-8 -*-
import os 
import time
import sys
import re
import traceback
import ConfigParser
from encrypt_tool.encrypt_app import CryptApp

WORK_PATH = '/tmp'
DIRPATH = os.path.split(os.path.realpath(__file__))[0]
BASEPATH =  os.path.split(DIRPATH)[0]
CODEPATH = os.path.split(BASEPATH)[0]
#app打包后的输出路径
PACKAGE_OUTPUT_PAHT = DIRPATH
ENCRYPT_FILE = os.path.normpath(os.path.join(DIRPATH, 'encrypt_tool', 'pyprotect.py'))

APPNAME = 'bsa_tsa'
VERSION = '2.1.0'

APP_WORK_PATH = os.path.normpath(os.path.join(WORK_PATH, APPNAME))
STATIC_DIR = os.path.normpath(os.path.join(APP_WORK_PATH, 'static'))

# 不加密以下python文件
PYC_NOT_ENCNRYPT_LIST = {
    'files' : [
        # os.path.normpath(APP_WORK_PATH + os.sep + 'install.py'),
    ],
    'paths' : [
        # os.path.normpath(APP_WORK_PATH + os.sep + 'target'),
    ],
}

class Package(object):
    
    def __init__(self, encrypt=0):
        self.is_dat = 0
        self.is_pyc = 0
        self.is_front_pac = 0
        self.is_front_enc = 0
        self.__prepare()
        self.version = self.__get_svn()
        self.do_copy_work_dir()
        self.__get_encrypt_conf()
        if not self.is_dat:
            self.is_dat = encrypt
        try:
            self.__set_package_name()
            self.__do_build_jar()
            if self.is_pyc:
                self.__do_encrypt_file()
            if self.is_front_pac:
                if self.is_front_enc:
                    self.__do_build_front_enc()
                else:
                    self.__do_build_front_pac()
            if self.is_dat:
                self.package_name = "%s.%s.%s.tar.gz" % (APPNAME, VERSION, self.version)
                self.run_encrypt()
            else:
                self.package_name = "%s.%s.%s.zip" % (APPNAME, VERSION, self.version)
                self.run_no_encrypt()
        except Exception, e:
            traceback.print_exc()
        finally:
            self.do_remove_work_dir()

    def do_copy_work_dir(self):
        cmd = 'cp -r %s %s' % (BASEPATH, WORK_PATH)
        os.system(cmd)

    def do_remove_work_dir(self):
        cmd = 'rm %s -rf' % (APP_WORK_PATH)
        os.system(cmd)
        # print 'remove %s successfully...' % (APP_WORK_PATH)

    def __get_svn(self):
        svnPath = BASEPATH
        svn_revision = None
        try:
            cmd = 'cd %s && svn info'%(svnPath)
            svnContent = os.popen(cmd).read()
            lang = os.popen('echo $LANG').read()
            if 'en_US' in lang:
                revision = 'Rev'
            elif 'zh_CN' in lang:
                revision = '最后修改的版本'
            else:
                print 'system language is not found'
                sys.exit(1)
            svnRe = re.compile('%s: (\d*?)\n'%(revision,))
            svn_revision = svnRe.findall(svnContent)[0]
            print 'svn_revision : %s cmd : %s' % (svn_revision, cmd)
        except Exception, e:
            print 'get SVN revision Failed. %s' % (str(e))
            sys.exit(1)
        return svn_revision

    def __get_encrypt_conf(self):
        sections_dict = dict()
        conf_path = os.path.normpath(os.path.join(APP_WORK_PATH, 'target', 'encrypt_conf'))
        if not os.path.exists(conf_path):
            print 'conf file is not exists...'
            return
        try:
            cf = ConfigParser.ConfigParser()
            cf.read(conf_path)
            sections = cf.sections()
            for section in sections:
                options = cf.options(section)
                options_dic = dict()
                for option in options:
                    try:
                        value = cf.get(section, option).decode('utf-8', 'ignore')
                    except Exception, e:
                        value = cf.get(section, option)
                    options_dic[option] = value
                sections_dict[section] = options_dic
        except Exception, e:
            print 'error', str(e)
        try:
            self.is_dat = int(sections_dict['encrypt'].get('is_dat', 0))
        except:
            pass
        try:
            self.is_pyc = int(sections_dict['encrypt'].get('is_pyc', 0))
        except:
            pass
        try:
            self.is_front_pac = int(sections_dict['encrypt'].get('is_front_pac', 0))
        except:
            pass
        try:
            self.is_front_enc = int(sections_dict['encrypt'].get('is_front_enc', 0))
        except:
            pass

    def __prepare(self):
        print "prepareing .................. "
        os.system('cd %s && svn up' % (BASEPATH))
        time.sleep(1)
        print "prepare end ................. "

    def __do_encrypt_file(self):
        for root, dirs, files in os.walk(APP_WORK_PATH):
            if root in PYC_NOT_ENCNRYPT_LIST['paths']:
                continue
            for fname in files: 
                pyPath = os.path.normpath(os.path.join(root, fname))
                if not fname.endswith('.py') : 
                    continue
                if pyPath in PYC_NOT_ENCNRYPT_LIST['files']:
                    continue
                cmd = "python '%s' '%s'" % (ENCRYPT_FILE, pyPath)
                os.system(cmd)
                print cmd
                os.remove(pyPath)

    def __set_package_name(self):
        try:
            app_version_file = os.path.normpath(os.path.join(APP_WORK_PATH, 'conf', 'buildversion'))
            with open(app_version_file, 'w') as fw:
                fw.write(self.version) 
        except Exception, e:
            print e

    def __do_build_front_pac(self):
        print "package front code..."
        try:
            os.chdir(STATIC_DIR)
            cmd = "npm run build"
            os.system(cmd)
        except Exception, e:
            print traceback.print_exc()

    def __do_build_front_enc(self):
        print "encrypt front code..."
        try:
            os.chdir(STATIC_DIR)
            cmd = "npm run buildug"
            os.system(cmd)
        except Exception, e:
            print traceback.print_exc()


    def __do_build_jar(self):
        pass

    def __info(self):
        print '\033[0;33m'
        print "*********************************"
        print "package ok. "
        print "package name:", self.package_name
        outputfile = os.path.join(PACKAGE_OUTPUT_PAHT, self.package_name)
        md5 = os.popen("md5sum %s" % (outputfile)).readlines()[0].strip()
        print "package path:", md5.split(' ')[-1]
        print "package md5:", md5.split(' ')[0]
        print '>>>>>>', 'is_dat:', 'yes' if self.is_dat else 'no'
        print '>>>>>>', 'is_pyc:', 'yes' if self.is_pyc else 'no'
        print '>>>>>>', 'is_front_enc:', 'yes' if self.is_front_enc else 'no'
        print '>>>>>>', 'is_front_pac:', 'yes' if self.is_front_pac else 'no'
        print "*********************************"
        print '\033[0m'

    def run_encrypt(self):
        print "package ..."
        os.chdir(WORK_PATH)
        if self.is_pyc:
            install_name = 'install.pyc'
        else:
            install_name = 'install.py'
        os.system("mv %s/%s ." % (APPNAME, install_name))
        os.system("tar -zcf %s %s/ %s  --exclude=.svn --exclude=%s/target > /dev/null " % (self.package_name, APPNAME, install_name, APPNAME))
        replace_reg = re.compile(r'tar.gz$')
        output_name = replace_reg.sub('dat', self.package_name)
        do_encrypt = CryptApp(self.package_name, output_name)
        do_encrypt.encrypt_app()
        #删除 tar包  保留加密包
        os.system("rm -rf %s " % (self.package_name))
        os.system("mv %s %s" % (install_name, APPNAME))
        os.system("mv %s %s -f" % (output_name, DIRPATH))
        self.package_name = output_name
        self.__info()

    def run_no_encrypt(self):
        print "package ..."
        os.chdir(WORK_PATH)
        if self.is_pyc:
            install_name = 'install.pyc'
        else:
            install_name = 'install.py'
        os.system("mv %s/%s ." % (APPNAME, install_name))
        os.system("zip -r %s %s/ %s  -x '*/.svn/*' '%s/target/*' '%s/java/*' '%s/analyzers_src/*' > /dev/null" % (self.package_name, APPNAME, install_name, APPNAME, APPNAME, APPNAME))
        os.system("mv %s %s" % (install_name, APPNAME))
        os.system("mv %s %s -f" % (self.package_name, DIRPATH))
        self.__info()

def usage():
    print "usage:"
    print "python package.py        ----   run script without a parameter, make a not encrypted package"
    print "python package.py 1      ----   run script with a parameter,eg:'1',make a encrypted package"

if __name__ == '__main__':

    '''
    若不传参数 则不加密打包 后缀为.zip，若传1个参数 则加密打包 后缀为.dat

    '''
    main_param = sys.argv

    if len(main_param) == 2:
        Package(1)
    elif len(main_param) == 1:
        Package()
    else:
        usage()
