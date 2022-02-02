from collections import namedtuple

HintStoneTabletData = namedtuple("HintStoneTabletData", 'stage_name room_num x y z y_rot')

STONE_TABLET_DATAS = [
	HintStoneTabletData("sea", 11, -1510.3162841796875, 832.3160400390625, -202566.484375, 0xB0D4), # Windfall - Next to Jail 1
	HintStoneTabletData("sea", 11, -1389.1197509765625, 854.2840576171875, -202882.515625, 0xB0D4), # Windfall - Next to Jail 2
	HintStoneTabletData("sea", 11, -1644.2230224609375, 920.1809692382812, -203255.671875, 0xECC2), # Windfall - Next to Jail 3
	HintStoneTabletData("sea", 11, -1808.2147216796875, 944.1951904296875, -203326.96875, 0xED8D), # Windfall - Next to Jail 4
	HintStoneTabletData("sea", 11, 1638.0003662109375, 942.4094848632812, -198845.171875, 0xB45B), # Windfall - Top of Bridge

	HintStoneTabletData("Orichh", 0, -648.318603515625, 155.9230194091797, -496.8177185058594, 0x3F96), # Windfall - Left of House of Wealth Podium
	HintStoneTabletData("Nitiyou", 0, -411.80731201171875, 0.0, -323.85296630859375, 0x4000), # Windfall - School House Left
	HintStoneTabletData("Nitiyou", 0, 413.2185363769531, 0.0, -318.052490234375, 0xC000), # Windfall - School House Right
	HintStoneTabletData("Kaisen", 0, 464.9999694824219, 0.0, 153.25082397460938, 0xC000), # Windfall - Sploosh Left Corner
	HintStoneTabletData("Kaisen", 0, 464.99993896484375, 0.0, 640.4966430664062, 0xC000), # Windfall - Sploosh Right Corner
	HintStoneTabletData("Kaisen", 0, 465.0, 0.0, 393.7803649902344, 0xC000), # Windfall - Sploosh Wall Middle
	HintStoneTabletData("Ocmera", 0, 315.1387634277344, 450.0, -616.5870971679688, 0xE039), # Windfall - Lenzo Upper Floor Corner

	HintStoneTabletData("sea", 12, 79541.1015625, 300.0, -179319.21875, 0xD25), # Pawprint - In Front of Mailbox
	HintStoneTabletData("sea", 12, 79708.03125, 299.0141906738281, -182821.28125, 0xD534), # Pawprint - Right Edge Island
	HintStoneTabletData("sea", 12, 77586.34375, 326.52978515625, -178512.203125, 0x4C36), # Pawprint - Left Edge Island
	HintStoneTabletData("sea", 12, 80519.8984375, 440.0, -179997.171875, 0xF66A), # Pawprint - Inside Shell

	HintStoneTabletData("TyuTyu", 0, 544.9401245117188, -2.0290522115828935e-06, 507.6248474121094, 0xA260), # Pawprint Cave - Entrance 1
	HintStoneTabletData("TyuTyu", 0, 521.4263916015625, -3.329448645672528e-06, -556.22412109375, 0xE068), # Pawprint Cave - Entrance 2
	HintStoneTabletData("TyuTyu", 0, -536.5362548828125, -9.38960693019908e-06, -550.7044067382812, 0x1F81), # Pawprint Cave - Entrance 3
	HintStoneTabletData("TyuTyu", 0, -646.927734375, 1.904676901176572e-05, 468.63983154296875, 0x57F1), # Pawprint Cave - Entrance 4

	HintStoneTabletData("sea", 13, 198319.78125, 634.4371948242188, -202287.4375, 0x8988), # DRI - Trail
	HintStoneTabletData("sea", 13, 199002.203125, 40.49930953979492, -198317.796875, 0x4A64), # DRI - Behind Secret Cave Boulder
	HintStoneTabletData("sea", 13, 201968.234375, 185.0, -197265.296875, 0xC786), # DRI - Wind Shrine Left
	HintStoneTabletData("sea", 13, 201055.046875, 185.0, -197329.046875, 0x3BE1), # DRI - Wind Shrine Right
	HintStoneTabletData("sea", 13, 199772.59375, 1130.0, -196579.78125, 0xAC9A), # DRI - In Front of Komali
	HintStoneTabletData("sea", 13, 200740.15625, 1536.748291015625, -198978.125, 0x7FC2), # DRI - Outside Aerie
	HintStoneTabletData("sea", 13, 202040.90625, 2562.213623046875, -197980.421875, 0x91E4), # DRI Upper Area Outside Platform Left
	HintStoneTabletData("sea", 13, 200569.390625, 2562.213623046875, -198439.375, 0x7D1B), # DRI Upper Area Outside Platform Right
	HintStoneTabletData("sea", 13, 198748.59375, 3115.56298828125, -196016.0625, 0x7660), # DRI Upper Area Outside Medli's Stage
	HintStoneTabletData("sea", 13, 198633.859375, 3160.0, -198817.359375, 0xD4B0), # DRI Upper Area Outside Uppermost Platform Close
	HintStoneTabletData("sea", 13, 198572.8125, 3300.0, -199631.796875, 0xE8D3), # DRI Upper Area Outside Uppermost Platform By Wall
	HintStoneTabletData("sea", 13, 202768.953125, 1000.0, -208083.0625, 0x8791), # DRI Fly Across Left
	HintStoneTabletData("sea", 13, 202636.984375, 1000.0, -209041.265625, 0x39B), # DRI Fly Across Right

	HintStoneTabletData("Atorizk", 0, 165.0, 0.0, -2065.0, 0xDD33), # Rito Aerie - Path to Komali's Room
	HintStoneTabletData("Atorizk", 0, -1317.035888671875, 700.0, 1128.6231689453125, 0x5C00), # Rito Aerie - Storage Room
	HintStoneTabletData("Comori", 0, 278.45635986328125, 0.0, -287.9402770996094, 0xDF55), # Rito Aerie - Komali's Room
	HintStoneTabletData("Adanmae", 0, -1008.187744140625, 750.0, 1749.326171875, 0xFC79), # DRC Path - By Entrance to Bridge

	HintStoneTabletData("sea", 9, -181563.640625, 1031.040283203125, -201493.265625, 0x1E5A), # M&C Highest Platform
	HintStoneTabletData("sea", 9, -180337.8125, 950.5496215820312, -197885.1875, 0x79AC), # M&C Lower Platform

	HintStoneTabletData("sea", 44, -205864.171875, 107.61651611328125, 316091.875, 0x9153), # Outset - Under Grandma's House
	HintStoneTabletData("sea", 44, -201702.4375, 1175.7100830078125, 320396.09375, 0x67CB), # Outset - BigPig House Corner
	HintStoneTabletData("sea", 44, -201289.796875, 1200.0, 321183.25, 0x4D34), # Outset - BigPig House Under Window
	HintStoneTabletData("sea", 44, -206737.0, 1090.3660888671875, 317897.3125, 0x3521), # Outset - Underneath Savage Tree
	HintStoneTabletData("sea", 44, -202289.859375, 683.5264282226562, 318754.59375, 0xC273), # Outset - Back of Orca's House
	HintStoneTabletData("sea", 44, -202249.234375, 684.9616088867188, 317941.09375, 0x1A5), # Outset - Front Ledge of Orca's House
	HintStoneTabletData("sea", 44, -192301.53125, 550.0, 319096.4375, 0x9DA4), # Outset - Behind Mesa's House
	HintStoneTabletData("sea", 44, -195436.140625, 1650.0, 313654.75, 0x2D25), # Outset - Watchtower

	HintStoneTabletData("sea", 45, -81767.6171875, 151.6699981689453, 320663.21875, 0x164B), # Headstone - Back Corner Left
	HintStoneTabletData("sea", 45, -78986.4609375, 108.12887573242188, 320942.53125, 0xD767), # Headstone - Back Corner Right

	HintStoneTabletData("Otkura", 0, -304.8036804199219, -221.74954223632812, 500.78857421875, 0x65EE), # FH - Makar Hideout - Right
	HintStoneTabletData("Otkura", 0, 230.89987182617188, -221.7495574951172, 549.0679931640625, 0xA232), # FH - Makar Hideout - Left
	HintStoneTabletData("sea", 41, 218215.046875, 866.7055053710938, 201666.140625, 0x770A), # FH - Side Ledge
	HintStoneTabletData("sea", 41, 217425.125, 1550.0, 202525.375, 0x9EB0), # FH - Pond before Entrance

	HintStoneTabletData("Omori", 0, -2075.904052734375, 100.0, -1570.4208984375, 0xE83C), # Inside FH - River Corner
	HintStoneTabletData("Omori", 0, 2304.37841796875, 350.0, 2396.619384765625, 0xA130), # Inside FH - In front of Deku Tree
	HintStoneTabletData("Ocrogh", 0, 488.7061767578125, 0.0, -5.626209735870361, 0xB28C), # Inside FH - Hollo's Shop

	HintStoneTabletData("Cave03", 0, 5056.4306640625, 600.0, -366.8910217285156, 0xCBFA), # Cliff Plateau Cave - Back Wall 1
	HintStoneTabletData("Cave03", 0, 4582.23974609375, 600.0, -1218.3988037109375, 0xE402), # Cliff Plateau Cave - Back Wall 2
	HintStoneTabletData("Cave03", 0, 3441.411376953125, 950.0000610351562, -116.45675659179688, 0x3BF4), # Cliff Plateau Cave - Tree Truck Platform

	HintStoneTabletData("sea", 35, 302915.5625, 490.1648254394531, 104366.0859375, 0x9798), # Bird's Peak Rock - Outside
	HintStoneTabletData("TF_03", 0, 0.93382728099823, 6.964859949221136e-06, -1192.338623046875, 0xD33), # Bird's Peak Rock - Cave Left
	HintStoneTabletData("TF_03", 0, -143.70986938476562, -2.9502700726879993e-06, 1142.8807373046875, 0x71F4), # Bird's Peak Rock -  Cave Right

	HintStoneTabletData("sea", 34, 220886.40625, 300.0, 78232.5390625, 0xE205), # Bomb Island - On Fuse
	HintStoneTabletData("sea", 34, 218074.328125, 300.0, 79949.7578125, 0xB99F), # Bomb Island - Between Boulders
	HintStoneTabletData("sea", 34, 218543.828125, 450.0, 80339.890625, 0xFBE), # Bomb Island - Middle Platform Lower
	HintStoneTabletData("sea", 34, 220878.21875, 700.0, 80187.515625, 0xCF9B), # Bomb Island - Middle Platform Higher

	HintStoneTabletData("sea", 33, 120654.0859375, 781.7080078125, 120570.3203125, 0xA74F), # Private Oasis - "Gazebo"
	HintStoneTabletData("sea", 33, 121329.375, 1000.0, 117127.59375, 0xF61A), # Private Oasis - Behind Cabana

	HintStoneTabletData("sea", 48, 178922.625, 574.3810424804688, 282349.6875, 0x6E51), # Boating Course - On Rock by NPC
	HintStoneTabletData("sea", 48, 180488.265625, 575.6987915039062, 277265.125, 0xA82E), # Boating Course - On Rock by Cave

	HintStoneTabletData("sea", 47, 100504.2421875, 300.0, 319943.25, 0x629E), # Angular - Around Corner on Right
	HintStoneTabletData("sea", 47, 102194.6953125, 300.0, 319493.96875, 0xC0C6), # Angular - By Cave Entrance
	HintStoneTabletData("SubD43", 0, 2041.167236328125, 325.71624755859375, -1098.14599609375, 0x8029), # Angular Cave - Left Mouth
	HintStoneTabletData("SubD43", 0, 1999.167236328125, 470.970947265625, 1111.4437255859375, 0x3DA), # Angular Cave - Right Mouth

	HintStoneTabletData("sea", 17, -101130.9453125, 350.42254638671875, -79374.921875, 0x4714), # Tingle Island - Free Corner

	HintStoneTabletData("sea", 16, -220388.390625, 164.36778259277344, -119384.7890625, 0xDF65), # Rock Spire - Bottom of the Island
	HintStoneTabletData("sea", 16, -218387.234375, 513.0156860351562, -121792.8671875, 0x1D41), # Rock Spire - On Main Pathway Corner
	HintStoneTabletData("sea", 16, -221534.546875, 1100.0, -118031.2109375, 0x9D99), # Rock Spire - By Cave Entrance

	HintStoneTabletData("sea", 10, -116205.8828125, 458.4581604003906, -182617.640625, 0xB57F), # Spectacle - By Barrels

	HintStoneTabletData("sea", 23, -203821.578125, 36.67220687866211, 3303.3818359375, 0xDB9B), # Greatfish - Backside Beach
	HintStoneTabletData("sea", 23, -201967.375, 50.98825454711914, 3541.974609375, 0xBBD), # Greatfish - Front Beach

	HintStoneTabletData("sea", 29, -279912.3125, 300.0, 121807.71875, 0x8127), # Needlerock - Southern Section of Circle
	HintStoneTabletData("sea", 29, -279710.6875, 500.0, 125595.359375, 0x8468), # Needlerock - Behind Chest

	HintStoneTabletData("sea", 36, -299506.84375, 1734.02001953125, 199134.765625, 0xF3AE), # Diamond Steppe - Third Platform

	HintStoneTabletData("sea", 43, -320877.84375, 790.7193603515625, 297638.1875, 0xB67), # Horseshoe - By Second Hole
	HintStoneTabletData("sea", 43, -321519.8125, 790.7193603515625, 297892.25, 0x244A), # Horseshoe - By Second Hole Left
	HintStoneTabletData("sea", 43, -320228.4375, 788.4400024414062, 297577.59375, 0xF3CC), # Horseshoe - By Second Hole Right

	HintStoneTabletData("sea", 1, -301985.71875, 715.0686645507812, -300921.3125, 0x6454), # FF - Main Platform Corner
	HintStoneTabletData("sea", 1, -296817.3125, 1427.8974609375, -298987.8125, 0xAA10), # FF - First Level Balcony
	HintStoneTabletData("sea", 1, -299621.78125, 2150.563720703125, -296941.0625, 0xA940), # FF - First Ramp Corner
	HintStoneTabletData("ma2room", 4, -2238.85302734375, 728.4600219726562, 3063.744140625, 0xA878), # FF - Chest on Bed Room Left
	HintStoneTabletData("ma2room", 4, -3804.265869140625, 728.4600219726562, 2687.489990234375, 0x2EDD), # FF - Chest on Bed Room Under Map
	HintStoneTabletData("ma2room", 0, 2455.560302734375, 1705.4151611328125, 3049.228515625, 0xC2), # FF - Jail Cell Room By Top Pots
	HintStoneTabletData("ma2room", 0, 3721.835693359375, 728.4600219726562, 3541.759765625, 0xC421), # FF - Jail Cell Room By Lower Window
	HintStoneTabletData("sea", 1, -304682.3125, 3109.52978515625, -301501.46875, 0x659A), # FF - Path to Helmaroc

	HintStoneTabletData("M_NewD2", 0, -1394.8887939453125, 250.0000762939453, 8322.20703125, 0x6407), # DRC - Entrance Left
	HintStoneTabletData("M_NewD2", 0, -599.7413940429688, 249.99990844726562, 8372.83203125, 0xA116), # DRC - Entrance Right
	HintStoneTabletData("M_NewD2", 0, -689.392822265625, 0.0, 4985.69677734375, 0xDE1), # DRC - Entrance Next to Stairs
	HintStoneTabletData("M_NewD2", 1, 3886.436279296875, 450.0, 3635.073974609375, 0xC020), # DRC - Near Boarded Up Bokoblin
	HintStoneTabletData("M_NewD2", 12, 5649.64599609375, -200.0, -2803.33251953125, 0xA236), # DRC - BK Chest Room
]
