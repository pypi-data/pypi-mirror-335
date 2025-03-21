# sources.py
# Copyright (C) 2022 Red Hat, Inc.
#
# Authors:
#   Akira TAGOH  <tagoh@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Module to deal with source files."""

import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import zipfile
from lxml import etree
from pathlib import Path
try:
    import _debugpath  # noqa: F401
except ModuleNotFoundError:
    pass
from fontrpmspec import font_reader as fr
from fontrpmspec.messages import Message as m
from urllib.parse import urlparse, parse_qs
from typing import Iterator, Any


def unpack_zip(fn, path, *args):
    """Unpack ZIP file."""
    d = Path(path)
    if not d.exists():
        d.mkdir(parents=True)

    zipf = zipfile.ZipFile(fn, 'r')
    for fn in zipf.namelist():
        fixedfn = os.path.join(
            *list(filter(lambda x: x != '..',
                         Path(os.path.normpath(fn)).parts))) if fn.startswith(
                             '..') else fn
        if fn != fixedfn:
            m([': ', '']).info(fn).warning(
                ('This file are going to be created outside of '
                 'the extracted directory. adjusting...')).out()
        info = zipf.getinfo(fn)
        if info.is_dir():
            (d / fixedfn).mkdir(parents=True)
        else:
            with zipf.open(fn) as i, (d / fixedfn).open(mode='wb') as o:
                shutil.copyfileobj(i, o)
    zipf.close()


def unpack_rpm(fn, path, *args):
    """Unpack RPM file."""
    d = Path(path)
    if not d.exists():
        d.mkdir(parents=True)

    os.chdir(path)
    rpm2cpiocmd = shutil.which('rpm2cpio')
    if rpm2cpiocmd is None:
        m([': '
           ]).info('rpm2cpio').error('command not found.').throw(RuntimeError)
    rpm2cpio = subprocess.Popen([rpm2cpiocmd, fn], stdout=subprocess.PIPE)
    subprocess.check_call(('cpio', '-i', '-d'),
                          stdin=rpm2cpio.stdout,
                          stderr=subprocess.DEVNULL)
    rpm2cpio.communicate()
    if rpm2cpio.returncode != 0:
        m([': ']).error('Unpacking RPM failed with return code').message(
            rpm2cpio.returncode).throw(RuntimeError)


try:
    shutil.unregister_unpack_format('rpm')
except KeyError:
    pass
shutil.register_unpack_format('rpm', ['.rpm'],
                              unpack_rpm,
                              description='Unpack RPM')
try:
    shutil.unregister_unpack_format('zip')
except KeyError:
    pass
shutil.register_unpack_format('zip', ['.zip'],
                              unpack_zip,
                              description='Custom ZIP unpacker')


