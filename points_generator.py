import random

with open('Input/points.txt', 'a') as file:
    # Generate 1000 points
    for _ in range(100):
        # Generate random x and y coordinates
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        
        # Write the coordinates to the file
        file.write(f"{x},{y}\n")