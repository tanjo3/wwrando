
.open "sys/main.dol"
.org @NextFreeSpace

li r4, 0 ; 
ori r4, r4, 0xC203 ; Register tracking mail sorting rounds with Koboli
li r5, 3 ; Set to 3 to indicate Koboli's rounds are finished (triggers Baito to take over)
bl setEventReg__11dSv_event_cFUsUc

close
