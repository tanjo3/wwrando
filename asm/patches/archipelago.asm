.open "sys/main.dol"
.org 0x80234FE0 ; In dScnPly_Execute
  bl      give_archipelago_item
; Every frame, loop through the Archipelago item array and give items to the player.
; The array is cleared as items are given. We put this function in `dScnPly_Execute`, which is run every frame.
.org @NextFreeSpace
.global give_archipelago_item
give_archipelago_item:
  stwu    sp, -0x10 (sp)
  mflr    r0
  stw     r0, 0x14 (sp)
  stmw    r29, 0x8 (sp)
  
  ; Store values of r3 in r29
  mr      r29, r3
  
  ; Load give_archipelago_item_array into r30
  lis     r30, give_archipelago_item_array@ha
  addi    r30, r30, give_archipelago_item_array@l
  
  ; Initialize loop counter r31 at 0
  li      r31, 0
  
  give_archipelago_item_loop:
  ; If we've looped through the entire array, return
  cmpwi   r31, num_give_archipelago_item_array_entries
  bge     give_archipelago_item_end
  
  ; Load the item ID into r3
  lbzx    r3, r30, r31
  
  ; If item ID is 0xFF, ignore
  cmpwi   r3, 0xFF
  beq     give_archipelago_item_loop_end
  
  ; Else, branch to execItemGet
  bl      execItemGet__FUc
  
  ; Overwrite item ID with 0xFF
  li      r3, 0xFF
  stbx    r3, r30, r31
  
  give_archipelago_item_loop_end:
  ; Increment loop counter and continue
  addi    r31, r31, 1
  b       give_archipelago_item_loop
  
  give_archipelago_item_end:
  ; Retore the value of r3
  mr      r3, r29
  
  lmw     r29, 0x8 (sp)
  lwz     r0, 0x14 (sp)
  mtlr    r0
  addi    sp, sp, 0x10
  
  mr      r31, r3         ; this is the line we overwrote on 0x80234FE0
  
  blr

.global give_archipelago_item_equ
give_archipelago_item_equ:
.equ num_give_archipelago_item_array_entries, 0x10

.global give_archipelago_item_array
give_archipelago_item_array:
  .space num_give_archipelago_item_array_entries, 0xFF
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
  blt     execItemGet
  cmpwi   r3, 0x08
  ble     skip_execItemGet

  ; Silver Rupee
  cmpwi   r3, 0x0F
  beq     skip_execItemGet

  ; DRC Keys
  cmpwi   r3, 0x13
  blt     execItemGet
  cmpwi   r3, 0x14
  ble     skip_execItemGet

  ; DRC Dungeon Map and Compass, FW Small Key
  cmpwi   r3, 0x1B
  blt     execItemGet
  cmpwi   r3, 0x1D
  ble     skip_execItemGet

  ; Joy Pendant, some progression items
  cmpwi   r3, 0x1F
  blt     execItemGet
  cmpwi   r3, 0x2A
  ble     skip_execItemGet

  ; Bait Bag, Boomerang
  cmpwi   r3, 0x2C
  blt     execItemGet
  cmpwi   r3, 0x2D
  ble     skip_execItemGet

  ; Hookshot, Delivery Bag, Bombs
  cmpwi   r3, 0x2F
  blt     execItemGet
  cmpwi   r3, 0x31
  ble     skip_execItemGet

  ; Skull Hammer, Deku Leaf
  cmpwi   r3, 0x33
  blt     execItemGet
  cmpwi   r3, 0x34
  ble     skip_execItemGet

  ; Swords, Shields, Piece of Heart (Alternate Message), FW Big Key, FW Dungeon Map
  cmpwi   r3, 0x38
  blt     execItemGet
  cmpwi   r3, 0x41
  ble     skip_execItemGet

  ; Hero's Charm
  cmpwi   r3, 0x43
  beq     skip_execItemGet

  ; Spoils
  cmpwi   r3, 0x45
  blt     execItemGet
  cmpwi   r3, 0x4A
  ble     skip_execItemGet

  ; Empty Bottle
  cmpwi   r3, 0x50
  beq     skip_execItemGet

  ; FW Compass, TotG and FF Dungeon Items, Triforce Shards, Goddess Pearls
  cmpwi   r3, 0x5A
  blt     execItemGet
  cmpwi   r3, 0x6B
  ble     skip_execItemGet

  ; Songs, ET Dungeon Items, WT Small Key
  cmpwi   r3, 0x6D
  blt     execItemGet
  cmpwi   r3, 0x77
  ble     skip_execItemGet

  ; WT Big Key, Bait, WT Dungeon Map and Compass
  cmpwi   r3, 0x81
  blt     execItemGet
  cmpwi   r3, 0x85
  ble     skip_execItemGet

  ; Delivery Bag Items
  cmpwi   r3, 0x99
  blt     execItemGet
  cmpwi   r3, 0x9C
  ble     skip_execItemGet

  ; Fill-Up Coupon
  cmpwi   r3, 0x9E
  beq     skip_execItemGet

  ; Tingle Statues
  cmpwi   r3, 0xA3
  blt     execItemGet
  cmpwi   r3, 0xA7
  ble     skip_execItemGet

  ; Hurricane Spin, Wallet, Bomb Bag, Quiver, Magic Meter
  cmpwi   r3, 0xAA
  blt     execItemGet
  cmpwi   r3, 0xB2
  ble     skip_execItemGet

  ; Rainbow Rupee
  cmpwi   r3, 0xB8
  beq     skip_execItemGet

  ; Charts
  cmpwi   r3, 0xC2
  blt     execItemGet
  cmpwi   r3, 0xFE
  ble     skip_execItemGet

  ; Else, branch to execItemGet
  b       execItemGet

skip_execItemGet:
  b 0xA08 ; skip execItemGet

call_execItemGet:
  b 0xA04 ; execItemGet
.close
