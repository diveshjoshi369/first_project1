''' Space invader game with Levels '''

# do these before running
''' >Change bo_speed and enemy speed according to your computer
    >Change 'D:/python saves/12vi project/' to your file location in your pc using ctrl + H
'''

# all of the modules
import turtle
import math
import random
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame # only for sound
pygame.mixer.init()
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time # for pause timing

#bas path for all resources
BASE_PATH = os.path.join(os.path.dirname(__file__), 'resources')
records_to_insert = [
    ("Vishwaraj", 7, 4520, "2025-05-15", "10:30:00", 1),
    ("Diksha", 10, 7890, "2025-06-03", "14:15:30", 2),
    ("Mayank", 12, 15000, "2025-07-20", "09:05:10", 3),
    ("Aryan", 6, 1850, "2025-05-28", "18:40:05", 0),
    ("Dhruv", 8, 3100, "2025-06-10", "11:22:45", 1),
    ("Vishwaraj", 5, 6200, "2025-07-01", "20:00:00", 2),
    ("Mayank", 9, 9150, "2025-05-01", "07:10:20", 2),
    ("Aryan", 11, 500, "2025-06-25", "16:55:12", 0),
    ("Shooter", 7, 15000, "2025-07-05", "13:00:00", 3), 
    ("Diksha", 10, 7050, "2025-05-20", "22:30:40", 2),
    ("Dhruv", 5, 15000, "2025-06-18", "08:00:00", 3), 
    ("Vishwaraj", 8, 950, "2025-07-11", "17:10:00", 0),
    ("Mayank", 12, 4000, "2025-05-05", "19:45:00", 1),
    ("Aryan", 6, 8200, "2025-06-22", "10:00:00", 2),
    ("Dhruv", 9, 1500, "2025-07-28", "15:30:00", 0),
    ("Diksha", 11, 3500, "2025-05-10", "12:00:00", 1),
    ("Shooter", 7, 15000, "2025-06-07", "21:00:00", 3), 
    ("Vishwaraj", 10, 15000, "2025-07-03", "06:45:00", 3),
    ("Mayank", 5, 750, "2025-05-25", "14:20:00", 0),
    ("Aryan", 8, 2800, "2025-06-14", "11:11:11", 1),
    ("Dhruv", 7, 5000, "2025-08-01", "09:00:00", 1),
    ("Diksha", 9, 9900, "2025-08-05", "17:30:00", 2), 
    ("Vishwaraj", 11, 2500, "2025-08-10", "13:45:00", 0),
    ("Mayank", 6, 7000, "2025-08-15", "10:00:00", 2),
    ("Aryan", 12, 1200, "2025-08-20", "16:00:00", 0)
]
# Setup screen
w = turtle.Screen()
w.bgcolor("black")
w.title("Space Invader game")
w.bgpic(os.path.join(BASE_PATH, "bg.gif"))
w.tracer(0)

#To have menu text appear slowly and gracefully
def slow_print(text, delay=0.02): #change speed
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def slow_input(prompt, delay=0.02): #change speed
    slow_print(prompt, delay=delay)
    return input()

#global varibales
score = 0
paused = False
muted = False
current_class = None
current_name = None

