
; =============================================================================
; MEDLI SHIP COMPANION PATCH
; =============================================================================
; This patch modifies Medli's create() function so that she always spawns as a
; ship companion when the player is on the "sea" stage, by removing all the
; flag-based conditions that normally restrict this.
;
; The vanilla conditions removed are:
;   1. Event flag 0x2E04 must NOT be set (Earth Temple entrance seen)
;   2. Event flag 0x1820 must be set
;   3. DRC boss must be beaten (isStageBossEnemy check)
;   4. Event flag 0x1608 must be set (Medli has joined party)
;
; After this patch, only the stage name check matters. If stage == "sea",
; Medli will spawn in ship companion mode.
;
; This preserves all other Medli functionality (Earth Temple, etc.) since those
; stages have their own type-setting logic that runs before the ship ride check.
;
; Offsets verified from TWW decompilation disassembly:
;   c:/dev/tww/build/GZLE01/d_a_npc_md/asm/d/actor/d_a_npc_md.s
; =============================================================================

.open "files/rels/d_a_npc_md.rel" ; Medli

; The create() function is at 0x884 (size 0x4FC, ends at 0xD80).
;
; PART 1: Sea stage spawn check (lines 391-396 in decompiled source)
; ===================================================================
; Original C++:
;   } else if (strcmp(dComIfGp_getStartStageName(), "sea") == 0) {
;       if (dComIfGs_isEventBit(UNK_2E04) ||     <- Check 1
;           !dComIfGs_isEventBit(UNK_1820) ||    <- Check 2
;           !dComIfGs_isStageBossEnemy(DRC))     <- Check 3
;       {
;           return cPhs_ERROR_e;
;       }
;   }
;
; Assembly at 0x9B0-0x9D4:
;   0x9B0: bne .L_000009D8  ; if 2E04 IS set, goto error
;   0x9C4: beq .L_000009D8  ; if 1820 NOT set, goto error
;   0x9D4: bne .L_00000BBC  ; if DRC boss beaten, goto SUCCESS (skip error)
;
; We NOP the first two branches and make the third unconditional.

; Check 1: bne for UNK_2E04 being set -> return error
; Original: 40 82 00 28 (bne +0x28)
; Section offset 0x9B0 -> File offset 0xAA4
.org 0xAA4
  nop  ; Was: bne .L_000009D8

; Check 2: beq for UNK_1820 NOT being set -> return error
; Original: 41 82 00 14 (beq +0x14)
; Section offset 0x9C4 -> File offset 0xAB8
.org 0xAB8
  nop  ; Was: beq .L_000009D8

; Check 3: bne for DRC boss beaten -> goto success
; We change this from conditional to unconditional so it ALWAYS succeeds.
; Original: 40 82 01 E8 (bne +0x1E8 to .L_00000BBC)
; New:      48 00 01 E8 (b +0x1E8 to .L_00000BBC)
; Section offset 0x9D4 -> File offset 0xAC8
; Branch target .L_00000BBC -> File offset 0xCB0
.org 0xAC8
  b 0xCB0  ; Was: bne .L_00000BBC - now unconditionally branch to success


; PART 2: setTypeShipRide conditional block (lines 424-428 in decompiled source)
; ==============================================================================
; Original C++:
;   if (!dComIfGs_isEventBit(UNK_2E04) &&
;       dComIfGs_isEventBit(UNK_1608)) {
;       setTypeShipRide();
;       strcpy(mModelArcName, l_arc_name_ship);
;       heapSizeIdx = 1;
;   }
;
; Problem: Simply NOPing the flag checks makes setTypeShipRide run on ALL stages,
; including dungeons where Medli should be in partner mode (mType 4/5/6).
;
; Solution: Replace the flag check code with a type check. If mType >= 4 (dungeon
; types: Edaichi=4, M_Dai=5, M_DaiB=6), skip ship mode. Otherwise, set ship mode.
;
; mType values:
;   0=Atorizk, 1=Adanmae, 2=M_Dra09, 3=Sea, 4=Edaichi, 5=M_Dai, 6=M_DaiB, 7=ShipRide
;
; Original assembly at 0xCB0-0xCCC (8 instructions):
;   lis r3, g_dComIfG_gameInfo@ha
;   addi r3, r3, g_dComIfG_gameInfo@l
;   addi r29, r3, 0x624
;   mr r3, r29
;   li r4, 0x2e04
;   bl isEventBit
;   cmpwi r3, 0
;   bne .L_00000C08   <- file offset 0xCCC
;
; We replace this with a type check that branches based on mType.
; mType is at offset 0x3138 from r28 (this pointer).

; Section offset 0xBBC -> File offset 0xCB0
.org 0xCB0
  lbz r0, 0x3138(r28)   ; Load mType
  cmpwi r0, 4           ; Compare with 4 (first dungeon type)
  bge 0xCFC             ; If mType >= 4, skip to .L_00000C08 (file offset 0xCFC)
  b 0xCE4               ; Else jump to setTypeShipRide (li r0, 7 at file offset 0xCE4)

.close
