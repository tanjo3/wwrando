
; This patch implements a custom flag system to track rupee collection in rupeesanity.
; Rupees normally use the per-room mItem flags (16 bits per room) to track collection, but some rooms have more rupees than available flags (e.g. sea/Room33 has 23 rupees).
; So instead, we store collection flags in dSv_reserve_c::mReserve, an unused 80-byte region of the save structure that persists to the memory card automatically.
; Rupeesanity items are identified by having their item_action set to 0x3F, a value not used in vanilla.
; The custom flag index (0-164) is stored in the enable_spawn_switch field, and the vanilla item_pickup_flag is set to 0x7F to disable the vanilla flag check.


; The vanilla dSv_save_c::init() does NOT call dSv_reserve_c::init(). This means mReserve retains stale RAM values after a soft reset or when switching save files.
; Since we store our collection flags in mReserve, stale flags would prevent items from spawning in a new or reloaded save.
; We hook at the end of dSv_save_c::init() to zero all 0x50 bytes of mReserve.
; This is safe because dSv_info_c::card_to_memory() subsequently loads the correct mReserve data from the memory card when an existing save is selected.
.open "sys/main.dol"
.org 0x8005D8B0 ; In dSv_save_c::init
  b rupeesanity_clear_reserve

.org @NextFreeSpace
.global rupeesanity_clear_reserve
rupeesanity_clear_reserve:
  ; mReserve is at offset 0x724 within dSv_save_c.
  addi r3, r29, 0x724
  li r0, 0
  li r4, 20
  mtctr r4
rupeesanity_clear_reserve_loop:
  stw r0, 0 (r3)
  addi r3, r3, 4
  bdnz rupeesanity_clear_reserve_loop
  
  addi r11, r1, 32  ; Replace the instruction we overwrote to branch here
  b 0x8005D8B4
.close




; When an item spawns, the vanilla code checks if the item's mItem flag has already been set and skips spawning if so.
; Since we set the vanilla flag to 0x7F (which is always "not set"), the vanilla check will always pass for rupeesanity items.
; So after the vanilla check passes, we do our own check against the custom flag in mReserve.
; If the flag is already set, we prevent the item from spawning by calling setLoadError and returning an error.
.open "sys/main.dol"
.org 0x800F55E4 ; In _daItem_create
  b rupeesanity_check_spawn

.org @NextFreeSpace
.global rupeesanity_check_spawn
rupeesanity_check_spawn:
  ; Check if this is a rupeesanity item by testing item_action == 0x3F.
  ; item_action is the top 6 bits of the actor params at offset 0xB0 (fopAc_ac_c::mParameters).
  lwz r3, 0xB0 (r31)
  rlwinm r3, r3, 6, 26, 31
  cmpwi r3, 0x3F
  bne rupeesanity_check_spawn_return
  
  ; Read the custom flag index from enable_spawn_switch.
  lwz r3, 0xB0 (r31)
  rlwinm r3, r3, 16, 24, 31
  
  ; Check if the corresponding bit in mReserve is set.
  ; mReserve is at g_dComIfG_gameInfo (0x803C4C08) + save offset 0x724 = 0x803C532C.
  srwi r4, r3, 3
  lis r5, 0x803C532C@ha
  addi r5, r5, 0x803C532C@l
  lbzx r5, r5, r4
  rlwinm r4, r3, 0, 29, 31
  li r3, 1
  slw r3, r3, r4
  and. r3, r5, r3
  beq rupeesanity_check_spawn_return
  
  ; The flag is already set, so prevent it from spawning.
  mr r3, r31
  bl setLoadError__12daItemBase_cFv
  li r3, 5
  b 0x800F5650

rupeesanity_check_spawn_return:
  lbz r0, 0x63A (r31) ; Replace the line we overwrote to branch here
  b 0x800F55E8
.close