# SQL setup
con = sqlite3.connect("player_data")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS final_database (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Class INTEGER,
    Score INTEGER,
    Date TEXT,
    Time TEXT,
    Level_Cleared INTEGER
)''')
con.commit()

# Registering the shapes
w.register_shape(os.path.join(BASE_PATH, "d1.gif"))
w.register_shape(os.path.join(BASE_PATH, "d2.gif"))
w.register_shape(os.path.join(BASE_PATH, "d3.gif"))
w.register_shape(os.path.join(BASE_PATH, "con.gif"))
w.register_shape(os.path.join(BASE_PATH, "player.gif"))
w.register_shape(os.path.join(BASE_PATH, "e1.gif"))
w.register_shape(os.path.join(BASE_PATH, "e2.gif"))
w.register_shape(os.path.join(BASE_PATH, "boss.gif"))
w.register_shape(os.path.join(BASE_PATH, "ship.gif"))
w.register_shape(os.path.join(BASE_PATH, "def.gif"))
w.register_shape(os.path.join(BASE_PATH, "atk.gif"))

# Score display
so = turtle.Turtle()
so.speed(0)
so.color("white")
so.penup()
so.setposition(-290, 280)
scorestring = "Score: {}".format(score)
so.write(scorestring, False, align="left", font=("arial", 14, "normal"))
so.hideturtle()

# Player
p = turtle.Turtle()
p.color("blue")
p.shape(os.path.join(BASE_PATH, "player.gif"))
p.penup()
p.speed(0)
p.setposition(0, -250)
p.setheading(90)
p.playerspeed = 0.50

# Bullet
bullets = []
bo_speed = 0.5 # speed of bullet!!
boss_bo = []
boss_bo_speed = -0.2 # downward movement
boss_delay = {}  
# Sound functions
def toggle_mute():
    global muted
    muted = not muted
    if muted:
        pygame.mixer.music.pause()
        slow_print("Game Muted")
    else:
        pygame.mixer.music.unpause()
        slow_print("Game Unmuted")

def sound_effect(file):
    global muted
    if not muted:
        effect = pygame.mixer.Sound(file)
        effect.play()

# Movement functions
def m_left():
    p.playerspeed = -0.50

def m_right():
    p.playerspeed = 0.50

def move_player():
    if paused: return
    try:
        x = p.xcor()
        x += p.playerspeed
        x = max(-280, min(280, x))
        p.setx(x)
    except turtle.TurtleGraphicsError:
        pass # ignore movement if window is closed

# Bullet fire
def fire_bullet():
    if paused:
        return

    if len(bullets) >= 5: # Max bullets
        return

    sound_effect(os.path.join(BASE_PATH, "lazer.wav"))
    new_bullet = turtle.Turtle()
    new_bullet.color("yellow")
    new_bullet.shape(os.path.join(BASE_PATH, "def.gif"))
    new_bullet.penup()
    new_bullet.speed(0)
    new_bullet.setheading(90)
    new_bullet.shapesize(0.50, 0.50)
    x = p.xcor()
    y = p.ycor() + 10
    new_bullet.setposition(x, y)
    bullets.append(new_bullet)

def boss_fire(ship):
    if len(boss_bo) >= 5:
        return
    bo = turtle.Turtle()
    bo.color("red")
    bo.shape(os.path.join(BASE_PATH, "atk.gif"))
    bo.penup()
    bo.speed(0)
    bo.setheading(270)
    bo.shapesize(0.5, 0.5)
    bo.setposition(ship.xcor(), ship.ycor() - 20)
    boss_bo.append(bo)

# Collision
def collision(t1, t2):
    if t2.shape() == os.path.join(BASE_PATH, "boss.gif"):
        return t1.distance(t2) < 45 # Bigger hitbox for boss
    elif t2.shape() == os.path.join(BASE_PATH, "ship.gif"):
        return t1.distance(t2) < 32 # Bigger hitbox for ship
    else:
        # Changed player hitbox for enemy touch for death to 18
        return t1.distance(t2) < 18

def save_score(score):
    global current_name, current_class
    name = current_name
    class_ = current_class
    date = datetime.date.today().isoformat()
    time_ = datetime.datetime.now().strftime("%H:%M:%S")
    level_cleared = get_level_cleared(score)

    cur.executemany('''
        INSERT INTO final_database (Name, Class, Score, Date, Time, Level_Cleared)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records_to_insert)
    slow_print("Score saved successfully!")
    con.commit() # Commit the changes to the database
    con.close()  # Close the connection

    print("20 sample records added successfully!")

# Analyze Scores
def analyze_scores():
    df = pd.read_sql_query("SELECT * FROM player_data", con)

    slow_print("\n--- Game Stats ---")
    slow_print(df.to_string(index=False))


    if df.empty:
        slow_print("No game data available yet.")
        return

    # Average Score
    avg = df["Score"].mean()
    slow_print(f"\nAverage Score: {avg:.2f}")

    # Games played per month
    df['month'] = pd.to_datetime(df['Date']).dt.month_name()
    games_by_month = df['month'].value_counts()

    slow_print("\nGames played per month:")
    slow_print(games_by_month.to_string())
    slow_input("\nPress Enter to return to the main menu...")


    # Bar graph for games played per month
    plt.figure(figsize=(8, 5), num="Games Played per Month") # Added window title
    games_by_month.plot(kind='bar', color='skyblue')
    plt.title("Games Played per Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Games")
    plt.tight_layout()
    plt.show()

