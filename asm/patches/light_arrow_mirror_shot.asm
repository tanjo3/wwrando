
; Allow Light Arrows to satisfy mirror-light receivers, and make relevant interactions trigger from a single arrow hit.
; (Medli is intentionally excluded for now.)

; Mirrored wall actor.
.open "files/rels/d_a_obj_mmrr.rel" ; Mirror wall
.org 0x239C ; M_tri_src SrcObjTg Type (AT_TYPE_LIGHT -> AT_TYPE_LIGHT | AT_TYPE_LIGHT_ARROW)
  .long 0x00900000
.close

; Mirror object.
.open "files/rels/d_a_obj_mkie.rel" ; Mirror object
.org 0x1928 ; M_sph_src SrcObjTg Type
  .long 0x00900000
.org 0x10FC ; In mode_wait__Q29daObjMkie5Act_cFv
  cmpwi r0, 0 ; Trigger on first valid light-hit frame
.close

; Mirror switch-light actor.
.open "files/rels/d_a_obj_swlight.rel" ; Mirror switch light
.org 0x1DE0 ; M_tri_src SrcObjTg Type (AT_TYPE_LIGHT -> AT_TYPE_LIGHT | AT_TYPE_LIGHT_ARROW)
  .long 0x00900000
.org 0x1DB8 ; L_attr[0]: timer reset value (vanilla=20). Set to 1 so one lit frame exhausts the timer.
  .short 1

; When chk_light registers a TG hit, check whether the attacker was a light arrow.
; If so, set the timer to -1 (permanently charged sentinel). Mirror beams skip this and
; use the normal decrement path, so their behavior is unchanged.
.org 0x1204 ; In chk_light, first instruction of the hit-processing block (originally: mr r3, r30)
  b swlight_chk_arrow_hit

; In mode_norm_moon and mode_active_moon, the not-lit path normally resets the timer to L_attr[0].
; Redirect to a trampoline that skips the reset when the timer is negative (arrow-charged).
.org 0x1328 ; In mode_norm_moon: first instruction of the not-lit timer-reset block
  b swlight_keep_charged_moon
.org 0x154C ; In mode_active_moon (sun-type actors): same not-lit reset path
  b swlight_keep_charged_sun

; The power_up/power_down decision checks "if timer != 0, call power_down".
; Change to "if timer > 0, call power_down" so that timer = -1 routes to power_up, not power_down.
.org 0x1368 ; In mode_norm_moon: "bne power_down" -> "bgt power_down"
  .long 0x41810014 ; bgt 0x137c
.org 0x155C ; In mode_active_moon: same fix
  .long 0x41810014 ; bgt 0x1570

; mode_active_moon_init resets the timer unconditionally. Patch to preserve the sentinel.
.org 0x14FC ; In mode_active_moon_init: "sth r0, 3884(r3)" (timer = L_attr[0])
  b swlight_init_keep_charged

; mode_active_sun calls power_down when NOT lit, eventually reverting to mode_active_moon.
; Redirect the NOT-LIT branch to a trampoline that calls power_up instead when arrow-charged.
.org 0x16A8 ; In mode_active_sun: "beq power_down_path" -> trampoline
  b swlight_sun_lit_check

.org @NextFreeSpace

; chk_light trampoline: inspect the attacking object's AT type flags.
; If the attacker was a light arrow (AT_TYPE_LIGHT_ARROW = 0x00100000), set the actor
; timer to -1 so it is treated as permanently charged for the rest of the room visit.
; Then execute the original vtable call sequence (clears the TG hit state) and return.
.global swlight_chk_arrow_hit
swlight_chk_arrow_hit:
  lwz r4, 0x20(r30)           ; r4 = TG.mObjTg.mHitObj -> pointer to attacking cCcD_Obj
  lwz r0, 0x10(r4)            ; r0 = attacker's mObjAt.mType (dCcD_ObjAtType flags)
  andis. r0, r0, 0x10         ; test AT_TYPE_LIGHT_ARROW = 0x00100000 (bit 20)
  beq swlight_chk_arrow_done  ; not a light arrow: leave timer alone
  li r0, -1                   ; permanently charged sentinel
  sth r0, 3884(r27)           ; actor+0xF2C = -1 (timer stays negative until room exit)
