import numpy as np, cv2, os, ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


def address_fix(address):
    if address[0] and address[len(address)-1] in ('\'', '\"'):
        fixed_address = address[1:len(address)-1]
    else:
        fixed_address = address
    for i in range(len(address)):
        if address[i] == '\\':
            fixed_address = fixed_address[:i]+'/'+fixed_address[i+1:]
    return fixed_address


def file_type(name):
    file_types = ['.png', '.jpg', '.bmp', '.jpeg', '.tiff']
    for i in file_types:
        if i.upper() in name and '.xml' not in name or i in name:
            return True


def downscale(demonstrate):
    global ratio
    res = demonstrate.shape
    sy, sx = res[0], res[1]
    if sy > float(Height) * 0.9 or sx > float(Width) * 0.9:
        dsx, dsy = sx/(float(Width)*0.9), sy/(float(Height)*0.9)
        if dsx > dsy:
            ratio = 1/dsx
        else:
            ratio = 1/dsy
        downscaled = cv2.resize(demonstrate, (0, 0), fx=ratio, fy=ratio)
        return downscaled
    else:
        ratio = 1
        return demonstrate


def get_pic(table, location, pictures):
    global Height, Width
    sign = {9: 'SCALE', 13: 'A', 17: 'B', 21: 'V', 25: 'G', 29: 'D', 33: 'E'}
    color = [(255, 127, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0)]
    color_dict = {7: 0, 9: 0, 11: 1, 13: 1, 15: 1, 17: 1, 19: 2, 21: 2, 23: 2, 25: 2, 27: 3, 29: 3, 31: 3, 33: 3}
    drawn = []
    new_name = ''
    for a in range(1, len(table)):
        if table[a][0] in pictures:
            if (table[a][:7]) not in drawn:
                drawn.append((table[a][:7]))
                Width = table[a][1]
                Height = table[a][2]
                img = cv2.imread(location+'/'+table[a][0])
                img = img[int(table[a][3]):int(table[a][5]), int(table[a][4]):int(table[a][6])]
                img = downscale(img)
                if new_name not in drawn:
                    for c in range(len(table[a][0])):
                        if table[a][0][c] == '.':
                            new_name = table[a][0][0:c]
                            drawn.append(new_name)
                else:
                    new_name += '+'
        for b in range(7, 34, 2):
            cv2.circle(img, (int(float(table[a][b + 1])), int(float(table[a][b]))), 2, color[color_dict[b]], 1)
        for b in range(9, 34, 4):
            cv2.putText(img, sign[b], (int(float(table[a][b + 1])), int(float(table[a][b]))),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 100, 240), 1)
        cv2.imwrite(location+'/'+new_name+'\'s LM check'+'.png', img)


directory = address_fix(r'' + raw_input('Folder with measured images:'))
print directory
photos = [a for a in os.listdir(directory) if file_type(a) is True]
print photos
table = open(directory + '/LM table.txt', 'r')
read_table = table.read()

restored_table = []
table_row = []
cell_start = 0

for a in range(len(read_table)):
    if read_table[a:a+1] == '\n':
        restored_table.append(read_table[cell_start:a])
        cell_start = a+1

newer_table = []
for line in restored_table:
    new_line = []
    cell_start = 0
    for a in range(len(line)):
        if line[a:a+1] == '\t':
            new_line.append(line[cell_start:a])
            cell_start = a+1
    new_line.append(line[cell_start-1:len(line)])
    newer_table.append(new_line)

print newer_table, 'length', len(newer_table), '; row length', [len(a) for a in newer_table]
get_pic(newer_table, directory, photos)
