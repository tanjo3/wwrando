; Replace the random auction item selection with a deterministic
; cycling selection that skips already-obtained items.
;
; The auction cycle will only reset to 0 when a save file is loaded.
; If map select is used from the title screen, then the auction won't reset to the first item
; and will continue cycling from the last item index used until a save file is loaded.

.open "files/rels/d_a_auction.rel" ; Auction controller

; Replace getItemNo with a branch to our custom function
; Symbol getItemNo is at .text:0x3754. File offset of .text starts at 0xF4.
; File offset = 0x3754 + 0xF4 = 0x3848.
.org 0x3848 ; Start of getItemNo__11daAuction_cFv in file
  b custom_getItemNo

; Custom getItemNo function in free space
.org @NextFreeSpace

.global custom_getItemNo
custom_getItemNo:
  ; Prologue - save LR and callee-saved registers
  stwu sp, -0x30(sp)
  mflr r0
  stw r0, 0x34(sp)
  stw r31, 0x2C(sp)  ; auction_event_bits base
  stw r30, 0x28(sp)  ; auction_price_order base
  stw r29, 0x24(sp)  ; loop counter (0-3)
  stw r28, 0x20(sp)  ; starting cycle position
  stw r27, 0x1C(sp)  ; current item index being checked

  ; r31 = auction_event_bits base address
  lis r31, auction_event_bits@ha
  addi r31, r31, auction_event_bits@l

  ; r30 = auction_price_order base address
  lis r30, auction_price_order@ha
  addi r30, r30, auction_price_order@l

  ; r28 = starting cycle position
  lis r4, auction_cycle_index@ha
  addi r4, r4, auction_cycle_index@l
  lbz r28, 0(r4)

  ; r29 = loop counter (try up to 4 items)
  li r29, 0

.check_item_loop:
  ; Calculate check position = (start + counter) & 3
  add r4, r28, r29
  andi. r4, r4, 3

  ; r27 = item array index from price order table
  lbzx r27, r30, r4

  ; Load event bit for this item index (2 bytes per entry)
  slwi r5, r27, 1
  lhzx r4, r31, r5

  ; Check if item is obtained using isEventBit
  ; r3 = event data address, r4 = event bit flag
  lis r3, 0x803C522C@ha
  addi r3, r3, 0x803C522C@l
  bl isEventBit__11dSv_event_cFUs

  ; If r3 == 0, item not obtained - use it
  cmpwi r3, 0
  beq .found_unobtained_item

  ; Item already obtained, try next
  addi r29, r29, 1
  cmpwi r29, 4
  blt .check_item_loop

  ; All 4 items obtained - use first item in cycle order as fallback
  lbzx r27, r30, r28
  b .update_cycle_index

.found_unobtained_item:
  ; Update r28 to reflect which cycle position we used
  add r28, r28, r29
  andi. r28, r28, 3

.update_cycle_index:
  ; Store next cycle position for the next auction
  addi r4, r28, 1
  andi. r4, r4, 3
  lis r5, auction_cycle_index@ha
  addi r5, r5, auction_cycle_index@l
  stb r4, 0(r5)

  ; Return item index in r3
  mr r3, r27

  ; Epilogue - restore registers
  lwz r27, 0x1C(sp)
  lwz r28, 0x20(sp)
  lwz r29, 0x24(sp)
  lwz r30, 0x28(sp)
  lwz r31, 0x2C(sp)
  lwz r0, 0x34(sp)
  mtlr r0
  addi sp, sp, 0x30
  blr

; Event bits for each l_item_dat entry, used to check if item was obtained.
; These correspond to l_item_dat[i].mObtainedEventBit from the original code.
.global auction_event_bits
auction_event_bits:
  .short 0x0F01  ; Index 0: Joy Pendant
  .short 0x1080  ; Index 1: Treasure Chart 27
  .short 0x1040  ; Index 2: Treasure Chart 18
  .short 0x1020  ; Index 3: Heart Piece

; Mapping from cycle position to l_item_dat array index.
; This orders items by ascending starting bid price:
;   Cycle 0 -> Array 1 (Treasure Chart 27, 5 rupees)
;   Cycle 1 -> Array 0 (Joy Pendant, 40 rupees)
;   Cycle 2 -> Array 2 (Treasure Chart 18, 60 rupees)
;   Cycle 3 -> Array 3 (Heart Piece, 80 rupees)
.global auction_price_order
auction_price_order:
  .byte 1, 0, 2, 3

.align 2

.close
