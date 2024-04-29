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

.close




; Remove the execItemGet call for demo items.
; Instead, let the Archipelago client call execItemGet when the player should receive an item. However, certain items
; should still be given to Link, so we need to check for those specific items.
.open "files/rels/d_a_demo_item.rel"
.org 0xA00
    b check_give_item

.org @NextFreeSpace
.global check_give_item
check_give_item:
  lbz     r3, 1594(r31) ; r3 = m_itemNo (This is the line we replaced.)

check_potions:
  cmplwi  r3, 0x51
  blt     check_deciphered_triforce_charts
  cmplwi  r3, 0x55
  ble     call_execItemGet

check_deciphered_triforce_charts:
  cmplwi  r3, 0x79
  blt     check_trade_quest_items
  cmplwi  r3, 0x80
  ble     call_execItemGet

check_trade_quest_items:
  cmplwi  r3, 0x8C
  blt     check_ankle_rewards
  cmplwi  r3, 0x97
  ble     call_execItemGet

check_ankle_rewards:
  cmplwi  r3, 0xB3
  blt     skip_execItemGet
  cmplwi  r3, 0xB7
  ble     call_execItemGet

skip_execItemGet:
  b 0xA08 ; skip execItemGet

call_execItemGet:
  b 0xA04 ; execItemGet
.close
