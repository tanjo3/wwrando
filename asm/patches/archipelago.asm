.open "sys/main.dol"
.org 0x80234FE0 ; In dScnPly_Execute
  bl      give_archipelago_item
; Every frame, check if the Archipelago client has set an item ID to give to the player.
; The byte is cleared after the item is given. We put this function in `dScnPly_Execute`, which is run every frame.
.org @NextFreeSpace
.global give_archipelago_item
give_archipelago_item:
  stwu    sp, -0x10 (sp)
  mflr    r0
  stw     r0, 0x14 (sp)
  stw     r31, 0xC (sp)
  
  ; Store value of r3 in r31
  mr      r31, r3
  
  ; Load the address of give_archipelago_item_byte into r4
  lis     r4, give_archipelago_item_byte@ha
  addi    r4, r4, give_archipelago_item_byte@l
  
  ; Load the item ID into r3
  lbz     r3, 0 (r4)
  
  ; If item ID is 0xFF, there's no item to give
  cmpwi   r3, 0xFF
  beq     give_archipelago_item_end
  
  ; Else, clear the byte to 0xFF before giving the item
  li      r5, 0xFF
  stb     r5, 0 (r4)
  
  ; Branch to execItemGet to give the item
  bl      execItemGet__FUc
  
  give_archipelago_item_end:
  ; Restore the value of r3
  mr      r3, r31
  
  lwz     r31, 0xC (sp)
  lwz     r0, 0x14 (sp)
  mtlr    r0
  addi    sp, sp, 0x10
  
  mr      r31, r3         ; this is the line we overwrote on 0x80234FE0
  
  blr

.global give_archipelago_item_byte
give_archipelago_item_byte:
  .byte 0xFF
.align 2 ; Align to the next 4 bytes


; Fix the Triforce shard message for Archipelago.
; Because normally you get the demo message before receiving the shard, the message will assume your shard count is one
; more than your current shard count. This is not true for Archipelago as you normally receive the item before the demo
; message is created. Thus, we need to decrement the return value of `dSv_player_collect_c::getTriforceNum` by one.
.org 0x80215724 ; In dMsg_Create
  b       modify_triforce_count

.org @NextFreeSpace
.global modify_triforce_count
modify_triforce_count:
  cmpwi   r3, 0
  beq     modify_triforce_count_return
  subi    r3, r3, 1       ; r3 holds the return value of `dSv_player_collect_c::getTriforceNum`
  
  modify_triforce_count_return:
  mr      r4, r3          ; this is the line we overwrote on 0x80215724
  b       0x80215728


; Allocate 0x40 bytes in memory for the player's slot name
.global archipelago_slot_name
archipelago_slot_name:
  .space 0x40
.align 2 ; Align to the next 4 bytes


; Allocate 49 shorts in memory for the charts mapping
.global archipelago_charts_mapping
archipelago_charts_mapping:
  .space 0x62
.align 2 ; Align to the next 4 bytes

.close




; Remove the execItemGet call for demo items.
; Instead, let the Archipelago client call execItemGet when the player should receive an item. However, certain items
; should still be given to Link, so we need to check for those specific items. In particular, we only skip the call to
; execItemGet if it's an item ID used by Archipelago.
.open "files/rels/d_a_demo_item.rel"
.org 0xA00
    b check_give_item

.org @NextFreeSpace
.global check_give_item
check_give_item:
  lbz     r3, 1594(r31) ; r3 = m_itemNo (This is the line we replaced.)

  ; Rupees, Piece of Heart, Heart Container
  cmpwi   r3, 0x01
  blt     call_execItemGet
  cmpwi   r3, 0x08
  ble     skip_execItemGet

  ; Silver Rupee
  cmpwi   r3, 0x0F
  beq     skip_execItemGet

  ; DRC Keys
  cmpwi   r3, 0x13
  blt     call_execItemGet
  cmpwi   r3, 0x14
  ble     skip_execItemGet

  ; DRC Dungeon Map and Compass, FW Small Key
  cmpwi   r3, 0x1B
  blt     call_execItemGet
  cmpwi   r3, 0x1D
  ble     skip_execItemGet

  ; Joy Pendant, some progression items
  cmpwi   r3, 0x1F
  blt     call_execItemGet
  cmpwi   r3, 0x2A
  ble     skip_execItemGet

  ; Bait Bag, Boomerang
  cmpwi   r3, 0x2C
  blt     call_execItemGet
  cmpwi   r3, 0x2D
  ble     skip_execItemGet

  ; Hookshot, Delivery Bag, Bombs
  cmpwi   r3, 0x2F
  blt     call_execItemGet
  cmpwi   r3, 0x31
  ble     skip_execItemGet

  ; Skull Hammer, Deku Leaf, Progressive Bows
  cmpwi   r3, 0x33
  blt     call_execItemGet
  cmpwi   r3, 0x36
  ble     skip_execItemGet

  ; Swords, Shields, Piece of Heart (Alternate Message), FW Big Key, FW Dungeon Map
  cmpwi   r3, 0x38
  blt     call_execItemGet
  cmpwi   r3, 0x41
  ble     skip_execItemGet

  ; Hero's Charm
  cmpwi   r3, 0x43
  beq     skip_execItemGet

  ; Spoils
  cmpwi   r3, 0x45
  blt     call_execItemGet
  cmpwi   r3, 0x4A
  ble     skip_execItemGet

  ; Empty Bottle
  cmpwi   r3, 0x50
  beq     skip_execItemGet

  ; FW Compass, TotG and FF Dungeon Items, Triforce Shards, Goddess Pearls
  cmpwi   r3, 0x5A
  blt     call_execItemGet
  cmpwi   r3, 0x6B
  ble     skip_execItemGet

  ; Songs, ET Dungeon Items, WT Small Key
  cmpwi   r3, 0x6D
  blt     call_execItemGet
  cmpwi   r3, 0x77
  ble     skip_execItemGet

  ; WT Big Key, Bait, WT Dungeon Map and Compass
  cmpwi   r3, 0x81
  blt     call_execItemGet
  cmpwi   r3, 0x85
  ble     skip_execItemGet

  ; Delivery Bag Items
  cmpwi   r3, 0x98
  blt     call_execItemGet
  cmpwi   r3, 0x9C
  ble     skip_execItemGet

  ; Fill-Up Coupon
  cmpwi   r3, 0x9E
  beq     skip_execItemGet

  ; Tingle Statues
  cmpwi   r3, 0xA3
  blt     call_execItemGet
  cmpwi   r3, 0xA7
  ble     skip_execItemGet

  ; Hurricane Spin, Wallet, Bomb Bag, Quiver, Magic Meter
  cmpwi   r3, 0xAA
  blt     call_execItemGet
  cmpwi   r3, 0xB2
  ble     skip_execItemGet

  ; Rainbow Rupee
  cmpwi   r3, 0xB8
  beq     skip_execItemGet

  ; Charts
  cmpwi   r3, 0xC2
  blt     call_execItemGet
  cmpwi   r3, 0xFE
  ble     skip_execItemGet

  ; Else, branch to execItemGet
  b       call_execItemGet

skip_execItemGet:
  b 0xA08 ; skip execItemGet

call_execItemGet:
  b 0xA04 ; execItemGet
.close
