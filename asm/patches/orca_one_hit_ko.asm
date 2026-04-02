; Orca 1‑Hit KO + 1 Heart UI modifications

.open "files/rels/d_a_npc_ji1.rel"

; Change UI to only display 1 Heart
.org 0x6BBC
  li r0, 1

; Orca 1-Hit KO
.org 0xC6CC
  cmpwi r0, 0

; Change UI to not reset to display 3 Hearts after Orca start
.org 0xCB5C
  subfic r3, r0, 1

.close