# Background music
pygame.mixer.music.load(os.path.join(BASE_PATH, "bgm.wav"))
pygame.mixer.music.play(-1)

def get_level_cleared(score):
    if score == 10000:
        return 3
    elif score > 6000:
        return 2
    elif score > 2000:
        return 1
    else:
        return 0

# Main menu
def menu():
    while True:
        slow_print("\n====== SPACE INVADERS GAME MAIN MENU ======")
        slow_print("1. Your Record")
        slow_print("2. View Scoreboard")
        slow_print("3. View Statistics")
        slow_print("4. Exit")
        choice = slow_input("Enter your choice (1-4): ").strip()

        if choice == '1':
            record_menu()
        elif choice == '2':
            view_scoreboard()
        elif choice == '3':
            view_statistics()
        elif choice == '4':
            slow_print("Exiting game. Goodbye!")
            con.close()
            pygame.quit()
            sys.exit()
        else:
            slow_print("Invalid choice. Please try again.")

def record_menu():
    global current_name, current_class
    while True:
        slow_print("\n--- YOUR RECORD ---")
        slow_print(f"Current Name: {current_name or 'Not set'}")
        slow_print(f"Current Class: {current_class or 'Not set'}")
        slow_print("1. Return to Main Menu")
        slow_print("2. Change Name")
        slow_print("3. Change Class")
        slow_print("4. View Record (your saved games)")
        choice = slow_input("Choose option: ").strip()

        if choice == '1':
            break

        elif choice == '2':
            current_name = slow_input("Enter new name: ")

        elif choice == '3':
            current_class = slow_input("Enter new class: ")

        elif choice == '4':
            if not current_name or not current_class:
                slow_print("Set name and class first.")
                continue
            df = pd.read_sql_query(
                "SELECT * FROM player_data WHERE Name = ? AND Class = ?",
                con, params=(current_name, current_class))
            if not df.empty:
                slow_print(df.to_string(index=False))
            else:
                slow_print("No records found.")

        else:
            slow_print("Invalid option.")

def view_scoreboard():
    df = pd.read_sql_query("SELECT * FROM player_data ORDER BY Score DESC", con).head(10)
    slow_print("\n--- SCOREBOARD ---")
    if df.empty:
        slow_print("No scores recorded yet.")
    else:
        df['Rank'] = range(1, len(df) + 1)
        cols = ['Rank', 'Name', 'Class', 'Score', 'Date', 'Time', 'Level_Cleared']
        slow_print(df[cols].to_string(index=False))


