#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gam_gate as gam

# ------------------------------------------------------
gam.warning('Compare root singles')
root_ref = 'output/output1.root'
root_offline = 'output/output1-singles.root'

checked_keys = ['time', 'energy',
                'globalPosX', 'globalPosY', 'globalPosZ']
scalings = [1] * len(checked_keys)
tols = [0.01] * len(checked_keys)
tols[0] = 0.02  # time
tols[1] = 0.001  # energy
tols[2] = 0.8  # globalPosX
tols[3] = 0.4  # globalPosY
tols[4] = 0.2  # globalPosZ
is_ok = gam.compare_root3(root_ref, root_offline,
                          "Singles", "Singles",
                          checked_keys, checked_keys,
                          tols, scalings, scalings,
                          'output/main1_root_singles.png')
print(is_ok)


# ------------------------------------------------------
# not yet possible to compare

'''print()
gam.warning('Compare root coinc')
root_ref = 'output/output1.root'
root_offline = 'output/output1-coinc.root'

checked_keys = ['time', 'energy',
                'globalPosX', 'globalPosY', 'globalPosZ']
scalings = [1] * len(checked_keys)
tols = [0.01] * len(checked_keys)
tols[0] = 0.02  # time
tols[1] = 0.001  # energy
tols[2] = 0.8  # globalPosX
tols[3] = 0.4  # globalPosY
tols[4] = 0.2  # globalPosZ

print(scalings, tols)
is_ok = gam.compare_root3(root_ref, root_offline,
                          "Coincidences", "Coincidences",
                          checked_keys, checked_keys,
                          tols, scalings, scalings,
                          'output/main1_root_singles.png')
print(is_ok)'''
