from dataclasses import dataclass

@dataclass(frozen=True)
class Trick:
  name: str
  description: str

ALL_TRICKS: list[Trick] = [
  Trick(
    name="DRC - Hookshot Across Lava Pit",
    description="Throw a burning stick across the pit to burn the barricade, then stand at a certain specific spot on the edge of the cliff and hookshot the chest to get across.",
  ),
  Trick(
    name="DRC - Cut Down Hanging Platform with Hookshot or Grappling Hook",
    description="Hookshot and Grappling Hook can also cut the ropes, though aiming them at such small targets without lock-on is fairly precise.",
  ),
  Trick(
    name="DRC - Use Deku Leaf to Enter Gaping Maw",
    description="You can sneak into the gap at the bottom of the second room of DRC to get here early (without cutting the platform down) by flying into the gap with Deku Leaf.",
  ),
  Trick(
    name="DRC - Use Ice Arrows to Enter Gaping Maw",
    description="You can use Ice Arrows to freeze the magma and make one or two platforms to jump across.<br>" \
    "It's somewhat tricky, but made easier by jump attacking if you have a sword.",
  ),
  Trick(
    name="FW - Fly Through Vines Without Destroying Seeds",
    description="You can fly past the seeds hanging by vines without destroying the seeds first, but it's slightly tricky to thread the needle like that, so you may fall.",
  ),
  Trick(
    name="FW - Grapple Up Tall Room Before Miniboss Without Killing Peahats",
    description="Grappling up is tricky while the Peahats are still alive since they knock you around.",
  ),
  Trick(
    name="TotG - Use Deku Leaf to Fly Between Floating Platforms",
    description="Instead of shooting the first eye, you can use Deku Leaf to fly from the platform near the entrance to the platform to the left of this chest.<br>" \
    "This doesn't require leaf pumping or any tricks, but it does require the cycles of the two platforms to be in sync, and decent timing.",
  ),
  Trick(
    name="TotG - Hookshot Floating Platforms Room Chest from Door",
    description="Instead of shooting the first eye, you can simply hookshot the chest from the platform near the entrance.",
  ),
  Trick(
    name="TotG - Skip Deku Leaf for North Servant of the Tower",
    description="You can skip using Deku Leaf by jumping on two decorative pillars near the side of the room, and then jumping onto the wall protrusion above where the lasers are coming out of.",
  ),
  Trick(
    name="TotG - Fight Gohdan with Hookshot Instead of Bow",
    description="You can use hookshot to shoot all of Gohdan's eyes instead of the bow.",
  ),
  Trick(
    name="FF - Trick Mounted Cannons to Blow Up Gate",
    description="You can trick the mounted cannons into blowing the door up for you.",
  ),
  Trick(
    name="FF - Access via Ganon's Tower Dark Portal",
    description="You can circumvent the gate entirely by going all the way down to Ganon's Tower, and then activating the dark portal so you can warp up to Forsaken Fortress.",
  ),
  Trick(
    name="FF - Use Floormaster to Reach Upper Jail Cell",
    description="You can intentionally get caught by the Floormaster in the boat room so that it takes you to jail, then escape and access this chest without needing any items.",
  ),
  Trick(
    name="FF - Reach Boss Entrance via Bedpost Jumps",
    description="It is possible to get up there without either Deku Leaf or Hookshot. To do it, go to the southwest room, and jump on top of the wooden bedposts (not the rightmost one).<br>" \
    "Then jump diagonally onto the corner of the platform with the Bokoblin and the Skull Hammer pegs on it.",
  ),
  Trick(
    name="ET - Defeat Floormasters with Skull Hammer",
    description="When using Skull Hammer to kill Floormasters, there's a chance you'll miss because of their wonky hitbox, and get taken all the way back to the dungeon entrance.",
  ),
  Trick(
    name="ET - Reach Third Crypt Without Defeating Red Bubbles",
    description="You can skip killing the Red Bubbles, but reflecting the light to progress is quite annoying while they're still alive.",
  ),
  Trick(
    name="ET - Defeat Inactive Blue Bubbles with Bow",
    description="You can defeat inactive Blue Bubbles with the bow without ever activating them.",
  ),
  Trick(
    name="ET - Defeat Inactive Blue Bubbles with a Melee Weapon",
    description="You can defeat inactive Blue Bubbles with a melee weapon as long as you're somewhat fast and you avoid activating both at once.",
  ),
  Trick(
    name="WT - Reach Hub Room Upper Level with Hookshot",
    description="Starting from the center of the hub room, use the hookshot on one of the targets above you to gain height, then take out the Deku Leaf when you hit the target with precise timing and float over to the upper level.",
  ),
  Trick(
    name="Circumvent Outset Island Trees with Deku Leaf",
    description="You can circumvent the trees entirely by jumping off the edge of the path near the trees and flying northeast to land on the elevated cliff on the side of the island.<br>" \
    "Then follow the path on top of the cliff to get behind the trees.",
  ),
  Trick(
    name="Use Big Pig to Cut Down Outset Island Trees",
    description="To do this, first carry the pig to the trees. Then pick it up and throw it against the wall several times. For the tenth throw, instead of throwing it against the wall, throw it through the trees. " \
    "Being thrown ten times will enrage it, so it will start rushing at you, cutting the trees down in the process.",
  ),
  Trick(
    name="Reach Pillar Outside Forest Haven without Grappling Hook",
    description="You can access pillar outside Forest Haven by flying to the lowest elevated exit out of Forest Haven, and then flying southwest.<br>" \
    "From there, you can access the middle elevated platform exit or the dungeon entrance.",
  ),
  Trick(
    name="Boating Course Cave with Only Hookshot",
    description="Hitting the 3 diamond switches inside the cave with Hookshot without being able to kill the Miniblins is difficult and involves a lot of running around.",
  ),
  Trick(
    name="Cliff Plateau Isles Cave with Only Grappling Hook",
    description="You can kill a Boko Baba here by throwing a nut at it to stun it, then using the Grappling Hook to finish it off. Then you can take its Boko Stick.",
  ),
  Trick(
    name="Use Magic Armor While Salvaging",
    description="Magic Armor prevents you from being knocked out of the ship if you get hit by enemies while salvaging.",
  ),
  Trick(
    name="Salvage Without Killing Enemies",
    description="The enemies can get in the way when trying to salvage treasures, so being able to destroy them makes this easier.<br>" \
    "Without killing them, salvaging is more difficult but still possible.",
  ),
  Trick(
    name="Defeat Electric ChuChus with Grappling Hook and Sword",
    description="Grappling Hook stuns them just barely long enough for you to kill them with your sword. This is somewhat tricky to time.",
  ),
  Trick(
    name="Defeat Wizzrobes with Hookshot",
    description="The Hookshot requires twice as many hits as the Hero's Bow and is slower, making fighting Wizzrobes at range rather challenging.",
  ),
  Trick(
    name="Defeat Mighty Darknuts with Skull Hammer",
    description="Destroying the armor the slow way by hitting it repeatedly with spinning hammer attacks is extremely difficult, but it is possible, even with only 3 hearts.",
  ),
  Trick(
    name="Defeat Puppet Ganon Without Boomerang",
    description="You can snipe Puppet Ganon's tail without cutting his strings first, though this is fairly precise.<br>" \
    "Boomerang makes things significantly easier, both to cut down Puppet Ganon's strings and to defeat the keese who drop refills.",
  ),
  Trick(
    name="Reflect Light Arrows with Skull Hammer",
    description="You can also reflect the light arrows in the Ganondorf fight with the Skull Hammer.",
  ),
]

ALL_TRICK_NAMES: list[str] = sorted([trick.name for trick in ALL_TRICKS])
