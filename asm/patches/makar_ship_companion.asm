
; Allow Makar to spawn as a ship companion on the "sea" stage.
;
; When 0x2910 (MAKAR_IN_WIND_TEMPLE) is set, vanilla create() only allows type 4
; (Wind Temple) through and returns cPhs_ERROR_e for all others, blocking the sea
; Makar actor (params=0xFFFFFFFF). We redirect that error to the sea stage check at
; 0x6B4, which validates stage=="sea" and event bit 0x1604 (set in custom_funcs.asm).
; Wind Temple Makar (type 4) is unaffected — it branches at 0x680 before reaching this.

.open "files/rels/d_a_npc_cb1.rel" ; Makar

; --- Allow sea Makar to pass the 0x2910 check in create() ---
.org 0x684
  b 0x6B4    ; Was: li r3, 5 (cPhs_ERROR_e) -> jump to sea/0x1604 check

; --- Disable ship ride talk in getMsg ---
; The fallthrough case checks m_status SHIP_RIDE bit (0x40) and returns msg 5423.
; Zero the message ID so getMsg returns 0, preventing the talk interaction.
.org 0x7B68
  li r0, 0   ; Was: li r0, 5423

.close