def view_statistics():
    df = pd.read_sql_query("SELECT * FROM player_data", con)
    if df.empty:
        slow_print("No game statistics available.")
        return

    while True:
        slow_print("\n===== GAME STATISTICS =====")
        slow_print("1. Level Cleared by People ")
        slow_print("2. Games Played by Day of the Week")
        slow_print("3. Monthly Games and Average Score Trend")
        slow_print("4. Average Score by Class")
        slow_print("5. Average Score of Winning vs. Losing Games") # Menu text for option 5 from ERRROR.py
        slow_print("6. Highest Score per Class")
        slow_print("7. Score Distribution Histogram")
        slow_print("8. Back to Main Menu")
        slow_print("9. Wanna know about the best player?") # Option 9 from ERRROR.py
        choice = slow_input("Choose option: ").strip()

        if choice == '1':
            plt.figure(figsize=(8, 8), num="Level Cleared Distribution") # Added window title
            level_counts = df['Level_Cleared'].value_counts().sort_index()
            level_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, title='Level Cleared by People')
            plt.show()

        elif choice == '2':
            slow_print("--- Games Played by Day of the Week ---")
            df_temp = pd.read_sql_query("SELECT Date FROM player_data", con)
            if df_temp.empty:
                slow_print("No game data available yet.")
                continue

            df_temp['day_of_week'] = pd.to_datetime(df_temp['Date']).dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = df_temp['day_of_week'].value_counts().reindex(day_order).fillna(0)

            if not day_counts.empty:
                plt.figure(figsize=(9, 6), num="Games Played by Day of Week") # Added window title
                day_counts.plot(kind='bar', title='Games Played by Day of the Week', color='orange')
                plt.xlabel("Day of Week")
                plt.ylabel("Number of Games")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
            else:
                slow_print("No game data available for this analysis.")


        elif choice == '3':
            slow_print("--- Monthly Games and Average Score Trend ---")
            df_temp = pd.read_sql_query("SELECT Date, Score FROM player_data", con)
            if df_temp.empty:
                slow_print("No records found to analyze.")
                continue

            df_temp['date'] = pd.to_datetime(df_temp['Date'])
            df_temp['month_year'] = df_temp['date'].dt.to_period('M')

            monthly_data = df_temp.groupby('month_year').agg(
                games_played=('date', 'size'),
                avg_score=('Score', 'mean')
            ).sort_values(by='month_year')

            if not monthly_data.empty:
                fig, ax1 = plt.subplots(figsize=(10, 6), num="Monthly Game Trends") # Added window title

                # Bar chart for Games Played
                ax1.bar(monthly_data.index.astype(str), monthly_data['games_played'], color='lightseagreen', alpha=0.7, label='Games Played')
                ax1.set_xlabel('Month-Year')
                ax1.set_ylabel('Games Played', color='lightseagreen')
                ax1.tick_params(axis='y', labelcolor='lightseagreen')
                ax1.set_title('Monthly Games and Average Score Trend')
                ax1.tick_params(axis='x', rotation=45)

                ax2 = ax1.twinx()
                ax2.plot(monthly_data.index.astype(str), monthly_data['avg_score'], color='firebrick', marker='o', linestyle='-', label='Average Score')
                ax2.set_ylabel('Average Score', color='firebrick')
                ax2.tick_params(axis='y', labelcolor='firebrick')

                fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
                plt.tight_layout()
                plt.show()
            else:
                slow_print("No monthly data available for analysis.")

        elif choice == '4':
            slow_print("--- Average Score by Class ---")
            df_temp = pd.read_sql_query("SELECT Class, Score FROM player_data", con)
            if df_temp.empty:
                slow_print("No records found to analyze.")
                continue

            avg_score_by_class = df_temp.groupby('Class')['Score'].mean().round(2)

            if not avg_score_by_class.empty:
                plt.figure(figsize=(9, 6), num="Average Score by Player Class") # Added window title
                avg_score_by_class.plot(kind='bar', title='Average Score by Player Class', color='mediumpurple')
                plt.xlabel('Player Class')
                plt.ylabel('Average Score')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
            else:
                slow_print("No class data available for analysis.")
        elif choice == '5': # Changed to calculate Average Score of Winning vs. Losing Games
            slow_print("--- Average Score: Win vs. Loss ---")
            df_temp = pd.read_sql_query("SELECT Score, Level_Cleared FROM player_data", con)
            if df_temp.empty:
                slow_print("No records found to analyze.")
                continue

            winning_scores = df_temp[df_temp['Level_Cleared'] == 3]['Score'] # Level 3 is considered a win
            losing_scores = df_temp[df_temp['Level_Cleared'] < 3]['Score'] # Levels 0, 1, 2 are losses

            avg_win_score = winning_scores.mean() if not winning_scores.empty else 0
            avg_loss_score = losing_scores.mean() if not losing_scores.empty else 0

            plot_data = pd.DataFrame({
                'Category': ['Wins', 'Losses'],
                'Average Score': [avg_win_score, avg_loss_score]
            })

            if not plot_data.empty:
                plt.figure(figsize=(7, 5), num="Average Score by Game Outcome") # Added window title
                plt.bar(plot_data['Category'], plot_data['Average Score'], color=['forestgreen', 'darkred'])
                plt.xlabel('Game Outcome')
                plt.ylabel('Average Score')
                plt.title('Average Score for Winning vs. Losing Games')
                plt.ylim(0, max(avg_win_score, avg_loss_score) * 1.1) # Set y-axis limit
                plt.tight_layout()
                plt.show()
            else:
                slow_print("No data available to compare win vs. loss scores.")

        elif choice == '6':
            slow_print("--- Highest Score per Class ---")
            df_temp = pd.read_sql_query("SELECT Class, Score FROM player_data", con)
            if df_temp.empty:
                slow_print("No records found to analyze.")
                continue

            highest_score_by_class = df_temp.groupby('Class')['Score'].max().sort_values(ascending=True)

            if not highest_score_by_class.empty:
                plt.figure(figsize=(9, 6), num="Highest Score per Player Class") # Added window title

                plt.hlines(y=highest_score_by_class.index, xmin=0, xmax=highest_score_by_class.values, color='skyblue', linewidth=3)

                plt.plot(highest_score_by_class.values, highest_score_by_class.index, "o", color='darkblue', markersize=8)

                plt.xlabel('Highest Score')
                plt.ylabel('Player Class')
                plt.title('Highest Score per Player Class')
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.show()
            else:
                slow_print("No class data available for analysis.")

        elif choice == '7':
            slow_print("--- Score Distribution Histogram ---")
            df_temp = pd.read_sql_query("SELECT Score FROM player_data", con)
            if df_temp.empty:
                slow_print("No records found to analyze.")
                continue

            mean_score = df_temp['Score'].mean()

            plt.figure(figsize=(10, 6), num="Score Distribution") # Added window title
            plt.hist(df_temp['Score'], bins=15, color='purple', alpha=0.7, rwidth=0.85)

            plt.axvline(mean_score, color='red', linestyle='dashed', linewidth=2, label=f'Average Score: {mean_score:.2f}')

            plt.xlabel("Score")
            plt.ylabel("Frequency")
            plt.title("Score Distribution")
            plt.grid(axis='y', alpha=0.75)
            plt.legend()
            plt.tight_layout()
            plt.show()

        elif choice == '8':
            break
        elif choice == '9': # Option 9 logic from ERRROR.py
            slow_print("Divesh Joshi is the best player yet with the Score of 10,000,000")

        else:
            slow_print("Invalid option.")

