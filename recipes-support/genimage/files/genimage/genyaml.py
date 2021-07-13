#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
#
# Copyright (C) 2020 Wind River Systems, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import sys
import logging
import argcomplete
import glob
import yaml

from genimage.utils import set_logger
from genimage.genXXX import GenXXX
from genimage.genXXX import set_parser

import genimage.constant as constant
from genimage.constant import DEFAULT_MACHINE
from genimage.constant import DEFAULT_PACKAGES
from genimage.constant import OSTREE_INITRD_PACKAGES
from genimage.constant import DEFAULT_CONTAINER_PACKAGES
from genimage.constant import DEFAULT_IMAGE
from genimage.constant import DEFAULT_INITRD_NAME
from genimage.constant import DEFAULT_CONTAINER_NAME
from genimage.constant import DEFAULT_OCI_CONTAINER_DATA
from genimage.constant import DEFAULT_IMAGE_FEATURES

from genimage.genimage import GenImage
from genimage.genimage import GenYoctoImage
from genimage.genimage import GenExtDebImage
from genimage.geninitramfs import GenYoctoInitramfs
from genimage.geninitramfs import GenExtDebInitramfs
from genimage.gencontainer import  GenYoctoContainer
from genimage.gencontainer import  GenExtDebContainer

import genimage.utils as utils

logger = logging.getLogger('appsdk')

def set_parser_genyaml(parser=None):
    supported_types = [
        'wic',
        'vmdk',
        'vdi',
        'ostree-repo',
        'container',
        'initramfs',
        'ustart',
    ]

    if DEFAULT_MACHINE == "intel-x86-64":
        supported_types.append('iso')

    parser = set_parser(parser, supported_types)
    parser.add_argument('-g', '--gpgpath',
        default=None,
        help='Specify gpg homedir, it overrides \'gpg_path\' in Yaml, default is /tmp/.lat_gnupg',
        action='store')

    parser.add_argument('--ostree-remote-url',
        default=None,
        help='Specify ostree remote url, it overrides \'ostree_remote_url\' in Yaml, default is None',
        action='store').completer = complete_url

    return parser

def complete_url(**kwargs):
    return ["http://", "https://"]

genclass = {
    "genimage": {"rpm": GenYoctoImage, "deb":GenYoctoImage, "external-debian":GenExtDebImage},
    "gencontainer": {"rpm": GenYoctoContainer, "deb":GenYoctoContainer, "external-debian":GenExtDebContainer},
    "geninitramfs": {"rpm": GenYoctoInitramfs, "deb":GenYoctoInitramfs, "external-debian":GenExtDebInitramfs}
}

class GenYaml():
    """
    * Use Input Yaml and command option to customize and generate new Yaml file:
    """
    def __init__(self, args):
        self.gen_type = self._get_gen_type(args)
        self.pkg_type = GenImage._get_pkg_type(args)
        self.generator = genclass[self.gen_type][self.pkg_type](args)

        self.generator.output_yaml = os.path.join(
             self.generator.outdir, "%s-%s.yaml" % (self.generator.data['name'],
                                                    self.generator.data['machine']))

    def _get_gen_type(self, args):
        '''
        According to image_type, get generator type:
        genimage for any of ostree_repo, wic, ustart, vmdk, vid
        gencontainer for container
        geninitramfs for initramfs
        '''
        image_types = []

        # Colloect image_type from input yamls
        if args.input:
            for input_glob in args.input:
                if not glob.glob(input_glob):
                    continue
                for yaml_file in glob.glob(input_glob):
                    with open(yaml_file) as f:
                        d = yaml.load(f, Loader=yaml.FullLoader) or dict()
                        if 'image_type' in d:
                            image_types.extend(d['image_type'])

        # Use option --type to override
        if args.type:
            image_types = args.type

        if any([i == t for i in image_types for t in ['ostree_repo', 'wic', 'ustart', 'vmdk', 'vdi']]):
            return "genimage"
        elif 'container' in image_types:
            return "gencontainer"
        elif 'initramfs' in image_types:
            return "geninitramfs"

        return "genimage"

    def do_generate(self):
        self.generator._save_output_yaml()
        logger.info("Save Yaml FIle to : %s" % (self.generator.output_yaml))

def _main_run_internal(args):
    yaml = GenYaml(args)
    yaml.do_generate()

def _main_run(args):
    try:
        ret = _main_run_internal(args)
    except Exception as e:
            logger.error(e)
            raise

def main_genyaml():
    parser = set_parser_genyaml()
    parser.set_defaults(func=_main_run)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    set_logger(logger, level=args.loglevel, log_path=args.logdir)
    args.func(args)

def set_subparser_genyaml(subparsers=None):
    if subparsers is None:
        sys.exit(1)
    parser_genimage = subparsers.add_parser('genyaml', help='Generate Yaml file from Input Yamls')
    parser_genimage = set_parser_genyaml(parser_genimage)
    parser_genimage.set_defaults(func=_main_run)

if __name__ == "__main__":
    main_genyaml()
