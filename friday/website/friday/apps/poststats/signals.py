#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-18.
# $Id$
#

from django.dispatch import Signal


post_received = Signal(providing_args=["subject", "poster", "recipients"])


# EOF
