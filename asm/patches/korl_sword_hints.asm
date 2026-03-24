
; This patch modifies KoRL's setInitMessage function so that when the player is in Hyrule, KoRL always shows message 3444 which contains sword hint text.
; We add an elif block to the if-statement in the original code that checks the current stage name and sets the message to 3444 if the player is in Hyrule.
; This is used by the "korl_hints_swords" option.

.open "files/rels/d_a_ship.rel"
.org 0xEFC ; In setInitMessage__8daShip_cFv
  b korl_sword_hint_precheck

.org @NextFreeSpace
.global korl_sword_hint_precheck
korl_sword_hint_precheck:
  ; Replicate the original bne: if checkForceMessage returned non-zero, go to epilogue.
  beq korl_not_force_message
  b 0x1810 ; Function epilogue

korl_not_force_message:
  ; Check if the current stage starts with "Hy".
  lis r3, 0x803C9D3C@ha ; Current stage name
  addi r3, r3, 0x803C9D3C@l
  lhz r4, 0 (r3)
  cmpwi r4, 0x4879 ; "Hy"
  bne korl_not_in_hyrule
  
  ; Set message to 3444 (0xD74).
  li r0, 0xD74
  stw r0, 0x35C (r30) ; mNextMessageNo
  b 0x1810

korl_not_in_hyrule:
  ; Continue with the original event flag checks.
  b 0xF00

.close
