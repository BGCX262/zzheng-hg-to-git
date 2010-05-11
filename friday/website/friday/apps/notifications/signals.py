#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-28.
# $Id$
#

from django.dispatch import Signal


something_happened = Signal(providing_args=["subject", "message", "author", "recipients"])


# EOF
