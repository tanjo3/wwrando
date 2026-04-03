
; This patch makes the Gohma boss fight require only 1 grapple swing instead of 3.
;
; In vanilla, you must swing on Valoo's tail 3 times to drop the ceiling on Gohma
; and break her shell before you can damage her eye. This patch reduces that to 1.
;
; The patch works by changing the comparison that checks how many times the ceiling
; has been dropped on Gohma (stored in m6190) from >= 3 to >= 1.
; This has the side effect of skipping all mid-fight cutscenes

.open "files/rels/d_a_btd.rel" ; Gohma

.org 0x2018
  ; Original: cmplwi r0, 3  (0x28000003)
  ; Changed:  cmplwi r0, 1
  ; This makes Gohma's shell break after just 1 ceiling drop instead of 3.
  cmplwi r0, 1

.close
