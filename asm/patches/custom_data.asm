
.open "sys/main.dol"
.org @NextFreeSpace

.global hurricane_spin_item_resource_arc_name
hurricane_spin_item_resource_arc_name:
.string "Vscroll"
.align 2 ; Align to the next 4 bytes

.global soul_item_arc_name_figure6b
soul_item_arc_name_figure6b:
.string "Figure6b"
.align 2 ; Align to the next 4 bytes

.global soul_item_arc_name_figure6c
soul_item_arc_name_figure6c:
.string "Figure6c"
.align 2 ; Align to the next 4 bytes




.global ballad_of_gales_warp_table
ballad_of_gales_warp_table:
  ; For reference, here is the original table from vanilla:
  ;.byte -2, -2,  0, -1,  1, -1,  7
  ;.byte  0, -2,  1,  0,  2, -1,  7
  ;.byte  2, -2,  2,  1, -1,  0,  7
  ;.byte -2,  0,  3, -1,  4,  7,  8
  ;.byte  1,  0,  4,  3, -1,  7,  8
  ;.byte  2,  2,  5,  8, -1,  4,  6
  ;.byte -2,  3,  6,  5, -1,  8, -1
  ;.byte -1, -1,  7, -1, -1,  0,  3
  ;.byte  0,  2,  8, -1,  5,  3,  6
  
  ; Custom table:
  .byte -2, -2,  0,  9,  1,  9,  7
  .byte  0, -2,  1,  0,  2, -1,  7
  .byte  2, -2,  2,  1, -1,  0,  7
  .byte -2,  0,  3, -1,  4,  7,  8
  .byte  1,  0,  4,  3, -1,  7,  8
  .byte  2,  2,  5,  8, -1,  4,  6
  .byte -2,  3,  6,  5, -1,  8, -1
  .byte -1, -1,  7, -1, -1,  0,  3
  .byte  0,  2,  8, -1,  5,  3,  6
  .byte -3, -3,  9, -1,  0, -1,  0
  
  .align 2 ; Align to the next 4 bytes

.global ballad_of_gales_warp_float_bank
ballad_of_gales_warp_float_bank:
  ; X positions for each warp
  .float -193, -82, 30, -193, -26, 30, -193, -137, -83, -249
  ; Y positions for each warp
  .float -137, -137, -137, -25, -25, 86, 145, -80, 86, -193
  ; Not sure what these are, but they need to be here because the code reads them from the same symbol as the X/Y positions
  .float 1.6, 0.75




; This is a list of custom REL files, to add on to the vanilla DynamicNameTable list.
.global custom_DynamicNameTable
custom_DynamicNameTable:
  .short 0x01F6 ; Actor ID
  .align 2 ; Align to the next 4 bytes
  .int custom_DynamicNameTable_switch_op_rel_name ; REL name
  
  .short 0x01F7 ; Actor ID
  .align 2 ; Align to the next 4 bytes
  .int custom_DynamicNameTable_dungeon_flag_sw_rel_name ; REL name

custom_DynamicNameTable_switch_op_rel_name:
  .string "d_a_switch_op"
  .align 2 ; Align to the next 4 bytes

custom_DynamicNameTable_dungeon_flag_sw_rel_name:
  .string "d_a_dungeon_flag_sw"
  .align 2 ; Align to the next 4 bytes

; This is a list of custom actor names, to add on to the vanilla l_objectName list.
.global custom_l_objectName
custom_l_objectName:
  padded_string "SwOp", 8 ; Actor name
  .short 0x01F6 ; Actor ID
  .byte 0xFF ; Subtype
  .byte 0x00 ; GBA name
  
  padded_string "DngSw", 8 ; Actor name
  .short 0x01F7 ; Actor ID
  .byte 0xFF ; Subtype
  .byte 0x00 ; GBA name

.global custom_l_objectName_end
custom_l_objectName_end:

; These constants are used by the code that reads these lists, so update these when adding new entries.
.equ num_custom_DynamicNameTable_entries, 2
.equ num_custom_l_objectName_entries, 2

; This is a BSS variable (initialized at runtime) that holds pointers to the DynamicModuleControl struct for each REL.
; Unlike the above two lists, there's no easy way to trick the code into reading both the vanilla list and our custom list, so instead we just move the entire list into free space we have control over.
.global custom_DMC
custom_DMC:
  .space 4 * (0x1F6 + num_custom_DynamicNameTable_entries) ; Total num actors, including our custom ones

.align 2 ; Align to the next 4 bytes


; Bitmask indicating which rupeesanity items should have the hold-above-head demo suppressed.
; Populated by tweaks.py at patch time.
.global rupeesanity_silent_pickup_bitmask
rupeesanity_silent_pickup_bitmask:
  .space 21
.align 2 ; Align to the next 4 bytes

; Table of vanilla spawn switch values indexed by custom flag index (0-164).
; Since enable_spawn_switch is repurposed to store the flag index, the vanilla spawn switch value is lost at runtime.
; This table preserves it so the ASM can restore the correct mSpawnSwitchNo during CreateInit.
; 0xFF means "no spawn switch" (always spawn). Non-0xFF values gate spawning on a room switch.
; Populated by tweaks.py at patch time.
.global rupeesanity_spawn_switch_table
rupeesanity_spawn_switch_table:
  .space 165
.align 2 ; Align to the next 4 bytes

; Current cycle position (0-3) for deterministic auction.
; Stored in sys/main.dol so it persists even when d_a_auction.rel is unloaded.
; Even though this is an optional feature, defining it here won't impact anything if the fix_auction.asm patch is not applied.
.global auction_cycle_index
auction_cycle_index:
  .byte 0
  .align 2


.close
