; This patch makes the sail check accessible and ensures it is properly blocked after purchase, allowing it to be randomized safely.
; Repurposes the intro dialogue event bit so it can be used to block the sail purchase once bought (0x2420).
; Adjusts Zunari's dialogue behavior: 
; - If the player has the delivery bag but not the town flower, they can obtain it without purchasing the sail check first.
; - Allows the player to complete the Zunari sidequest without purchasing the sail beforehand.
; - Allows the player to buy flowers from the shop without needing to purchase the sail.

.open "files/rels/d_a_npc_rsh1.rel"

.org 0x17B0 ; NOP the branch so we always enter the sail dialogue block.
  nop

.org 0x17B4 ; Replace save data setup + isEventBit call with dComIfGs wrapper so r31 is not overwritten.
  li r3, 0x2420 ; Event bit to check.
  nop           ; was lis r3
  nop           ; was addi r3,r3,0x0
  nop           ; was addi r31,r3,0x624
  nop           ; was or r3,r31,r31
  bl dComIfGs_isEventBit__FUs ; was li r4,0x2420 + bl FUN_00000154

.org 0x17D0 ; If sail bit not set, branch to trampoline.
  beq 0x17DC

.org 0x17D4 ; If sail bit set → branch to shop dialogue.
  b 0x17F0

.org 0x17DC ; branch to our custom function. (originally part of 0x2420 setter)
  b zunari_dialogue_switcher
.org 0x17E0 ; remove original 0x2420 setter
  nop
.org 0x17E4 ; remove original 0x2420 setter
  nop

.org @NextFreeSpace
; If the sail event bit is not set, check whether to show sail dialogue or show shop/town flower dialogue.
.global zunari_dialogue_switcher
zunari_dialogue_switcher:
  stwu sp, -0x10 (sp)
  mflr r0
  stw r0, 0x14 (sp)
  
  li r3, 0x30 ; Delivery Bag item ID.
  bl dComIfGs_checkGetItem__FUc ; Check if player has the Delivery Bag.
  cmpwi r3, 0x0
  beq zunari_sail_dialogue ; No delivery bag → show sail dialogue.

  li r3, 0x6B20 ; Check if the town flower has already been obtained (Unused event bit).
  bl dComIfGs_isEventBit__FUs
  cmpwi r3, 0x0
  beq zunari_shop_dialogue ; Town flower not yet obtained → skip to shop/town flower dialogue.

  b zunari_sail_dialogue

zunari_shop_dialogue:
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  b 0x1808

zunari_sail_dialogue:
  lwz r0, 0x788 (r31) ; Check which side of the shop we're on, we need this as the sail dialogue doesn't check it normally and will block shop otherwise.
  cmpwi r0, -0x1
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  bne 0x1808 ; Right side → show shop dialogue.
  b 0x17E8 ; Left side → show sail dialogue.

.close