; The item's CreateInit function copies enable_spawn_switch into mSpawnSwitchNo, which controls whether the item is visible based on a room switch being set.
; Since we repurposed enable_spawn_switch to store the custom flag index, the item would incorrectly check a switch that doesn't correspond to what we want.
; So after the vanilla store, we look up the original vanilla spawn switch value from rupeesanity_spawn_switch_table and restore it.
; Items behind destructible obstacles retain their original spawn switch so they only appear after the obstacle is destroyed.
; Items with no vanilla spawn switch get 0xFF (always spawn), which is the default value in the table.
.open "sys/main.dol"
.org 0x800F529C ; In daItem_c::CreateInit
  b rupeesanity_fix_spawn_switch

.org @NextFreeSpace
.global rupeesanity_fix_spawn_switch
rupeesanity_fix_spawn_switch:
  stw r0, 0x648 (r30) ; Replace the line we overwrote to branch here
  
  ; Check if this is a rupeesanity item (item_action == 0x3F).
  lwz r3, 0xB0 (r30)
  rlwinm r3, r3, 6, 26, 31
  cmpwi r3, 0x3F
  bne rupeesanity_fix_spawn_switch_return
  
  ; Read the custom flag index from mSpawnSwitchNo.
  lwz r3, 0x648 (r30)
  rlwinm r3, r3, 0, 24, 31
  
  ; Look up the original vanilla spawn switch value from the table.
  lis r4, rupeesanity_spawn_switch_table@ha
  addi r4, r4, rupeesanity_spawn_switch_table@l
  lbzx r0, r4, r3
  stw r0, 0x648 (r30)

rupeesanity_fix_spawn_switch_return:
  b 0x800F52A0
.close




; When a rupeesanity item is collected, we need to set its custom flag in mReserve, so it doesn't respawn.
; The vanilla onItem call is a no-op for flag 0x7F, so after it, we set the corresponding bit ourselves.
;
; Additionally, some rupeesanity items are in locations where the hold-above-head demo must be suppressed.
; These are marked in the rupeesanity_silent_pickup_bitmask.
; For marked items, we force silent collection and play a generic pickup sound effect.
.open "sys/main.dol"
.org 0x800F6CC4 ; In daItem_c::itemGetExecute
  b rupeesanity_set_flag

.org @NextFreeSpace
.global rupeesanity_set_flag
rupeesanity_set_flag:
  ; Check if this is a rupeesanity item (item_action == 0x3F).
  lwz r3, 0xB0 (r31)
  rlwinm r3, r3, 6, 26, 31
  cmpwi r3, 0x3F
  bne rupeesanity_set_flag_return
  
  ; Read the custom flag index from enable_spawn_switch.
  lwz r3, 0xB0 (r31)
  rlwinm r3, r3, 16, 24, 31
  
  ; Set the corresponding bit in mReserve.
  srwi r4, r3, 3
  lis r5, 0x803C532C@ha
  addi r5, r5, 0x803C532C@l
  lbzx r6, r5, r4
  rlwinm r0, r3, 0, 29, 31
  li r3, 1
  slw r3, r3, r0
  or r6, r6, r3
  stbx r6, r5, r4
  
  ; Check if this item is marked for silent pickup (rupeesanity_silent_pickup_bitmask, populated by tweaks.py).
  ; If so, and the item would trigger a hold-above-head demo, force silent collection instead.
  
  ; Read the flag index again from enable_spawn_switch.
  lwz r3, 0xB0 (r31)
  rlwinm r3, r3, 16, 24, 31
  
  ; Check the silent pickup bitmask.
  srwi r4, r3, 3
  lis r5, rupeesanity_silent_pickup_bitmask@ha
  addi r5, r5, rupeesanity_silent_pickup_bitmask@l
  lbzx r5, r5, r4
  rlwinm r4, r3, 0, 29, 31
  li r3, 1
  slw r3, r3, r4
  and. r3, r5, r3
  beq rupeesanity_set_flag_return
  
  ; This item is marked for silent pickup. Check if it would trigger a hold-above-head demo.
  lbz r3, 0x66B (r31) ; daItem_c::mItemStatus
  cmpwi r3, 0x7       ; STATUS_INIT_GET_DEMO
  bne rupeesanity_set_flag_return
  
  ; Force silent collection, skip demo.
  ; Items like Heart Piece and Heart Container already play their sound effect before setting STATUS_INIT_GET_DEMO, so they will still have audio.
  ; Items like Small Key and Deku Leaf set the demo status without a sound and play JA_SE_CONSUMP_ITEM_GET as a generic pickup sound.
  lbz r3, 0x63A (r31) ; daItemBase_c::m_itemNo
  bl execItemGet__FUc
  
  ; Play a pickup sound effect.
  ; This replicates mDoAud_seStart(u32) which calls zel_basic->seStart(seNum, NULL, 0, 0, 1.0, 1.0, -1.0, -1.0, 0).
  lis r3, 0x803F7710@ha
  lwz r3, 0x803F7710@l (r3) ; zel_basic
  li r4, 0x0827             ; JA_SE_CONSUMP_ITEM_GET
  li r5, 0
  li r6, 0
  li r7, 0
  lis r8, 0x3F80            ; 1.0f = 0x3F800000
  stw r8, 0x08 (r1)
  lfs f1, 0x08 (r1)
  fmr f2, f1
  lis r8, 0xBF80            ; -1.0f = 0xBF800000
  stw r8, 0x08 (r1)
  lfs f3, 0x08 (r1)
  fmr f4, f3
  li r8, 0
  bl seStart__11JAIZelBasicFUlP3VecUlScffffUc
  
  li r0, 0x5          ; STATUS_INIT_NORMAL
  stb r0, 0x66B (r31) ; Reset mItemStatus to prevent demo from triggering