class File:
    """File class to deal with files in archive."""

    def __init__(self, fn: str, prefixdir: str, is_source: bool = False):
        """Initialize `File`."""
        self._filename = fn
        self._prefixdir = prefixdir
        self.__families = None
        self.__aliases = None
        self.__langs = None
        self.__is_source = is_source

    def __name(self, name):
        p = Path(name)
        d = p.parent
        n = p.name
        if not d.parts[1:]:
            if d == '.':
                return str(d / n)
            else:
                return n
        else:
            return str(d.relative_to(*d.parts[:1]) / n)

    @property
    def name(self) -> str:
        """Obtain filename."""
        u = urlparse(self.realname, allow_fragments=True)
        if not u.scheme:
            return self.__name(self.realname)
        elif u.fragment:
            return Path(u.fragment).name
        elif u.query:
            return Path(u.query).name
        else:
            return Path(u.path).name

    @property
    def realname(self) -> str:
        """Obtain filename as it is."""
        return self._filename

    @property
    def fullname(self) -> str:
        """Obtain filename with fullpath."""
        u = urlparse(self.realname, allow_fragments=True)
        f = Path(self.prefix) / (self.realname if not u.scheme else self.name)
        if f.is_symlink():
            sym = f.readlink()
            if not sym.is_relative_to(self.prefix):
                # Symlink may points to the absolute path.
                f = Path(self.prefix) / sym.relative_to('/')
        return f

    @property
    def prefix(self):
        """Obtain prefix directory."""
        return self._prefixdir

    @property
    def family(self) -> str | None:
        """Obtain family name if available. otherwise `None`."""
        retval = self.families
        if retval is not None:
            return retval[0]
        else:
            return None

    @property
    def alias(self) -> str | None:
        """Obtain alias name if available. otherwise `None`."""
        retval = self.aliases
        if retval is not None:
            return retval[0]
        else:
            return None

    @property
    def families(self) -> list[str] | None:
        """Obtain the list of family names if available. otherwise `None`."""
        if self.is_fontconfig():
            if self.__families is None:
                tree = etree.parse(self.fullname)
                family_list = tree.xpath(
                    '/fontconfig/alias[not(descendant::prefer)]/family/text()')
                if not family_list:
                    family_list = tree.xpath(
                        ('/fontconfig/match/edit[@name=\'family\']'
                         '/string/text()'))
                    if not family_list:
                        raise ValueError(
                            m([': ']).info(self.name).error(
                                'Unable to guess the targeted family name'))
                fmap = self.family_map()
                if fmap:
                    for k, v in fmap.items():
                        if k in family_list:
                            family_list.append(v)

                family_list = list(set(family_list))
                family_list = [s.strip() for s in family_list]
                family_list.sort(key=lambda s: len(s))
                if len(family_list) > 1:
                    basename = family_list[0]
                    error = []
                    for f in family_list[1:]:
                        if not re.search(r'^{}'.format(basename), f):
                            error.append(f)
                    if len(error):
                        m([': ']).info(self.name).warning(
                            'Different family names detected').message(
                                error).out()
                self.__families = family_list
                return self.__families
            else:
                return self.__families
        else:
            return None

    @property
    def aliases(self) -> list[str] | None:
        """Obtain the list of alias names if available. otherwise `None`."""
        if self.is_fontconfig():
            if self.__aliases is None:
                tree = etree.parse(self.fullname)
                alias_list = tree.xpath(
                    '/fontconfig/alias/default/family/text()')
                if not alias_list:
                    alias_list = tree.xpath(
                        ('/fontconfig/match[not(@target) or contains(@target, \'pattern\')]/test[@name=\'family\']'
                         '/string/text()'))
                    if not alias_list:
                        return None

                alias_list = list(set([s.strip() for s in alias_list]))
                alias_list.sort(key=lambda s: len(s))
                if len(alias_list) > 1:
                    basename = alias_list[0]
                    error = []
                    for f in alias_list[1:]:
                        if not re.search(r'^{}'.format(basename), f):
                            error.append(f)
                    if len(error):
                        m([': ']).info(self.name).warning(
                            'Different alias names detected').message(
                                error).out()
                self.__aliases = alias_list
                return self.__aliases
            else:
                return self.__aliases
        else:
            return None

    @property
    def languages(self) -> list[str] | None:
        """Obtain the list of language names if available. otherwise `None`."""
        if self.is_fontconfig():
            if self.__langs is None:
                tree = etree.parse(self.fullname)
                lang_list = tree.xpath('/fontconfig/match/test[@name=\'lang\']/string/text()')

                lang_list = [s.strip() for s in lang_list]
                lang_list.sort(key=lambda s: len(s))
                self.__langs = lang_list
                return self.__langs
            else:
                return self.__langs
        else:
            return None

    def is_license(self) -> bool:
        """Wheter or not the targeted file is a license file."""
        LICENSES = ['OFL', 'MIT', 'GPL']
        if re.search(r'(?i:license|notice)', self.name) or re.search(
                re.compile('|'.join(LICENSES)), self.name):
            return True
        else:
            return False

    def is_doc(self) -> bool:
        """Whether or not the targeted file is a document."""
        if re.search(r'(?i:readme|news.*)', self.name):
            return True
        elif self.name.endswith('.txt') and self.name != 'requirements.txt':
            return True
        else:
            return False

    def is_font(self) -> bool:
        """Whether or not the targeted file is a font."""
        if self.name.endswith('.otf') or self.name.endswith('.otc') or self.name.endswith('.ttf') or self.name.endswith('.ttc'):
            return True
        else:
            return False

    def is_fontcollection(self) -> bool:
        """Whether or not the targeted file is a font."""
        if self.name.endswith('.otc') or self.name.endswith('.ttc'):
            return True
        else:
            return False

    def is_vf(self) -> bool:
        """Whether or not the target font file is a variable font."""
        if not self.is_font():
            return False
        fcquery = shutil.which('fc-query')
        if fcquery is None:
            raise RuntimeError('fc-query is not installed.')
        p = subprocess.Popen([fcquery, '-f', '%{variable}\n', self.fullname],
                             stdout=subprocess.PIPE)
        b = p.communicate()[0].decode('utf-8').splitlines()
        return any([i == 'True' for i in b])

    def is_fontconfig(self) -> bool:
        """Whether or not the targeted file is a fontconfig config file."""
        if re.search(r'(?i:fontconfig)',
                     self.name) or self.name.endswith('.conf'):
            return True
        else:
            return False

    def has_family_map(self) -> bool:
        """Whether or not Dict of family names are generated."""
        return self.family_map() is not None

    def family_map(self) -> dict[str, str] | None:
        """Get a table from old name to new name defined in fontconfig file."""
        if not self.is_fontconfig():
            return None
        else:
            tree = etree.parse(self.fullname)
            mapfrom = tree.xpath(
                ('/fontconfig/match[@target=\'scan\']/test[@name=\'family\']'
                 '/string/text()'))
            mapto = tree.xpath(
                ('/fontconfig/match[@target=\'scan\']/edit[@name=\'family\']'
                 '/string/text()'))
            if len(mapfrom) != len(mapto):
                return None
            else:
                familymap = {}
                for i in range(len(mapfrom)):
                    familymap[mapfrom[i]] = mapto[i]
                return familymap

    def is_source(self) -> bool:
        """Whether or not the targeted file is a source archive."""
        return self.__is_source

    def is_appstream_file(self) -> bool:
        """Whether or not the targeted file is an appstream file."""
        if self.name.endswith('.xml'):
            try:
                tree = etree.parse(self.fullname)
                s = tree.xpath('/component[@type="font"]')
                if not s:
                    return False
                else:
                    return True
            except etree.XMLSyntaxError:
                return False
        else:
            return False


