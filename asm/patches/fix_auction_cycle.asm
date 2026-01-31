; Replace the random auction item selection with a simple
; deterministic cycling selection. Each auction increments the index,
; cycling through items in ascending starting bid price order.

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
  ; r3 contains 'this' pointer on entry, but we don't need it
  ; We only need to return the item index (0-3) in r3
  
  ; Load current cycle index.
  ; auction_cycle_index is defined in custom_data.asm (sys/main.dol)
  ; so it persists even when d_a_auction.rel is unloaded.
  lis r4, auction_cycle_index@ha
  addi r4, r4, auction_cycle_index@l
  lbz r5, 0(r4)         ; r5 = current cycle position (0-3)
  
  ; Increment cycle index for next auction
  addi r6, r5, 1
  andi. r6, r6, 3       ; Wrap at 4
  stb r6, 0(r4)         ; Store incremented index
  
  ; Map cycle position to array index using lookup table
  lis r4, auction_price_order@ha
  addi r4, r4, auction_price_order@l
  lbzx r3, r4, r5       ; r3 = l_item_dat array index
  
  blr

; Mapping from cycle position to l_item_dat array index
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
