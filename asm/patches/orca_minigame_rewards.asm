
; This patch makes Orca's minigame rewards work correctly when randomized.
; Each of the 4 rewards (100/300/500/1000 hits) is given exactly once as a randomized item.
; When the player passes multiple thresholds in one session, all uncollected rewards are chained in sequence without requiring replay.
; Uses event bits 0x6C01-0x6C08 (byte 0x6C, completely unused in vanilla) to track which randomized rewards have been collected.

.open "files/rels/d_a_npc_ji1.rel"

; Normally createItem uses an if/else chain based on game flags to decide which reward to give.
; This doesn't work well when randomized because rewards can be skipped or repeated.
; We replace the minigame reward branching (after the sword and hurricane spin checks) with custom code that finds the lowest uncollected reward the player has earned.
.org 0x426C
  b orca_reward_select

; Normally when the item get event ends, eventAction transitions back to normalAction.
; We replace this so it checks if there are more uncollected rewards to give.
; If so, it restarts the event to give the next reward in sequence.
.org 0x468C
  b orca_check_chain


; Custom function to select which randomized reward to give.
; Checks each reward threshold in order.
; For each one, if the player's level is high enough and the per-reward event bit is not set, that reward is given and the bit is set.
; If all randomized rewards are already collected, falls through to the vanilla reward logic.
.org @NextFreeSpace
.global orca_reward_select
orca_reward_select:
  stwu sp, -0x10 (sp)
  mflr r0
  stw r0, 0x14 (sp)
  
  lis r3, 0x803C522C@ha
  addi r3, r3, 0x803C522C@l
  mr r31, r3
  
  ; Get effective difficulty level.
  ; UNK_D003 is a 2-bit field (0-3). When 1000 hits is reached, the game writes 4 which wraps to 0.
  ; We detect this by checking UNK_0F20 (the "all thresholds cleared" flag) and overriding to 4.
  mr r3, r31
  lis r4, 1
  addi r4, r4, -12285 ; 0xD003
  bl getEventReg__11dSv_event_cFUs
  clrlwi r0, r3, 24 ; Mask to u8
  stw r0, 0x08 (sp) ; Save level on stack
  mr r3, r31
  li r4, 0x0F20 ; UNK_0F20: set when player has reached 1000 hits
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_reward_level_ready
  li r0, 4
  stw r0, 0x08 (sp) ; Override level to 4

orca_reward_level_ready:
  ; Check 100-hit reward: level >= 1 and 0x6C01 not set
  lwz r0, 0x08 (sp)
  cmpwi r0, 1
  blt orca_reward_vanilla_fallback
  mr r3, r31
  li r4, 0x6C01
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_give_100_hit

  ; Check 300-hit reward: level >= 2 and 0x6C02 not set
  lwz r0, 0x08 (sp)
  cmpwi r0, 2
  blt orca_reward_vanilla_fallback
  mr r3, r31
  li r4, 0x6C02
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_give_300_hit

  ; Check 500-hit reward: level >= 3 and 0x6C04 not set
  lwz r0, 0x08 (sp)
  cmpwi r0, 3
  blt orca_reward_vanilla_fallback
  mr r3, r31
  li r4, 0x6C04
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_give_500_hit

  ; Check 1000-hit reward: level >= 4 and 0x6C08 not set
  lwz r0, 0x08 (sp)
  cmpwi r0, 4
  blt orca_reward_vanilla_fallback
  mr r3, r31
  li r4, 0x6C08
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_give_1000_hit

; All randomized rewards already collected, fall through to vanilla logic
orca_reward_vanilla_fallback:
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  b 0x4278

orca_give_100_hit:
  mr r3, r31
  li r4, 0x6C01 ; Mark 100-hit reward as collected
  bl onEventBit__11dSv_event_cFUs
  lis r3, orca_100_hit_item_id@ha
  addi r3, r3, orca_100_hit_item_id@l
  lbz r30, 0 (r3) ; Load the randomized item ID for this slot
  b orca_reward_done

orca_give_300_hit:
  mr r3, r31
  li r4, 0x6C02 ; Mark 300-hit reward as collected
  bl onEventBit__11dSv_event_cFUs
  lis r3, orca_300_hit_item_id@ha
  addi r3, r3, orca_300_hit_item_id@l
  lbz r30, 0 (r3)
  b orca_reward_done

