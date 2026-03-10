; This patch changes both of Dampa's Pig minigames so they can only be completed once, 
; thus allowing safe randomization without duplicating certain progression items.
; Removes unnecessary restrictions for minigame 1.

.open "files/rels/d_a_npc_people.rel"

; Bypasses the intro dialogue to allow immediate access to both minigames, skips setting of flag 2440 so it can be repurposed later
.org 0x7128
  b 0x7144

; MG1: Block replay if flag 0x2A04 is set instead of checking flag 2680; also removes the day lock.
.org 0x71C8
  li r4, 0x2A04

; MG1: Replace the "come back tomorrow" dialogue to intro dialogue
; to avoid confusing players into thinking it can be replayed.
.org 0x71D8
  addi r0, r30, 0x1B64

; MG1: Bypass the 80 Rupee limit to start the minigame.
.org 0x71F4
  b 0x7204

; MG2: Repurposed flag 2440 to trigger upon completing MG2 instead of the intro dialogue.
.org 0x70FC
  b 0x7134

; MG2: Block replay if flag 2440 is set (inverted behavior).
.org 0x8AB0
  bne 0x8AD8

.close