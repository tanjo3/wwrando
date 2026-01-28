; Always set the event flag for seeing the Triforce refuse together.
; This skips the cutscene that would normally play when you collect all 8 Triforce Shards.
.open "sys/main.dol"
.org @NextFreeSpace
;  stwu sp, -0x10 (sp)
;  mflr r0
;  stw r0, 0x14 (sp)

lis r3, 0x803C522C@ha
addi r3, r3, 0x803C522C@l
li r4, 0x3D04 ; Saw the Triforce refuse
bl onEventBit__11dSv_event_cFUs

;  lwz r0, 0x14 (sp)
;  mtlr r0
;  addi sp, sp, 0x10
;  blr
.close