class Source:
    """A Class to deal with the source archive."""

    def __init__(self, fn: str, sourcedir: str = '.'):
        """Initialize `Source` with source file."""
        self.__sourcedir = sourcedir
        self._sourcename = fn
        self._tempdir = None
        self._root = None
        self.ignore = False
        self._is_archive = False

    def __del__(self):
        """Cleanup a temporary directory where extracted source archive."""
        if self._tempdir is not None:
            self._tempdir.cleanup()

    def __iter__(self) -> Iterator[File]:
        """Implement iter(self) with `File`."""
        if not Path(self.fullname).exists():
            if self.is_downloadable:
                with requests.get(self.url, stream=True) as r:
                    r.raise_for_status()
                    with open(self.fullname, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            else:
                raise FileNotFoundError(
                    m([': ']).info(self.name).error('file not found'))
        self._tempdir = tempfile.TemporaryDirectory()
        try:
            shutil.unpack_archive(self.fullname, self._tempdir.name)
            self._is_archive = True
            for root, dirs, files in os.walk(self._tempdir.name):
                self._root = str(
                    Path(
                        *Path(root).relative_to(self._tempdir.name).parts[:1]))
                for n in files:
                    fn = str(Path(root).relative_to(self._tempdir.name) / n)
                    yield File(fn, self._tempdir.name)
        except shutil.ReadError:
            yield File(self.realname, self.__sourcedir, is_source=True)
        else:
            if self._tempdir is not None:
                self._tempdir.cleanup()
                self._tempdir = None

    def __name(self, name):
        return Path(name).name

    @property
    def name(self) -> str:
        """Obtain filename."""
        u = urlparse(self.realname, allow_fragments=True)
        if not u.scheme:
            return self.__name(self.realname)
        else:
            if u.fragment:
                return self.__name(u.fragment)
            elif u.query:
                return self.__name(u.query)
            else:
                return self.__name(u.path)

    @property
    def realname(self) -> str:
        """Obtain filename as it is."""
        return self._sourcename

    @property
    def url(self) -> str:
        """Obtain URL without querystring"""
        u = urlparse(self.realname, allow_fragments=True)
        return u._replace(query=None).geturl()

    @property
    def querystring(self) -> str:
        """Obtain QueryString"""
        u = urlparse(self.realname, allow_fragments=True)
        return parse_qs(u.query)

    @property
    def fullname(self) -> str:
        """Obtain filename with fullpath."""
        u = urlparse(self.realname, allow_fragments=True)
        f = Path(self.__sourcedir) / (self.realname if not u.scheme else self.name)
        if f.is_symlink():
            sym = f.readlink()
            if not sym.is_relative_to(self.__sourcedir):
                # Symlink may points to the absolute path.
                f = Path(self.__sourcedir) / sym.relative_to('/')
        return f

    @property
    def root(self) -> str:
        """Obtain a directory name where extracted."""
        return self._root

    def is_archive(self) -> bool:
        """Whether or not the targeted file is an archive file."""
        return self._is_archive

    @property
    def is_downloadable(self) -> bool:
        """Whether a source is downloadable"""
        u = urlparse(self.realname, allow_fragments=True)
        if re.match(r'http.*', u.scheme):
            return True
        else:
            return False


class Sources:
    """Class to deal with source files."""

    def __init__(self, arrays: list[str] = None, sourcedir: str = None):
        """Initialze `Sources` with the list of source files."""
        self._sources = []
        self.__sourcedir = sourcedir
        if arrays is not None:
            for e in arrays:
                self.add(e)

    def add(self, fn: str, sourcedir: str = None) -> int:
        """Add a source file and returns number of source files."""
        if sourcedir is None:
            sourcedir = self.__sourcedir
        self._sources.append(Source(fn, sourcedir=sourcedir))
        return len(self._sources) - 1

    def get(self, idx: int) -> str:
        """Get a source file points to `idx`."""
        return self._sources[idx]

    @property
    def length(self) -> int:
        """Get a number of the source files."""
        return len(self._sources)

    def __iter__(self) -> Iterator[list[Source]]:
        """Implement iter(self) for list of the source files."""
        yield from self._sources


def params(func):
    """Decorate function to initialize default parameters."""

    def wrapper(*args, **kwargs):
        kwargs.update(zip(func.__code__.co_varnames, args))
        # Add default values for optional parameters.
        ('excludepath' not in kwargs or
         kwargs['excludepath'] is None) and kwargs.update({'excludepath': []})

        return func(**kwargs)

    return wrapper


@params
def extract(name: str, version: str, sources: list[str], sourcedir: str,
            **kwargs: Any) -> dict[str, Any]:
    """Extract source files and gather information."""
    exdata = {
        'sources': [],
        'nsources': {},
        'docs': [],
        'licenses': [],
        'fontconfig': {},
        'fontmap': {},
        'fonts': [],
        'fontinfo': {},
        'archive': False
    }
    sources = Sources(arrays=sources, sourcedir=sourcedir)
    nsource = 20
    exists = {}
    for source in sources:
        for sf in source:
            if sf.is_license():
                exdata['licenses'].append(sf)
            elif sf.is_doc():
                exdata['docs'].append(sf)
            elif sf.is_fontconfig():
                sf.family in exdata['fontconfig'] and m([': ', ' ']).info(
                    sf.family).warning('Duplicate family name').out()
                exdata['fontconfig'][sf.family] = sf
                sf.has_family_map() and exdata['fontmap'].update(
                    sf.family_map())
                source.ignore = not source.is_archive()
            elif sf.is_font():
                found = False
                for ss in kwargs['excludepath']:
                    if sf.name.startswith(ss):
                        found = True
                        break
                if found:
                    continue
                exdata['fonts'].append(sf)
                nm = Path(sf.name).name
                if nm in exists:
                    m([': ']).info(sf.name).warning(
                        ('Possibly duplicate font files detected. '
                         'Consider to use `excludepath` option.')).out()
                    m().message(exists[nm]).out()
                else:
                    exists[nm] = []
                exists[nm].append(sf.name)
                if sf.name not in exdata['fontinfo']:
                    exdata['fontinfo'][sf.name] = fr.font_meta_reader(
                        sf.fullname)
                    exdata['foundry'] = exdata['fontinfo'][sf.name]['foundry']
                else:
                    m([': ', ' ']).info(sf.name).warning(
                        ('Duplicate font files detected. '
                         'this may not works as expected')).out()
                source.ignore = not source.is_archive()
            elif sf.is_appstream_file():
                m([': ', ' ']).info(sf.name).warning(
                    ('AppStream file is no longer needed. '
                     'this will be generated by the macro automatically'
                     )).out()
                source.ignore = not source.is_archive()
            else:
                m([': ',
                   ' ']).info(sf.name).warning('Unknown type of file').out()
                source.ignore = not source.is_archive()

        if exdata['archive'] is True and source.is_archive():
            raise AttributeError(
                m().error('Multiple archives are not supported'))
        exdata['archive'] = exdata['archive'] or source.is_archive()
        if 'root' not in exdata:
            exdata['root'] = source.root if source.root != '{}-{}'.format(
                name, version) else ''
        if not source.ignore and not source.is_archive():
            exdata['sources'].append(source.realname)
            exdata['nsources'][source.realname] = nsource
            nsource += 1

    return exdata


if __name__ == '__main__':
    s = Source('./foo.zip')
    for x in s:
        print(s.root, x.prefix, x.name, x.is_license())
    s = Source('./requirements.txt')
    for x in s:
        print(x.prefix, x.name, x.is_doc())
    s = Source('./foo.conf')
    for x in s:
        print(x.family)
