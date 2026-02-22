from random import randint

def generate_room(maze, x, y, w, h, char="0"):
    for j in range(y, y + h):
        if 0 <= j < len(maze):
            row = maze[j]
            for i in range(x, x + w):
                if 0 <= i < len(row):
                    row[i] = char
    
    if randint(1, 2) == 1:
        center = get_center(x, y, w, h)
        maze[center[1]][center[0]] = "#"
        print("!!")

def get_center(x, y, w, h):
    return (x + w // 2, y + h // 2)

def generate_rooms(maze, maze_size, num_of_rooms, min_size, max_size, char, centers, occupied):
    w, h = maze_size
    for _ in range(num_of_rooms):
        room_w = randint(min_size[0], max_size[0])
        room_h = randint(min_size[1], max_size[1])
        x = randint(1, w - room_w - 1)
        y = randint(1, h - room_h - 1)

        # Перевірка зіткнення через сет зайнятих клітинок
        touching = False
        for j in range(y-1, y+room_h+1):
            for i in range(x-1, x+room_w+1):
                if (i,j) in occupied:
                    touching = True
                    break
            if touching:
                break

        if not touching:
            generate_room(maze, x, y, room_w, room_h, char)
            centers.append(get_center(x, y, room_w, room_h))
            # Додаємо всі клітини кімнати у сет
            for j in range(y, y + room_h):
                for i in range(x, x + room_w):
                    occupied.add((i,j))

def generate_line(x, y, maze, maze_size, min_len, max_len, char, direction):
    w, h = maze_size
    length = randint(min_len, max_len)
    horizontal = direction == 0  # True = горизонтально, False = вертикально

    for i in range(length):
        xi = x + i if horizontal else x
        yi = y if horizontal else y + i

        # Перевірка меж лабіринту
        if 0 <= xi < w and 0 <= yi < h:
            maze[yi][xi] = char
        

def carve_corridor(maze, start, end, occupied):
    x1, y1 = start
    x2, y2 = end

    if randint(0,1) == 0:
        for x in range(min(x1,x2), max(x1,x2)+1):
            maze[y1][x] = maze[y1+1][x] = "0"
            occupied.add((x,y1))
            occupied.add((x,y1+1))
        for y in range(min(y1,y2), max(y1,y2)+1):
            maze[y][x2] = maze[y][x2+1] = "0"
            occupied.add((x2,y))
            occupied.add((x2+1,y))
    else:
        for y in range(min(y1,y2), max(y1,y2)+1):
            maze[y][x1] = maze[y][x1+1] = "0"
            occupied.add((x1,y))
            occupied.add((x1+1,y))
        for x in range(min(x1,x2), max(x1,x2)+1):
            maze[y2][x] = maze[y2+1][x] = "0"
            occupied.add((x,y2))
            occupied.add((x,y2+1))

def generate(size, num_of_rooms, min_size, max_size, num_of_lines, min_size_l, max_size_l):
    w, h = size
    maze = [["1"] * w for _ in range(h)]
    centers = []
    occupied = set()  # сет всіх зайнятих клітин
    directions = {0: randint(6, 7), 1: randint(4, 5)}

    # Стартова кімната
    generate_room(maze, 1, 1, 3, 3)
    centers.append(get_center(1, 1, 3, 3))
    for j in range(1,4):
        for i in range(1,4):
            occupied.add((i,j))

    # Генерація кімнат різного типу
    for char in ["0","2","3"]:
        generate_rooms(maze, size, num_of_rooms, min_size, max_size, char, centers, occupied)
    
    for _ in range(num_of_lines):
        direction = randint(0,1)  # 0 = горизонтальна, 1 = вертикальна
        length = randint(min_size_l, max_size_l)
        
        c = "4"
        if direction == 0:  # горизонтальна
            x = randint(0, w - length - 1)
            y = randint(0, h - 1)
            c = str(randint(6, 7))
        else:  # вертикальна
            x = randint(0, w - 1)
            y = randint(0, h - length - 1)
            c = str(randint(4, 5))

        generate_line(x, y, maze, size, min_size_l, max_size_l, char=c, direction=direction)

    # Коридори
    for i in range(1, len(centers)):
        carve_corridor(maze, centers[i-1], centers[i], occupied)

    return maze