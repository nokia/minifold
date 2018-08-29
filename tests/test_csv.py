#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pprint             import pprint
from minifold.csv       import CsvConnector

from minifold.where     import where
from minifold.group_by  import group_by
from minifold.select    import select
from minifold.sort_by   import sort_by

if __name__ == "__main__":
    filename = "/home/mando/git/gitolite/space_temp_alarm/BTS_Syslog_10.16.214.44_23_9_2015_10_20_13_40.csv"
    connector = CsvConnector(filename, delimiter=',', quotechar='"')

    alarms = sort_by(
        ["timestamp"],
        select(
            where(
                connector.m_entries,
                lambda e: e["severity"] in ["VIP", "WRN", "ERR"]
            ),
            ["timestamp", "process_id", "print_id"]
        )
    )

    aggregat = group_by(["process_id"], alarms)
    pprint(aggregat)

    sys.exit(0)

