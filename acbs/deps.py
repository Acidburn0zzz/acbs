from .pm import PackageManager
from acbs.utils import ACBSGeneralError, format_packages
import logging


class Dependencies(object):

    def __init__(self):
        self.acbs_pm = PackageManager()
        self.retry = 0
        self.missing = []

    def search_deps(self, search_pkgs):
        pkgs_miss = self.acbs_pm.query_current_miss_pkgs(search_pkgs)
        pkgs_to_install = self.acbs_pm.query_online_pkgs(pkgs_miss)
        pkgs_not_avail = (set(pkgs_miss) - set(pkgs_to_install))
        if pkgs_not_avail:
            return [], pkgs_not_avail
        return pkgs_to_install, []

    def process_deps(self, build_deps, run_deps, pkg_slug):
        return self.process_deps_main(build_deps, run_deps, pkg_slug)

    def process_deps_main(self, build_deps, run_deps, pkg_slug):
        if build_deps:
            logging.info('Build dependencies: ' + format_packages(*build_deps))
        logging.info('Dependencies: ' + format_packages(*run_deps))
        search_pkgs_tmp = (build_deps + run_deps)
        search_pkgs = []
        logging.debug('Searching dependencies: {}'.format(search_pkgs_tmp))
        for i in search_pkgs_tmp:
            if i == pkg_slug:
                _, pkgs_not_avail = self.search_deps([i])
                if pkgs_not_avail:
                    raise ACBSGeneralError(
                        "The package can't depends on its self, and no binary package  is found!")
                else:
                    logging.warning(
                        'The package depends on its self, but it has a binary package.')
            if not i.strip():
                continue
            search_pkgs.append(i)
        pkgs_to_install, self.missing = self.search_deps(search_pkgs)
        if not pkgs_to_install:
            logging.info('No packages to install.')
            return self.missing
        logging.info('Will install {} as required.'.format(
            format_packages(*pkgs_to_install)))
        try:
            self.acbs_pm.install_pkgs(pkgs_to_install)
            pkgs_to_install = []
        except Exception:
            self.retry += 1
            logging.warning("Can't install: " + format_packages(*pkgs_to_install))
        return self.missing + pkgs_to_install
