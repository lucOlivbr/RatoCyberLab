# -*- coding: utf-8 -*-
"""Regera só os fundos das salas (sem mexer nos sprites do rato). Uso: python3 rooms_bg.py [ids...]"""
import sys
import art_build as A
from rooms_def import ROOMS
only = [int(a) for a in sys.argv[1:]]
for r in ROOMS:
    if only and r["id"] not in only:
        continue
    A.save(A.build_room_bg(r), "world", f"bg_{r['id']:02d}.png")
print("fundos ok")
