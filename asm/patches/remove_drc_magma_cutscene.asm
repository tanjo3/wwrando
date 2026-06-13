; Remove the cutscene that plays in DRC when you use a water pot on magma for the first time.
; In the demo_move function, we change the conditional branch that checks if event bit 0x0380 is set
; to an unconditional branch, so it always skips the cutscene code.
.open "files/rels/d_a_obj_magmarock.rel" ; Magma rock platform
.org 0x238
  b 0x31c
.close
