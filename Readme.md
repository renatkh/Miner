# Simple Game  
   
A simple grid-based game built with Python and Pygame.  
   
## Overview  
   
"Simple Game" is a grid-based adventure game where you navigate a player through a world filled with materials, ores, water, lava, and zombies. Collect resources, craft items like buckets, and strategically use them to overcome obstacles and enemies.  
   
## Installation  
   
### Prerequisites  
   
- **Python 3.x** installed on your system. You can download Python from [here](https://www.python.org/downloads/).  
- **Pip** (Python package installer) should be installed. It usually comes with Python.  
   
### Clone the Repository  
   
You can clone the repository using git (if you have it installed):  
   
```bash  
git clone <repository-url>  
```  
   
Or you can download the source code as a ZIP file and extract it.  
   
### Install Dependencies  
   
1. Navigate to the project directory in your terminal or command prompt:  
  
   ```bash  
   cd <project-directory>  
   ```  
   
2. Create a `requirements.txt` file with the following content:  
  
   **requirements.txt**  
  
   ```  
   pygame  
   ```  
   
3. Install the required packages using `pip` and the `requirements.txt` file:  
  
   ```bash  
   pip install -r requirements.txt  
   ```  
  
   Alternatively, you can install Pygame directly:  
  
   ```bash  
   pip install pygame  
   ```  
   
## Running the Game  
   
To start the game, run the `game.py` script:  
   
```bash  
python game.py  
```  
   
Make sure you are in the directory where `game.py` is located.  
   
## Game Controls  
   
- **Movement:**  
  
  - **Arrow Keys**: Move the player up, down, left, or right.  
   
- **Actions:**  
  
  - **`w`, `a`, `s`, `d`**: Interact with the square in the corresponding direction (up, left, down, right). Use these to mine materials or attack zombies.  
  - **`p`**: Place a material block at the player's current position (if you have materials in your inventory).  
  - **`Enter`**: Place a green ore block in front of the player (requires green ore in inventory).  
  - **`b`**: Craft a bucket (requires 1 green ore).  
  - **`Shift`**: Use the bucket to pick up lava or water (if adjacent to the player).  
  - **`Alt`**: Use the bucket to pour its contents to create obsidian (if adjacent to the opposite element).  
   
- **Exiting the Game:**  
  
  - **Click the close button** on the game window.  
   
## Game Rules  
   
### Objective  
   
Reach the obsidian tile with at least **2 blue ores** in your inventory to complete the level.  
   
### Game Elements  
   
- **Player**: Represented by a green square on the grid. You can move around, collect resources, craft items, and interact with the environment.  
   
- **Materials**: Brown squares that can be mined and collected into your inventory. Use them to block paths or create barriers.  
   
- **Blue Ore**: Blue squares that can be collected. You need at least **2 blue ores** to complete the level.  
   
- **Green Ore**: Dark green squares that can be collected. Use green ores to craft buckets or place them on the grid.  
   
- **Water**: Light blue squares that form pools. Water is initially placed on the grid and does not spread during gameplay.  
   
- **Lava**: Orange squares that form pools. Contact with lava is lethal to the player and zombies.  
   
- **Obsidian**: Purple squares formed when water and lava interact. Reach obsidian tiles to complete the level.  
   
- **Zombies**: Red squares that chase the player. Zombies have health and can be defeated by attacking them.  
   
### Crafting and Using Items  
   
- **Bucket**:  
  
  - **Crafting**: Press **`b`** while you have at least **1 green ore** to craft a bucket.  
  - **Using the Bucket**:  
  
    - **Filling**: Press **`Shift`** while adjacent to water or lava to fill the bucket.  
    - **Pouring**: Press **`Alt`** while adjacent to the opposite element (lava if carrying water, or water if carrying lava) to create obsidian.  
   
### Interactions  
   
- **Mining**:  
  
  - Use **`w`, `a`, `s`, `d`** to mine material blocks in the specified direction.  
  - Mining collects materials into your inventory.  
   
- **Placing Blocks**:  
  
  - Press **`p`** to place a material block at your current position (requires materials in inventory).  
  - Press **`Enter`** to place a green ore block in front of you (requires green ore in inventory).  
   
- **Combat**:  
  
  - Use **`w`, `a`, `s`, `d`** to attack zombies in the specified direction.  
  - Zombies have health and may drop blue ores upon defeat.  
   
- **Zombies**:  
  
  - Zombies move towards the player and can attack if adjacent.  
  - Avoid or defeat zombies to survive.  
   
### Health and Game Over  
   
- The player starts with **5 health points**.  
- Getting attacked by zombies or stepping into lava reduces health.  
- If health drops to zero, the game is over.  
   
### Level Progression  
   
- Upon completing a level, you proceed to the next with increased difficulty.  
- Each new level adds more zombies to the game.  
   
## Dependencies  
   
- **Python 3.x**  
- **Pygame**: Install via `pip install pygame`  
   
## Tips and Strategies  
   
- **Collect Resources**: Gather materials and ores to craft items and prepare for encounters with zombies.  
- **Use the Bucket Wisely**: Craft a bucket to manipulate water and lava, creating obsidian to block paths or create new routes.  
- **Plan Your Moves**: Be cautious around zombies and plan your attacks when they are vulnerable.  
- **Avoid Lava**: Stepping into lava is lethal. Be careful when navigating near lava pools.  
   
## Credits  
   
- Developed by [Your Name or Team Name]  
   
## License  
   
[Specify the license if any]  
   
---  
   
**Enjoy the game! If you have any questions or encounter issues, feel free to reach out.**