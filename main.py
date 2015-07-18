#!/usr/bin/env python
import sys

# allow this script to be executed as a child of another script (lsprofcalltree, for example)
sys.path.insert(0, '.')

from friture.analyzer import main

main()