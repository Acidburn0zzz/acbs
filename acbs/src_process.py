import os
# import sys
import subprocess
# import re
import tempfile
import logging
import shutil
import hashlib
from acbs import utils
from acbs.utils import ACBSGeneralError


class SourceProcessor(object):

    def __init__(self, pkg_info, dump_loc, tmp_loc):
        self.tobj = tempfile.mkdtemp(dir=tmp_loc, prefix='acbs.')
        self.pkg_name = pkg_info.pkg_name
        self.src_loc = dump_loc
        self.src_name = pkg_info.src_name
        self.chksum_val = pkg_info.chksums
        self.src_full_loc = None
        self.shadow_ark_loc = None

    def process(self):
        if self.src_name:
            self.src_full_loc = os.path.join(self.src_loc, self.src_name)
            self.shadow_ark_loc = os.path.join(self.tobj, self.src_name)
            if not os.path.isdir(self.src_full_loc):
                self.chksum()
        else:
            return self.tobj
        if os.path.isdir(self.src_full_loc):
            logging.debug('Making a copy of the source directory...')
            try:
                logging.debug('Copy {} to {}'.format(
                    self.src_full_loc, self.shadow_ark_loc))
                shutil.copytree(src=self.src_full_loc, dst=self.shadow_ark_loc, symlinks=True, ignore=None)
            except Exception as ex:
                print('Failed!')
                raise ACBSGeneralError(
                    'Failed to make a copy of source directory!') from ex
            logging.debug('Done on making a copy!')
            return self.tobj
        else:
            os.symlink(self.src_full_loc, self.shadow_ark_loc)
            logging.debug('Source location: {}, Shadow link: {}'.format(
                self.src_full_loc, self.shadow_ark_loc))
            self.decomp_file()
            return self.tobj

    def file_type(self, file_loc=None, res_type=1):
        try:
            import magic
        except ImportError:
            logging.warning(
                'ACBS cannot find libmagic bindings, will use file utility.')
            import acbs.magic as magic
        file_loc = self.src_full_loc or file_loc
        if res_type == 1:
            mco = magic.open(magic.MIME_TYPE | magic.MAGIC_SYMLINK)
        elif res_type == 2:
            mco = magic.open(magic.NONE | magic.MAGIC_SYMLINK)
        else:
            mco = magic.open(magic.NONE)
        mco.load()
        try:
            tp = mco.file(file_loc)
            if isinstance(tp, str):
                if res_type == 1:
                    tp_res = tp.split('/')
                else:
                    tp_res = tp
            else:
                # Workaround a bug in certain version of libmagic
                if res_type == 1:
                    tp_res = tp.decode('utf-8').strip('b\'\'').split('/')
                else:
                    tp_res = tp.decode('utf-8').strip('b\'\'')
        except Exception:
            logging.error('Unable to determine the file type!')
            if res_type == 1:
                return ['unknown', 'unknown']
            else:
                return 'data'
        return tp_res

    def decomp_file(self):
        file_type_name = self.file_type()
        ext_list = ['x-tar*', 'zip*', 'x-zip*', 'tar*', 'bzip*',
                    'x-cpio*', 'x-gzip*', 'x-bzip*', 'x-xz*',
                    'x-7z*', 'x-lzip*', '7z*', 'xz*', 'gzip*',
                    'lzip*', 'cpio*']
        if (len(file_type_name[0].split('application')) > 1) and utils.group_match(ext_list, file_type_name[1], 1):
            # x-tar*|zip*|x-*zip*|x-cpio*|x-gzip*|x-bzip*|x-xz*
            pass
        else:
            logging.warning('ACBS don\'t know how to decompress {} file, will leave it as is!'.format(
                self.file_type(res_type=2)))
            return
        return self.decomp_lib()

    def decomp_ext(self):
        if not shutil.which('bsdtar'):
            raise AssertionError(
                'Unable to use bsdtar. Can\'t decompress files... :-(')
        try:
            subprocess.check_call(
                ['bsdtar', '-xf', self.shadow_ark_loc, '-C', self.tobj])
        except Exception as ex:
            raise ACBSGeneralError(
                'Unable to decompress file! File corrupted?! Or Permission denied?!') from ex

    def chksum_file(self, hash_type, target_file):
        hash_type = hash_type.lower()
        if hash_type in hashlib.algorithms_available:
            hash_obj = hashlib.new(hash_type)
        else:
            raise NotImplementedError(
                'Unsupported hash type %s! Currently supported: %s' % (
                hash_type, ' '.join(sorted(hashlib.algorithms_available))))
        with open(target_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def chksum(self):
        chksums = self.chksum_val or (('sha256', ''),)
        logging.debug('Checksums: %s' % chksums)
        for hash_type, hash_value in chksums:
            target_hash = self.chksum_file(hash_type, self.src_full_loc)
            if not hash_value:
                raise ACBSGeneralError("No checksum is found for file %s. Suggested:\n"
                    "%s::%s", (self.src_full_loc, hash_type, target_hash))
            elif hash_value != target_hash:
                raise ACBSGeneralError('%s checksums mismatch for file %s:\n'
                    'Current %s / Downloaded %s' % (
                    hash_type, self.src_full_loc, hash_value, target_hash))
        logging.info('\033[92mChecksum matched\033[0m for %s (%s)' % (
            self.src_full_loc, hash_type))

    def decomp_lib(self):
        try:
            import libarchive
            import os
        except ImportError:
            logging.warning(
                'Failed to load libarchive library! Fall back to bsdtar!')
            return self.decomp_ext()
        # Begin
        os.chdir(self.tobj)
        try:
            libarchive.extract.extract_file(self.shadow_ark_loc)
        except Exception as ex:
            raise Exception('Extraction failure!') from ex
