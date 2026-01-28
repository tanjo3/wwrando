; Remove the cutscene that plays in DRC when you use a water pot on magma for the first time.
; In the demo_move function, we change the conditional branch that checks if event bit 0x0380 is set
; to an unconditional branch, so it always skips the cutscene code.
.open "files/rels/d_a_obj_magmarock.rel" ; Magma rock platform
.org 0x238
  b 0x31c
.close

; In DRC, set a switch (14) for having seen the event where the hanging platform is lowered.
; Also set a switch (09) for having seen the event where the camera pans up to Valoo when you go outside.
.open "sys/main.dol"
.org @NextFreeSpace

lis r3, 0x803C4FF4@ha ; Dragon Roost Cavern stage info.
addi r3, r3, 0x803C4FF4@l
lis r4, 0x0010 ; Switch 0x14 (Hanging platform cutscene)
ori r4, r4, 0x0200 ; Switch 0x09 (Camera pans to Valoo)
stw r4, 4 (r3)

.close