
# 🎮 10 Second Life – Game Design Document

## 📌 Game Title
**10 Second Life: Echoes of a Short World**

## 🧠 Concept
You live a life that lasts only 10 seconds. Every run, your actions shape the world. Progress is made through short, impactful decisions. The more you explore, the deeper the story, mechanics, and world becomes.

## 🧩 Genre
2D Puzzle-Adventure / Exploration / Narrative Roguelite

## 🕹️ Platform
- Web (using Phaser.js or HTML5 Canvas)
- Python (using Pygame)

---

## 🎯 Objective
Progress through a mysterious world in 10-second lifespans. Uncover secrets, unlock paths, and influence a persistent world with each life.

---

## 🌀 Gameplay Loop

1. **Start Life (10s Timer Begins)**
2. Move around, interact with objects/NPCs
3. Game world reacts to your actions
4. Timer ends → “You Died” screen
5. Restart with world updated from previous choices

---

## 🗺️ World Layout

- **Zone 1: The Garden of Beginnings**  
  Tutorial-like open area with few objects (seed, tree, door, NPC)

- **Zone 2: Memory Cavern**  
  Dark underground puzzle area. Requires torch.

- **Zone 3: Clocktower Ruins**  
  A vertical climb, unlocks slow-time ability

- **Zone 4: The Mirror Realm**  
  A reversed world where time flows backward

- **Zone 5: Final Gate**  
  Requires specific actions over several lives to unlock

---

## 🧍 Characters

### 1. 🧒 The Player
- Role: The soul reliving short lives
- Abilities: Move, interact, pick/drop, use tools

### 2. 🌳 The Talking Tree
- Role: Remembers your past lives. Gives hints.
- Dialogue evolves with progress.

### 3. 🪞 The Mirror Twin
- Role: Opposes your actions. Unlocks puzzles when synced.

### 4. 👁️ The Watcher
- Role: Silent NPC that follows you after certain milestones

---

## 🔧 Core Mechanics

| Mechanic             | Description |
|----------------------|-------------|
| ⏱️ 10-Second Timer   | Each life lasts 10 seconds |
| 🧠 Memory Persistence | Certain actions (opening doors, planting seeds) persist |
| 🔁 Unlock Progression | New areas, characters, and story unlocked via progress |
| 🧩 Puzzle Solving     | Multi-life environmental puzzles |
| 🕰️ Time Power-Ups     | Temporarily slow down or reverse time (later) |
| 🪞 Parallel Realms     | World flips, affects puzzles |
| 🧱 Environmental Triggers | Doors, switches, objects that change state across lives |

---

## 🎨 Art & Sound Style

- **Visual**: Pixel art or minimalist line-art
- **Audio**: Lo-fi background music, heartbeat countdown, echoing sound effects

---

## 🧪 Sample Scenarios

### 🌱 Life 1:
- Walk to tree, plant a seed
- Tree remembers you planted it

### 🔥 Life 2:
- Use torch to burn vines
- Vines stay gone in future lives

### 🗝️ Life 3:
- Find a hidden key in cave
- Unlocks tower in life 4

---

## 📝 UI Elements

- Timer Countdown
- Text overlays: “You Died”, “Unlocked: Mirror Realm”
- Dialogue popups
- Action hint popups (e.g., “Press E to interact”)

---

## 📏 Rules

- Max time: 10 seconds per life
- Movement: 8-direction with keyboard or arrow keys
- Inventory: 1 item per life
- One action per object per life
- Persistent world state saved between lives

---

## 🧠 Technical Design

- Global `world_state` object (stores opened doors, NPC states, unlocked areas)
- Each run reads from `world_state`
- Modified at end of life based on player actions
- Timer resets every run

---

## 📦 File Structure Suggestion

```
/10-second-life
├── index.html
├── game.js
├── style.css
├── assets/
│   ├── sprites/
│   ├── tilesets/
│   ├── sounds/
└── data/
    └── worldState.json
```

---

## 🚀 Expansion Ideas

- Multiplayer: Two players with synced 10s lives
- Daily Challenge Mode
- Procedural World Generator
- Emotion-based music transitions
- Steam or Mobile Port

---

## 💡 Development Tools

- Phaser.js (Web)
- Pygame (Python)
- Tiled Map Editor
- Audacity for sound
- GPT or LLM for code generation

---

## ✅ MVP Goals (Within 4 Hours)

- 10s Timer with life loop
- Basic 2D map with 2-3 rooms
- Persistent world state
- 1–2 NPCs and one puzzle (like a locked door)
- Polished UX (timer UI, restart loop, basic sound)