rupeesanity_set_flag_return:
  lbz r0, 0x669 (r31) ; Replace the line we overwrote to branch here
  b 0x800F6CC8
.close




; Normally, only Heart Pieces and Heart Containers get a sparkle particle effect when they spawn as field items.
; Since rupeesanity items can be randomized to contain important progression items, we want all of them to sparkle so players don't overlook them.
; We hook right after the vanilla sparkle code in CreateInit and add the same sparkle effect to rupeesanity items that don't already have one.
; The sparkle uses the item's mPtclFollowCb callback so the particles follow the item as it moves.
.open "sys/main.dol"
.org 0x800F5258 ; In daItem_c::CreateInit
  b rupeesanity_add_sparkle

.org @NextFreeSpace
.global rupeesanity_add_sparkle
rupeesanity_add_sparkle:
  ; Check if this is a rupeesanity item (item_action == 0x3F).
  lwz r3, 0xB0 (r30)
  rlwinm r3, r3, 6, 26, 31
  cmpwi r3, 0x3F
  bne rupeesanity_add_sparkle_return
  
  ; Skip items that already have vanilla sparkles (Heart Piece = 0x07, Heart Container = 0x08).
  lbz r3, 0x63A (r30) ; m_itemNo
  cmpwi r3, 0x07      ; Heart Piece
  beq rupeesanity_add_sparkle_return
  cmpwi r3, 0x08      ; Heart Container
  beq rupeesanity_add_sparkle_return
  
  ; Spawn the sparkle particle effect.
  lis r3, g_dComIfG_gameInfo@ha
  addi r3, r3, g_dComIfG_gameInfo@l
  lwz r3, 0x5AC4 (r3)  ; dPa_control_c* particle control
  li r0, -1
  stw r0, 0x08 (r1)
  li r0, 0
  stw r0, 0x0C (r1)
  stw r0, 0x10 (r1)
  stw r0, 0x14 (r1)
  li r4, 0
  li r5, 0x0293        ; ID_COMMON_0293, the same sparkle used by Heart Pieces/Containers
  addi r6, r30, 0x1F8  ; fopAc_ac_c::current.pos
  li r7, 0
  li r8, 0
  li r9, 0xFF ; Alpha
  addi r10, r30, 0x688 ; daItem_c::mPtclFollowCb, so the sparkle follows the item
  bl set__13dPa_control_cFUcUsPC4cXyzPC5csXyzPC4cXyzUcP18dPa_levelEcallBackScPC8_GXColorPC8_GXColorPC4cXyz

rupeesanity_add_sparkle_return:
  lbz r0, 0x63A (r30) ; Replace the line we overwrote to branch here
  b 0x800F525C
.close
