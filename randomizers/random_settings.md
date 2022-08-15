# Random Settings Weights

Below are the weights for the randomized settings. If only one weight is listed, that is the probability that the setting is **on**.

|                 **Setting**                	|                                                           **Weights**                                                           	|
|:------------------------------------------:	|:-------------------------------------------------------------------------------------------------------------------------------:	|
|                **Dungeons**                	|                                                               80%                                                               	|
|           **Puzzle Secret Caves**          	|                                                               50%                                                               	|
|           **Combat Secret Caves**          	|                                                               50%                                                               	|
|            **Savage Labyrinth**            	|                                                               35%                                                               	|
|              **Great Fairies**             	|                                                               50%                                                               	|
|               **Free Gifts**               	|                                                               80%                                                               	|
|              **Miscellaneous**             	|                                                               50%                                                               	|
|              **Tingle Chests**             	|                                                               50%                                                               	|
|            **Short Sidequests**            	|                                                               50%                                                               	|
|             **Long Sidequests**            	|                                                               20%                                                               	|
|             **Spoils Trading**             	|                                                               10%                                                               	|
|                  **Mail**                  	|                                                               50%                                                               	|
|                **Minigames**               	|                                                               50%                                                               	|
|          **Battlesquid Minigame**          	|                                                               20%                                                               	|
|           **Expensive Purchases**          	|                                                               20%                                                               	|
|             **Island Puzzles**             	|                                                               50%                                                               	|
|       **Lookout Platforms and Rafts**      	|                                                               50%                                                               	|
|               **Submarines**               	|                                                               50%                                                               	|
|         **Big Octos and Gunboats**         	|                                                               50%                                                               	|
|             **Eye Reef Chests**            	|                                                               50%                                                               	|
| **Sunken Treasure (From Triforce Charts)** 	|                                                               20%                                                               	|
| **Sunken Treasure (From Treasure Charts)** 	|                                                                5%                                                               	|
|                                            	|                                                                                                                                 	|
|               **Sword Mode**               	|                                 60% Start with Hero's Sword, 35% No Starting Sword, 5% Swordless                                	|
|           **Randomize Entrances**          	| 20% Disabled, 20%, Dungeons, 20% Secret Caves, 20% Dungeons & Secret Caves (Separately), 20% Dungeons & Secret Caves (Together) 	|
|               **Key-Lunacy**               	|                                                               40%                                                               	|
|                **Race Mode**               	|                                                               90%                                                               	|
|      **Number of Race Mode Dungeons**      	|                                             5% 1, 15% 2, 25% 3, 30% 4, 15% 5, 10% 6                                             	|
|      **Triforce Shards to Start With**     	|                                      60% 0, 9% 1, 8% 2, 8% 3, 5% 4, 5% 5, 2% 6, 2% 7, 1% 8                                      	|
|            **Randomize Charts**            	|                                                               50%                                                               	|
|        **Randomize Starting Island**       	|                                                               100%                                                              	|
|       **Chest Type Matches Contents**      	|                                                               100%                                                              	|
|        **Keep Duplicates in Logic**        	|                                                               50%                                                               	|
|                                            	|                                                                                                                                 	|
|             **Hint Placement**             	|                                    80% King of Red Lions, 15% Stone Tablets, 5% Old Man Ho Ho                                   	|
|            **Hint Distribution**           	|                                      100% 6 Path Hints + 6 Barren Hints + 8 Location Hints                                      	|
|        **Only Use Ganondorf Paths**        	|                                                               25%                                                               	|
|              **Clearer Hints**             	|                                                               100%                                                              	|
|            **Use Always Hints**            	|                                                               100%                                                              	|
|                                            	|                                                                                                                                 	|
|               **Swift Sail**               	|                                                               100%                                                              	|
|           **Instant Text Boxes**           	|                                                               100%                                                              	|
|          **Reveal Full Sea Chart**         	|                                                               100%                                                              	|
|           **Skip Boss Rematches**          	|                                                               75%*                                                              	|
|   **Add Shortcut Warps Between Dungeons**  	|                                                               80%                                                               	|
|              **Remove Music**              	|                                                                0%                                                               	|
|                                            	|                                                                                                                                 	|
|        **Number of Starting Items**        	|                                             25% 0, 40% 1, 25% 2, 10% 3 [_see below_]                                            	|
|      **Start With Maps And Compasses**     	|                                                               80%                                                               	|
|     **Starting Extra Heart Containers**    	|                                                              100% 0                                                             	|
|       **Starting Extra Heart Pieces**      	|                                                              100% 0                                                             	|

\* *If **Dungeons** are on, then the weight for **Skip Boss Rematches** is set to 100%*.

## Additional Starting Items
For starting items, you will always start with the Telescope, Ballad of Gales, and Song of Passing. Depending on the value of _Number of Starting Items_, additional weighted pulls (without replacement) from the following table with be made.

**_Importantly_**, the pool of starting items is dynamically modified based on the settings that were randomly chosen. For every option in the starting item pool, if it contains only items with **_no_** logical implications in the seed, that option is removed and its weight is evenly distributed among the remaining options. For example, if **Spoils Trading** is not on, _Spoils Bag_ is removed from the starting items pool and its weight is redistributed.

|              **Starting Item(s)**              	| **Weight** 	|
|:----------------------------------------------:	|:----------:	|
|            **Progressive Picto Box**           	|    5.60%   	|
|                 **Spoils Bag**                 	|    5.60%   	|
|               **Grappling Hook**               	|    5.60%   	|
|               **Progressive Bow**              	|    5.60%   	|
|               **Power Bracelets**              	|    5.60%   	|
|                 **Iron Boots**                 	|    5.60%   	|
|                  **Bait Bag**                  	|    5.60%   	|
|                  **Boomerang**                 	|    5.60%   	|
|                  **Hookshot**                  	|    5.60%   	|
|                    **Bombs**                   	|    5.60%   	|
|                **Skull Hammer**                	|    5.60%   	|
|                  **Deku Leaf**                 	|    5.60%   	|
|             **Progressive Shield**             	|    5.60%   	|
|                **Empty Bottle**                	|    5.60%   	|
|              **Ghost Ship Chart**              	|    5.60%   	|
|          **Progressive Magic Meter**           	|    5.60%   	|
| **Din's Pearl, Farore's Pearl, Nayru's Pearl** 	|    5.60%   	|
|                **Delivery Bag**                	|    1.16%   	|
|          **Delivery Bag, Note to Mom**         	|    0.91%   	|
|        **Delivery Bag, Maggie's Letter**       	|    0.91%   	|
|        **Delivery Bag, Moblin's Letter**       	|    0.91%   	|
|          **Delivery Bag, Cabana Deed**         	|    0.91%   	|
