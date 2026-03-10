
; This patch prevents bosses from spawning if the player does not have the corresponding boss soul item.
; Each boss soul is tracked via a unique event bit set by the soul's item_get_func.
; When boss soul shuffle is disabled, all souls are given as starting items so the event bits are already set.
;
; We hook fpcSCtRq_Request, the lowest-level actor creation function that all creation paths go through.
; If the actor being created is a boss and the player doesn't have its soul, we return -1 (error) before any actor memory is allocated.

.open "sys/main.dol"

.org 0x8004086C ; In fpcSCtRq_Request
  b check_boss_soul_before_create

.org @NextFreeSpace

; Table of (actor_id, event_bit) pairs, terminated by 0x0000.
boss_soul_table:
.short 0x00EB ; Gohma
.short 0x6A80 ; Soul of Gohma event bit
.short 0x00EC ; Kalle Demos
.short 0x6B01 ; Soul of Kalle Demos event bit
.short 0x00F0 ; Helmaroc King
.short 0x6B04 ; Soul of Helmaroc King event bit
.short 0x00F2 ; Gohdan
.short 0x6B02 ; Soul of Gohdan event bit
.short 0x00D4 ; Jalhalla
.short 0x6B08 ; Soul of Jalhalla event bit
.short 0x00DA ; Molgera
.short 0x6B10 ; Soul of Molgera event bit
.short 0x0000 ; End of table
.align 2

.global check_boss_soul_before_create
check_boss_soul_before_create:
stwu sp, -0x20 (sp)
stw r3, 0x08 (sp)
stw r4, 0x0C (sp)
stw r5, 0x10 (sp)
stw r6, 0x14 (sp)
stw r7, 0x18 (sp)
mflr r0
stw r0, 0x24 (sp)

lis r5, boss_soul_table@ha
addi r5, r5, boss_soul_table@l

check_boss_soul_loop:
lhz r3, 0 (r5) ; Load actor ID from table
cmplwi r3, 0
beq check_boss_soul_not_boss ; End of table, not a boss

clrlwi r0, r4, 16 ; Zero-extend procName to compare
cmplw r0, r3
beq check_boss_soul_found_boss

addi r5, r5, 4
b check_boss_soul_loop

check_boss_soul_found_boss:
lhz r4, 2 (r5) ; Load the soul's event bit from table

lis r3, 0x803C522C@ha
addi r3, r3, 0x803C522C@l
bl isEventBit__11dSv_event_cFUs
cmpwi r3, 0
bne check_boss_soul_not_boss ; Has soul, allow creation

; Player doesn't have the soul. Return error to prevent actor creation.
lwz r0, 0x24 (sp)
mtlr r0
addi sp, sp, 0x20
li r3, -1 ; fpcM_ERROR_PROCESS_ID_e
blr

check_boss_soul_not_boss:
; Not a boss, or player has the soul. Continue with normal fpcSCtRq_Request.
lwz r0, 0x24 (sp)
mtlr r0
lwz r3, 0x08 (sp)
lwz r4, 0x0C (sp)
lwz r5, 0x10 (sp)
lwz r6, 0x14 (sp)
lwz r7, 0x18 (sp)
addi sp, sp, 0x20
stwu sp, -32 (sp) ; Replace the instruction we overwrote to branch here
b 0x80040870

.close