swlight_chk_arrow_done:
  mr r3, r30                  ; (original 0x1204: pass TG obj as this for vtable call)
  lwz r12, 60(r30)            ; (original 0x1208: load vtable pointer)
  lwz r12, 32(r12)            ; (original 0x120C: load vtable[8] function pointer)
  mtctr r12                   ; (original 0x1210)
  bctrl                       ; (original 0x1214: call vtable method, e.g. ClrTgHit)
  b 0x1218                    ; return to chk_light after the vtable call

; mode_norm_moon trampoline: skip timer reset when charged by a light arrow (timer < 0).
; Mirror shield hits leave timer >= 0, so they reset normally.
.global swlight_keep_charged_moon
swlight_keep_charged_moon:
  lha r0, 3884(r31)           ; load current timer (actor+0xF2C)
  cmpwi r0, 0
  blt swlight_moon_done       ; timer < 0 means arrow-charged: skip reset
  lha r0, 0(r30)              ; load L_attr[0] (= 1, the reset value)
  sth r0, 3884(r31)           ; reset timer
swlight_moon_done:
  b 0x1330                    ; return to merge point in mode_norm_moon

; mode_active_moon trampoline: identical logic for sun-type swlight actors.
.global swlight_keep_charged_sun
swlight_keep_charged_sun:
  lha r0, 3884(r31)           ; load current timer (actor+0xF2C)
  cmpwi r0, 0
  blt swlight_sun_done        ; timer < 0: skip reset
  lha r0, 0(r30)              ; load L_attr[0]
  sth r0, 3884(r31)           ; reset timer
swlight_sun_done:
  b 0x1554                    ; return to merge point in mode_active_moon

; mode_active_moon_init trampoline: preserve the arrow-charged sentinel through state resets.
; On entry: r3 = actor, r0 = L_attr[0] (= 1), r4 = L_attr base address.
.global swlight_init_keep_charged
swlight_init_keep_charged:
  lha r4, 3884(r3)            ; r4 = current timer (actor+0xF2C)
  cmpwi r4, 0
  blt swlight_init_done       ; timer < 0 (arrow-charged): skip reset
  sth r0, 3884(r3)            ; timer >= 0: reset to L_attr[0] (normal reset)
swlight_init_done:
  b 0x1500                    ; return to mode_active_moon_init's blr

; mode_active_sun trampoline: when NOT lit, skip power_down if arrow-charged.
; CR0 is set by clrlwi. at 0x16A4 from chk_light's return value.
; On entry: r30 = actor, r31 = L_attr base address.
.global swlight_sun_lit_check
swlight_sun_lit_check:
  bne swlight_sun_power_up    ; LIT (CR0[EQ]=0): go to power_up
  lha r0, 3884(r30)           ; NOT LIT: load timer (actor+0xF2C)
  cmpwi r0, 0
  blt swlight_sun_power_up    ; timer < 0 (arrow-charged): call power_up instead
  b 0x16B8                    ; timer >= 0: normal power_down path
swlight_sun_power_up:
  b 0x16AC                    ; power_up path in mode_active_sun

.close

; Coffin.
.open "files/rels/d_a_obj_kanoke.rel" ; Coffin
.org 0x2550 ; l_cps_src_body SrcObjTg Type
  .long 0x00900000
.org 0x1000 ; In executeNormal__13daObjKanoke_cFv
  cmpwi r0, 0 ; Trigger on first valid light-hit frame
.close

; Stone head.
.open "files/rels/d_a_obj_mkiek.rel" ; Stone head
.org 0x11C0 ; sph_check_src SrcObjTg Type
  .long 0x00900000
.org 0x9D4 ; In check__Q210daObjMkiek5Act_cFv
  cmpwi r0, 1 ; Trigger as soon as one hit has been registered
.close

; Light tag volume.
.open "files/rels/d_a_tag_light.rel" ; Tag Light
.org 0x2214 ; M_sph_src SrcObjTg Type
  .long 0x00900000
.org 0x1C84 ; In type_2__Q210daTagLight5Act_cFv
  cmpwi r0, 0 ; Single hit is enough to pass the activation threshold
.close
