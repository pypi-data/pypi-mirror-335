# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Model providing optional view() call options"""

from dataclasses import dataclass


# Implement additional option(s) in https://jira-dc.qualcomm.com/jira/browse/AISW-119343
@dataclass
class WindowOptions:
    """List of Window view() call options"""
