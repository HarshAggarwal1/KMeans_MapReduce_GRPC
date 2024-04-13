import matplotlib.pyplot as plt
import os
import random

centroid_coords = []

centroids = {}

for _, dirs, _ in os.walk("Mappers"):
    for dir in dirs:
        for _, _, files in os.walk(f"Mappers/{dir}"):
            for file in files:
                file = open(f"Mappers/{dir}/{file}", "r")
                for line in file:
                    centroid_index = int(line.split(",")[0])
                    x = float(line.split(",")[1])
                    y = float(line.split(",")[2])
                    if centroid_index not in centroids:
                        centroids[centroid_index] = []
                    centroids[centroid_index].append((x, y))

# plot the centroids and the points with their respective centroids in different colors

file = open("centroids.txt", "r")
for line in file:
    x, y = map(float, line.split(sep=","))
    centroid_coords.append((x, y))

colors = ["r", "g", "c", "m", "y", "k", "w", "orange", "purple", "brown", "pink", "gray", "olive", "cyan", "lime", "teal", "lavender", "maroon", "navy", "aquamarine", "gold", "coral", "indigo", "ivory", "khaki", "magenta", "orchid", "plum", "salmon", "sienna", "tan", "thistle", "tomato", "turquoise", "violet", "wheat", "yellow", "azure", "bisque", "blanchedalmond", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod", "gray", "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "mocc"]

for centroid_index in centroids:
    x = [point[0] for point in centroids[centroid_index]]
    y = [point[1] for point in centroids[centroid_index]]
    plt.scatter(x, y, color=colors[centroid_index])
    
    # plot the centroid coords
    plt.scatter(centroid_coords[centroid_index][0], centroid_coords[centroid_index][1], color=colors[centroid_index], marker="x")
    
plt.savefig("output.png")