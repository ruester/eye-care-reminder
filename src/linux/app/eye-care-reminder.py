#!/usr/bin/env python3
"""Eye Care Reminder for Linux. Started by the launcher the installer creates."""

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from eye_care_reminder.main import main  # noqa: E402

sys.exit(main(sys.argv, APP_DIR))
