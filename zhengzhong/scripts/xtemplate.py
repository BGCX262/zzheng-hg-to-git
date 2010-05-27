#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#

from __future__ import with_statement
import logging
import os
import sys
from xml.dom import minidom


_IGNORE = (
    "&#", "&bull;", "&copy;", "&nbsp;", "&raquo;", "&laquo;",
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
)


def check_template(template_file):
    logging.info("Checking: %s ..." % template_file)
    good = False
    error = None
    with open(template_file) as f:
        try:
            content = f.read()
            for ignore in _IGNORE:
                content = content.replace(ignore, "[ignored]")
            xml_str = "<root>" + content + "</root>"
            try:
                xdoc = minidom.parseString(xml_str)
                good = True
                error = None
            except Exception, exc:
                logging.error("Invalid XHTML found in %s: %s" % (template_file, exc))
                good = False
                error = str(exc)
        except Exception, exc:
            logging.error("Error checking %s: %s" % (template_file, exc))
            good = False
            error = str(exc)
        finally:
            f.close()
    return (good, error)


def check_templates(template_dir):
    checked = 0
    ignored = 0
    bad_templates = []
    for dir_path, dir_names, file_names in os.walk(template_dir):
        for file_name in file_names:
            template_file = os.path.join(dir_path, file_name)
            if template_file.lower().endswith(".html"):
                good, error = check_template(template_file)
                if not good:
                    bad_templates.append((template_file, error))
                checked += 1
            else:
                ignored += 1
    failed = len(bad_templates)
    logging.info("%d bad templates found in %d files (%d ignored)." % (failed, checked, ignored))
    if bad_templates:
        for template_file, error in bad_templates:
            logging.error(template_file)
            logging.error("  --> " + error)


def main(argv=None):
    """
    Main entry point.
    """

    # Get template top directory.
    argv = argv or sys.argv[1:]
    if len(argv) == 1:
        template_dir = argv[0]
    else:
        template_dir = os.getcwd()
    # Configure logging, set logging level to INFO.
    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(logging.DEBUG)
    # Check templates.
    check_templates(template_dir)


if __name__ == "__main__":
    main()


# EOF