orca_give_500_hit:
  mr r3, r31
  li r4, 0x6C04 ; Mark 500-hit reward as collected
  bl onEventBit__11dSv_event_cFUs
  ; Also set UNK_0F10 to preserve vanilla behavior (this flag gates the 1000-hit Silver Rupee reward on replays)
  mr r3, r31
  li r4, 0x0F10
  bl onEventBit__11dSv_event_cFUs
  lis r3, orca_500_hit_item_id@ha
  addi r3, r3, orca_500_hit_item_id@l
  lbz r30, 0 (r3)
  b orca_reward_done

orca_give_1000_hit:
  mr r3, r31
  li r4, 0x6C08 ; Mark 1000-hit reward as collected
  bl onEventBit__11dSv_event_cFUs
  lis r3, orca_1000_hit_item_id@ha
  addi r3, r3, orca_1000_hit_item_id@l
  lbz r30, 0 (r3)

orca_reward_done:
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  b 0x4304


; Custom function to chain multiple rewards after an item get event finishes.
; First replicates the inlined dComIfGp_event_reset, then checks if there are more uncollected rewards at or below the current UNK_D003 level.
; If so, sets field_0xC78 = 0 to restart the event on the next frame.
; Otherwise, continues to the original setAction(normalAction) code.
.global orca_check_chain
orca_check_chain:
  lhz r0, 0x52C0 (r29)
  ori r0, r0, 8
  sth r0, 0x52C0 (r29)
  
  stwu sp, -0x10 (sp)
  mflr r0
  stw r0, 0x14 (sp)
  
  ; Get event save data pointer
  lis r3, 0x803C522C@ha
  addi r3, r3, 0x803C522C@l
  stw r3, 0x08 (sp)
  
  ; Get effective difficulty level
  lis r4, 1
  addi r4, r4, -12285 ; 0xD003
  bl getEventReg__11dSv_event_cFUs
  clrlwi r3, r3, 24
  stw r3, 0x0C (sp)
  lwz r3, 0x08 (sp)
  li r4, 0x0F20
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_chain_level_ready
  li r0, 4
  stw r0, 0x0C (sp)

orca_chain_level_ready:
  ; Check 100-hit
  lwz r3, 0x0C (sp)
  cmpwi r3, 1
  blt orca_chain_no_more
  lwz r3, 0x08 (sp)
  li r4, 0x6C01
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_chain_has_more

  ; Check 300-hit
  lwz r3, 0x0C (sp)
  cmpwi r3, 2
  blt orca_chain_no_more
  lwz r3, 0x08 (sp)
  li r4, 0x6C02
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_chain_has_more

  ; Check 500-hit
  lwz r3, 0x0C (sp)
  cmpwi r3, 3
  blt orca_chain_no_more
  lwz r3, 0x08 (sp)
  li r4, 0x6C04
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_chain_has_more

  ; Check 1000-hit
  lwz r3, 0x0C (sp)
  cmpwi r3, 4
  blt orca_chain_no_more
  lwz r3, 0x08 (sp)
  li r4, 0x6C08
  bl isEventBit__11dSv_event_cFUs
  cmpwi r3, 0
  beq orca_chain_has_more

orca_chain_no_more:
  ; No more uncollected rewards. Continue to original setAction(normalAction) code.
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  b 0x4698

orca_chain_has_more:
  ; More rewards to give. Restart the event on the next frame.
  li r0, 0
  stb r0, 0x0C78 (r31) ; field_0xC78 = 0 triggers the event to be re-ordered on the next frame
  lwz r0, 0x14 (sp)
  mtlr r0
  addi sp, sp, 0x10
  b 0x47EC ; Jump to eventAction epilogue


; Item ID data slots.
; Default values match vanilla rewards. The randomizer overwrites these via the CustomSymbol path in item_locations.txt.
.global orca_100_hit_item_id
orca_100_hit_item_id:
  .byte 0x05 ; Purple Rupee
.global orca_300_hit_item_id
orca_300_hit_item_id:
  .byte 0x06 ; Orange Rupee
.global orca_500_hit_item_id
orca_500_hit_item_id:
  .byte 0x07 ; Piece of Heart
.global orca_1000_hit_item_id
orca_1000_hit_item_id:
  .byte 0x0F ; Silver Rupee
.align 2

.close
