#!/usr/bin/env python3
#
#   Post Kali Installer
#   --------------------
#   This script was built for simple post installation of any tool needed
#   after the initial installation of the regular 64 bit version of Kali Linux.
#
#   For configuring this script according to your own needs please review the packages in the
#   _apt_packages(), _git_packages(), __wget_packages() methods and change them according to your preferred
#   configuration. If you are new to Kali Linux then you should be ok running the vanilla configuration.
#
#
#   Author: Zorko
#   Year:   2018
#   Contact: contact@zorko.co
#   Website: www.zorko.co
#
import os
import sys
import logging
import datetime as dt
from subprocess import STDOUT, check_call


class PKInstall:
    __DEBUG__ = False
    __SIMULATOR__ = False
    __ROOT_PATH__ = os.getcwd()
    __ACCESS_RIGHTS__ = 0o755
    __GIT__ = '{}/git'.format(__ROOT_PATH__)
    __TOOLS__ = '{}/tools'.format(__ROOT_PATH__)
    __SOURCES__ = {
        'apt': True,
        'git': True,
        'wget': True,
        'scripts': True
    }

    def __init__(self, args={}):
        #
        # Set tools root directory
        if 'root' in args:
            self.__ROOT_PATH__ = args['root'].strip('/')

        self.__GIT__ = '{}/git/'.format(self.__ROOT_PATH__)
        self.__TOOLS__ = '{}/tools/'.format(self.__ROOT_PATH__)

        if self.__ROOT_PATH__ != os.getcwd():
            os.chdir(self.__ROOT_PATH__)

        if 'SIMULATOR' in args:
            if args['SIMULATOR']:
                self.__SIMULATOR__ = True
        #
        # Set log-level
        if 'DEBUG' in args:
            if args['DEBUG']:
                self.__DEBUG__ = True
                log_level = logging.DEBUG
            else:
                log_level = logging.INFO
        else:
            log_level = logging.INFO

        logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', filename='{}/pk_install.log'.format(self.__ROOT_PATH__), level=log_level)
        logging.info('Started running PK Installer at {}'.format(dt.datetime.now()))
        if 'skip' in args:
            if 'apt' in args['skip']:
                if args['skip']['apt']:
                    self.__SOURCES__['apt'] = False

            if 'git' in args['skip']:
                if args['skip']['git']:
                    self.__SOURCES__['git'] = False

            if 'wget' in args['skip']:
                if args['skip']['wget']:
                    self.__SOURCES__['wget'] = False

            if 'scripts' in args['skip']:
                if args['skip']['scripts']:
                    self.__SOURCES__['scripts'] = False

        #
        # Set directory rights
        if 'access_rights' in args:
            print('args access_rights:', type(args['access_rights']))
            self.__ACCESS_RIGHTS__ = args['access_rights']

        if self.__DEBUG__:
            msg = "\n\tROOT PATH: {},\n\t" \
                  "ACCESS RIGHTS: {},\n\t" \
                  "INSTALL SOURCES: \n\t\t" \
                  "apt: {},\n\t\t" \
                  "git: {},\n\t\t" \
                  "wget: {},\n\t\t" \
                  "scripts: {},\n\t\t" \
                  "SIMULATOR MODE: {}\n\t\t" \
                  "LOG LEVEL: {}".format(self.__ROOT_PATH__,
                                         self.__ACCESS_RIGHTS__,
                                         self.__SOURCES__['apt'],
                                         self.__SOURCES__['git'],
                                         self.__SOURCES__['wget'],
                                         self.__SOURCES__['scripts'],
                                         self.__SIMULATOR__,
                                         log_level)
            logging.debug(msg)

    def install(self):
        # Prepare directory structure
        # Defaults to: ~/git/ and ~/tools/
        if self.__SIMULATOR__:
            logging.info("SIMULATOR: Running in simulator mode! "
                         "This will only dump commands which would have been run on the system. "
                         "It is recommended that this mode is run with the DEBUG config flag set for the best output")
        logging.debug('Attempting to build the directory structure')
        self.__build_dir_tree()

        if self.__SOURCES__['scripts']:
            logging.debug("Attempting to run initial scripts")
            self.__scripts_install()

        if self.__SOURCES__['apt']:
            logging.debug("Attempting to install packages with apt")
            self.__apt_install()

        if self.__SOURCES__['git']:
            logging.debug("Attempting to install packages with git")
            self.__git_install()

        if self.__SOURCES__['wget']:
            logging.debug("Attempting to install packages with wget")
            self.__wget_install()

        if self.__SOURCES__['scripts']:
            logging.debug("Attempting to run final scripts")
            self.__scripts_install(False)

        logging.info('Installation finished at {}'.format(dt.datetime.now()))
        return

    def __build_dir_tree(self):
        logging.debug("Entered self.__build_dir_tree()")

        if os.path.isdir(self.__ROOT_PATH__) and os.access(self.__ROOT_PATH__, os.W_OK):
            try:
                logging.debug("Creating git directory: {}".format(self.__GIT__))
                if not os.path.isdir(self.__GIT__):
                    if self.__SOURCES__['git']:
                        if self.__SIMULATOR__:
                            msg = "SIMULATOR: creating directory: {} " \
                                  "with the following rights {}".format(self.__GIT__, self.__ACCESS_RIGHTS__)
                            logging.info(msg)
                        else:
                            os.mkdir(self.__GIT__, self.__ACCESS_RIGHTS__)
                else:
                    logging.warning('The directory: {} already exists, using existing directory'.format(self.__GIT__))

                if os.path.isdir(self.__GIT__):
                    for path in self.__git_packages():
                        new_dir = '{}{}'.format(self.__GIT__, path)

                        if not os.path.isdir(new_dir):
                            os.mkdir(new_dir, self.__ACCESS_RIGHTS__)
                        else:
                            logging.warning('The directory {} already exists, using existing directory'.format(new_dir))

                logging.debug("Creating tools directory: {}".format(self.__TOOLS__))
                if not os.path.isdir(self.__TOOLS__):
                    if self.__SOURCES__['wget']:
                        if self.__SIMULATOR__:
                            msg = "SIMULATOR: creating directory: {} " \
                                  "with the following rights {}".format(self.__TOOLS__, self.__ACCESS_RIGHTS__)
                            logging.info(msg)
                        else:
                            os.mkdir(self.__TOOLS__, self.__ACCESS_RIGHTS__)
                else:
                    logging.warning('The directory: {} already exists, using existing directory'.format(self.__TOOLS__))
            except OSError as e:
                logging.fatal(e)
                sys.exit(e)
        return

    def __apt_install(self):
        logging.debug('Entered self.__apt_install()')
        if os.geteuid() != 0:
            logging.warning('Installing software with apt should only be done by root, skipping step...')
            return

        try:
            check_call(['apt-get', 'update'], stdout=open(os.devnull, 'wb'), stderr=STDOUT)

            for pkg in self.__apt_packages():
                logging.debug('Installing {} with apt-get'.format(pkg))
                if self.__SIMULATOR__:
                    logging.info('SIMULATOR: running command: apt-get install -y {}'.format(pkg))
                else:
                    check_call(['apt-get', 'install', '-y', pkg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
        except OSError as e:
            logging.fatal(e)
            sys.exit(e)

        logging.debug('Apt done.')
        return

    def __git_install(self):
        logging.debug('Entered self.__git_install()')
        if not self.__SIMULATOR__:
            logging.debug('Changing directory to: {}'.format(self.__GIT__))
            os.chdir(self.__GIT__)
            logging.debug('CWD: {}'.format(os.getcwd()))

        try:
            packages = self.__git_packages()
            for key in packages:
                if not self.__SIMULATOR__:
                    os.chdir('{}/{}'.format(os.getcwd(), key))

                for pkg in packages[key]:
                    if key == 'tools':
                        url = packages[key][pkg]['url']
                        cfg = packages[key][pkg]['config']

                        if not os.path.isdir('{}/{}'.format(os.getcwd(), pkg)) or self.__SIMULATOR__:
                            logging.debug('Installing {} with git'.format(url))
                            try:
                                if self.__SIMULATOR__:
                                    logging.info('SIMULATOR: running command: git clone {} {}'.format(url, pkg))
                                else:
                                    check_call(['git', 'clone', url, pkg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)

                                if cfg != '':
                                    if self.__SIMULATOR__:
                                        logging.info('SIMULATOR: running command: sh {}'.format(cfg))
                                    else:
                                        try:
                                            logging.debug('Running {} config script'.format(pkg))
                                            check_call(['sh', cfg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
                                        except OSError as e:
                                            logging.warning(e)
                            except OSError as e:
                                logging.warning(e)
                        else:
                            logging.warning('The directory {0}/{1} already exists, skipping tool {1}'.format(os.getcwd(), pkg))
                    else:
                        logging.debug('Installing {} with git'.format(pkg))
                        if self.__SIMULATOR__:
                            logging.info('SIMULATOR: running command: git clone {}'.format(pkg))
                        else:
                            try:
                                check_call(['git', 'clone', pkg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
                            except OSError as e:
                                logging.warning(e)

                if not self.__SIMULATOR__:
                    logging.debug('Changing directory to: {}'.format(self.__GIT__))
                    os.chdir(self.__GIT__)
                    logging.debug('CWD: {}'.format(os.getcwd()))
        except OSError as e:
            logging.warning(e)

        if not self.__SIMULATOR__:
            logging.debug('Changing directory to: {}'.format(self.__ROOT_PATH__))
            os.chdir(self.__ROOT_PATH__)
            logging.debug('CWD: {}'.format(os.getcwd()))
        logging.debug('Git done.')
        return

    def __wget_install(self):
        logging.debug('Entered self.__wget_install()')
        if not self.__SIMULATOR__:
            logging.debug('Changing directory to: {}'.format(self.__TOOLS__))
            os.chdir(self.__TOOLS__)
            logging.debug('CWD: {}'.format(os.getcwd()))

        try:
            for pkg in self.__wget_packages():
                logging.debug('Installing {} with wget'.format(pkg))
                if self.__SIMULATOR__:
                    logging.info('SIMULATOR: running command: wget {}'.format(pkg))
                else:
                    check_call(['wget', pkg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
        except OSError as e:
            logging.warning(e)

        if not self.__SIMULATOR__:
            logging.debug('Changing directory to: {}'.format(self.__ROOT_PATH__))
            os.chdir(self.__ROOT_PATH__)
            logging.debug('CWD: {}'.format(os.getcwd()))
        logging.debug('Wget done.')
        return

    def __scripts_install(self, initial=True):
        logging.debug('Entered self.__scripts_install()')
        try:
            if initial:
                script = self.__initial_scripts()
            else:
                script = self.__final_scripts()

            for pkg in script:
                logging.debug('Running {}'.format(pkg))
                if self.__SIMULATOR__:
                    logging.info('SIMULATOR: running command: sh {}'.format(pkg))
                else:
                    check_call(['sh', pkg], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
        except OSError as e:
            logging.warning(e)

        logging.debug('Scripts done.')
        return

    @staticmethod
    def __initial_scripts():
        logging.debug('Entered self.__initial_scripts()')
        from packages import initial_scripts
        return initial_scripts.cfg

    @staticmethod
    def __final_scripts():
        logging.debug('Entered self.__final_scripts()')
        from packages import final_scripts
        return final_scripts.cfg

    @staticmethod
    def __apt_packages():
        logging.debug('Entered self.__apt_packages()')
        from packages import apt
        return apt.cfg

    @staticmethod
    def __git_packages():
        logging.debug('Entered self.__git_packages()')
        from packages import git
        return git.cfg

    @staticmethod
    def __wget_packages():
        logging.debug('Entered self.__wget_packages()')
        from packages import wget
        return wget.cfg


if __name__ == '__main__':
    config = {

    }
    pki = PKInstall(config)
    pki.install()