# Pause button
def pause():
    global paused
    paused = not paused
    if paused:
        slow_print("Game Paused")
    else:
        slow_print("Game Resumed")

# Quiting game
def quit_game():
    global score
    slow_print("\nYou quit the game!")
    end_game(score, message="Game Over! (Quit Pressed)")

# Death or win screen
def show_result_screen(image, sound=None):
    w.clearscreen()
    w.bgcolor("black")
    w.bgpic(image)
    if sound:
        sound_effect(sound)
    w.update()
    time.sleep(5)

def end_game(score, message="Game Over!"):
    slow_print(f" {message} ")
    slow_print(f"Final Score: {score}")
    pygame.mixer.music.stop()
    try:
        turtle.bye()
    except turtle.Terminator:
        pass
    except Exception as e: # Added from main.py, good for error handling
        print(f"An unexpected error occurred during turtle shutdown: {e}")


    global current_name, current_class

    current_name = slow_input("Enter your name: ")
    current_class = slow_input("Enter your class: ")

    save_score(score)
    menu()

# Key controls
w.listen()
w.onkeypress(m_left, "Left")
w.onkeypress(m_right, "Right")
w.onkeypress(fire_bullet, "Up")
w.onkeypress(pause, "space")
w.onkeypress(quit_game, "q")
w.onkeypress(quit_game, "Q") # Added for uppercase 'Q' from ERRROR.py
w.onkeypress(toggle_mute, "m")
w.onkeypress(toggle_mute, "M") # Added for uppercase 'M' from ERRROR.py

