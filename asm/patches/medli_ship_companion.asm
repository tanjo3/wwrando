
; Allow Medli to always spawn as a ship companion on the "sea" stage by removing
; vanilla flag-based conditions from her create() function in d_a_npc_md.rel.
;
; Vanilla create() blocks sea spawn unless: 0x2E04 unset, 0x1820 set, DRC boss beaten, 0x1608 set.
; We remove all of these so only the stage=="sea" check matters.
;
; Dungeon behavior is preserved: Part 2 replaces the flag-gated setTypeShipRide()
; with an mType check so ship mode only activates for non-dungeon types (mType < 4).

.open "files/rels/d_a_npc_md.rel" ; Medli

; --- Part 1: Remove flag conditions from sea stage spawn check in create() ---
; NOP the 0x2E04 and 0x1820 branches, make the DRC boss check unconditional.

.org 0xAA4
  nop        ; Was: bne (reject if 0x2E04 set)
.org 0xAB8
  nop        ; Was: beq (reject if 0x1820 not set)
.org 0xAC8
  b 0xCB0    ; Was: bne 0xCB0 (conditional on DRC boss) -> unconditional

; --- Part 2: Replace setTypeShipRide flag check with mType check ---
; Original checked 0x2E04/0x1608 flags, which would activate ship mode on all stages.
; Instead, check mType: skip ship mode for dungeon types (>= 4), enable otherwise.
; mType: 0=Atorizk 1=Adanmae 2=M_Dra09 3=Sea 4=Edaichi 5=M_Dai 6=M_DaiB 7=ShipRide

.org 0xCB0
  lbz r0, 0x3138(r28)   ; mType
  cmpwi r0, 4
  bge 0xCFC             ; dungeon type -> skip ship mode
  b 0xCE4               ; else -> setTypeShipRide

; --- Part 3: Disable ship ride talk prompt in shipNpcAction ---
; shipRideCheck routes mType==7 here. Prevent the attention check and prompt.

.org 0x5564
  li r3, 0             ; Skip chkAttention result (no talk)

.org 0x5880
  li r4, 0             ; setAttention(false)

.close