# Create enemies
def create_enemies(level):
    enemies = []

    p.hideturtle() # hide player
    for bullet in bullets:
        bullet.hideturtle()
    bullets.clear() # reset bullet list

    for t in turtle.turtles(): # hide any stray turtles (including old enemies)
        t.hideturtle()


    current_healths = []

    if level == 1:
        w.bgpic(os.path.join(BASE_PATH, "n.gif")) # Transition background
        sound_effect(os.path.join(BASE_PATH, "entry.wav")) # Play entry sound here
        w.update()
        time.sleep(5) # Short pause after transition

        slow_print("Level 1 Starting...")
        w.bgpic(os.path.join(BASE_PATH, "bg.gif")) # Level background
        current_healths = [1] * 20 # 20 enemies with 1 health (e1.gif)

    elif level == 2:
        w.bgpic(os.path.join(BASE_PATH, "n1.gif"))
        sound_effect(os.path.join(BASE_PATH, "entry.wav"))
        w.update()
        time.sleep(5)

        slow_print("Level 2 Starting...")
        w.bgpic(os.path.join(BASE_PATH, "bg2.gif"))
        current_healths =  [2] * 20 # 20 e1 enemies + 10 e2 enemies

    elif level == 3:
        w.bgpic(os.path.join(BASE_PATH, "n2.gif"))
        sound_effect(os.path.join(BASE_PATH, "entry.wav"))
        w.update()
        time.sleep(5)

        slow_print("Ultimate Boss Battle!")
        w.bgpic(os.path.join(BASE_PATH, "bg3.gif"))

        # Main Boss Spaceship (Center)
        m_boss = turtle.Turtle()
        m_boss.penup()
        m_boss.speed(0)
        m_boss.shape(os.path.join(BASE_PATH, "ship.gif"))
        m_boss.health = 20
        m_boss.setposition(0, 250)
        enemies.append(m_boss)

        # Left Sidekick Boss
        l_boss = turtle.Turtle()
        l_boss.penup()
        l_boss.speed(0)
        l_boss.shape(os.path.join(BASE_PATH, "boss.gif"))
        l_boss.health = 8
        l_boss.setposition(-150, 220)
        enemies.append(l_boss)

        # Right Sidekick Boss
        r_boss = turtle.Turtle()
        r_boss.penup()
        r_boss.speed(0)
        r_boss.shape(os.path.join(BASE_PATH, "boss.gif"))
        r_boss.health = 8
        r_boss.setposition(150, 220)
        enemies.append(r_boss)
        current_healths = []

    else:
        w.bgpic(os.path.join(BASE_PATH, "n3.gif"))
        current_healths = []


    start_y = 250
    spacing_x = 50
    spacing_y = 50
    start_x = -260

    for idx, hp in enumerate(current_healths):
        e = turtle.Turtle()
        e.penup()
        e.speed(0)
        # Choose shape based on health (1 for e1, 2 for e2)
        e.shape(os.path.join(BASE_PATH, "e1.gif")) if hp == 1 else e.shape(os.path.join(BASE_PATH, "e2.gif"))
        e.health = hp
        x = start_x + (idx % 10) * spacing_x
        y = start_y - (idx // 10) * spacing_y
        e.setposition(x, y)
        enemies.append(e)

    p.showturtle() # Show player after all enemies are created
    return enemies

'''    MAIN GAME LOOP    '''

def start_game():
    global score
    game_over = False
    bullets.clear() # reset bullet list

    try:
        level = 3       # start level 
        level_speeds = {1: 0.080, 2: 0.080, 3: 0.050}       #enemy speed
        e_speed = level_speeds[level]
        en = create_enemies(level)

        pygame.mixer.music.load(os.path.join(BASE_PATH, "bgm.wav"))
        pygame.mixer.music.play(-1)

        while not game_over :
            try:
                w.update()
                if paused:
                    continue
                move_player()
            except turtle.Terminator:
                slow_print("Turtle window closed during game. Exiting.")
                return


            enemy_drop = False

            for e in en:
                x = e.xcor() + e_speed
                e.setx(x)


                enemy_width = 0
                if e.shape() in [os.path.join(BASE_PATH, "e1.gif"), os.path.join(BASE_PATH, "e2.gif")]:
                    enemy_width = 12
                elif e.shape() == os.path.join(BASE_PATH, "boss.gif"):
                    enemy_width = 32
                elif e.shape() == os.path.join(BASE_PATH, "ship.gif"):
                    enemy_width = 32


                if e.xcor() + enemy_width > 300 or e.xcor() - enemy_width < -300:
                    enemy_drop = True

                if e.shape() == os.path.join(BASE_PATH, "ship.gif"):
                    current_time = time.time()
                    last_fired = boss_delay.get(e, 0)
                    if current_time - last_fired >= 1:  # 1-second cooldown
                        boss_fire(e)
                        boss_delay[e] = current_time


            if enemy_drop:
                e_speed *= -1
                for s in en:
                    s.sety(s.ycor() - 40)


            # Move and handle bullets
            for bullet in bullets[:]:
                bullet.sety(bullet.ycor() + bo_speed)

                if bullet.ycor() > 275:
                    bullet.hideturtle()
                    bullets.remove(bullet)
                    continue

                for e in en:
                    if collision(bullet, e):
                        bullet.hideturtle()
                        if bullet in bullets:
                            bullets.remove(bullet)

                        if e.shape() in [os.path.join(BASE_PATH, "e2.gif"), os.path.join(BASE_PATH, "boss.gif"), os.path.join(BASE_PATH, "ship.gif")]:
                            sound_effect(os.path.join(BASE_PATH, "explo.wav"))

                        e.health -= 1
                        if e.health <= 0:
                            e.setposition(0, 10000)
                            if e.shape() == os.path.join(BASE_PATH, "e2.gif"):
                                score += 200
                            elif e.shape() == os.path.join(BASE_PATH, "boss.gif"):
                                score += 1100
                            elif e.shape() == os.path.join(BASE_PATH, "ship.gif"): # Added Score for main boss
                                score += 1800
                            else:
                                score += 100

                            scorestring = "Score: {}".format(score)
                            so.clear()
                            so.write(scorestring, False, align="left", font=("arial", 15, "normal"))
                        break # One bullet should hit only one enemy
            for bo in boss_bo[:]:
                bo.sety(bo.ycor() + boss_bo_speed)

                if bo.ycor() < -280:
                    bo.hideturtle()
                    boss_bo.remove(bo)

                elif collision(bo, p):
                    bo.hideturtle()
                    boss_bo.remove(bo)
                    p.hideturtle()
                    sound_effect(os.path.join(BASE_PATH, "dead.wav"))
                    show_result_screen(os.path.join(BASE_PATH, "d3.gif"), sound=os.path.join(BASE_PATH, "lose.wav"))
                    end_game(score, message="Killed by Spaceship Attack!")
                    return
                        
            # Check for player collision
            for e in en:
                if collision(p, e):
                    sound_effect(os.path.join(BASE_PATH, "dead.wav"))
                    p.hideturtle()
                    e.hideturtle()

                    # Show result screen based on level immediately before calling end_game
                    if level == 1:
                        show_result_screen(os.path.join(BASE_PATH, "d1.gif"), sound=os.path.join(BASE_PATH, "lose.wav"))
                    elif level == 2:
                        show_result_screen(os.path.join(BASE_PATH, "d2.gif"), sound=os.path.join(BASE_PATH, "lose.wav"))
                    elif level == 3:
                        show_result_screen(os.path.join(BASE_PATH, "d3.gif"), sound=os.path.join(BASE_PATH, "lose.wav"))

                    end_game(score, message="Game Over! Better luck next time!")

                    return

            # Check if level is cleared
            alive = [e for e in en if e.ycor() < 5000 and e.health > 0]
            if len(alive) == 0:
                if level < 3:
                    slow_print(f"You WON against Level {level}!")
                level += 1
                if level > 3:
                     score += 5000 # Bonus Score
                     show_result_screen(os.path.join(BASE_PATH, "con.gif"), sound=os.path.join(BASE_PATH, "win.wav"))
                     end_game(score, message="!! Congratulations, You WON all levels !!")

                else:
                    e_speed = level_speeds.get(level, 0.060)
                    en = create_enemies(level)
                    bullets.clear() # clear bullets between levels

    except turtle.Terminator:
        slow_print("Turtle graphics window was closed. Exiting the program...")
        con.close()
        pygame.quit()
        sys.exit()

start_game()
