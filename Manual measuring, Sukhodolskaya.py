import numpy as np, cv2, os, copy, math, ctypes

Latency, Pressed, SCALE = 300, None, 10.0
user32 = ctypes.windll.user32; user32.SetProcessDPIAware()
Width, Height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1); print(type(Width), Width, type(Height), Height)


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
    if sy > Height * 0.9 or sx > Width * 0.9:
        dsx, dsy = sx/(Width*0.9), sy/(Height*0.9)
        if dsx > dsy:
            ratio = 1/dsx
        else:
            ratio = 1/dsy
        downscaled = cv2.resize(demonstrate, (0, 0), fx=ratio, fy=ratio)
        return downscaled
    else:
        ratio = 1
        return demonstrate


def write_down(output_table, output_directory):
    global SCALE
    header = 'Photo\tScale\tA\tB\tV\tG\tD\tE\tSex\n'
    hor, ver = [15, 23, 31], [11, 19, 27]
    for a in output_table[1:]:
        for b in ver:
            if a[b] > a[b+2]:
                col_buff, row_buff = a[b + 2], a[b + 3]
                a[b+2], a[b+3] = a[b], a[b+1]
                a[b], a[b+1] = col_buff, row_buff
        for b in hor:
            if a[b+1] > a[b+3]:
                col_buff, row_buff = a[b], a[b+1]
                a[b], a[b+1] = a[b+2], a[b+3]
                a[b+2], a[b+3] = col_buff, row_buff
        header += a[0]+'\t'
        row_scale = math.sqrt((a[7] - a[9]) ** 2 + (a[8] - a[10]) ** 2); header += str(row_scale) + '\t'
        for c in range(11, 35, 4):
            header += str(SCALE * math.sqrt((a[c+2]-a[c])**2+(a[c+3]-a[c+1])**2) / row_scale) + '\t'
        header += a[35]
    string_table = ''
    for line in output_table:
        for item_num in range(len(line)):
            line_item = str(line[item_num]); string_table += line_item
            if '\n' not in line_item:
                string_table += '\t'
    with open(output_directory+'/LM table.txt', 'w') as results1:
        results1.write(string_table)
        results1.close()
    with open(output_directory+'/Measures table.txt', 'w') as results2:
        results2.write(header)
        results2.close()


def lm_points(event, lm_col, lm_row, flags, param):
        global order, table_row, error_counter, Pressed
        if event == cv2.EVENT_LBUTTONDOWN and order < 14:
            order += 1
            print('LM_#'+str(order), lm_row, lm_col)
            if order <= 14:
                table_row.extend([float(lm_row), float(lm_col)])
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            if order <= 2 or len(table_row) <= 9:
                print('No measuring to discard for the current beetle')
            else:
                print('LM_#' + str(order) + '\'s discarded')
                table_row = table_row[0:len(table_row)-2]
                order -= 1


def trim(event, col, row, flags, param):
    global t, l, b, r, Pressed
    warning = None
    if event == cv2.EVENT_LBUTTONDOWN:
        warning = False
        l, t = col, row
        print('top-left', t, l)
    elif event == cv2.EVENT_RBUTTONDOWN:
        r, b = col, row
        warning = False
        print('bottom-right', b, r)
    if (t > b or l > r) and warning is False:
        print('Mixed up corners!')
    elif (t == b or l == r) and warning is False:
        print('No area selected!')


table = [['Photo', 'Screen width', 'Screen height',
          't', 'l', 'b', 'r',
          'SP1R', 'SP1C', 'SP2R', 'SP2C',
          'AAR', 'AAC', 'APR', 'APC',
          'BLR', 'BLC', 'BRR', 'BRC',
          'VAR', 'VAC', 'VPR', 'VPC',
          'GLR', 'GLC', 'GRR', 'GRC',
          'DAR', 'DAC', 'DPR', 'DPC',
          'ELR', 'ELC', 'ERR', 'ERC', 'Sex\n']]
trimmingKeys, measureKeys = ['q', 'c', 'r', 'p'], ['q', 's', 'v', 't', 'p', 'z']
trimmingActionKeys, measureActionKeys = [], []
for a in trimmingKeys:
    trimmingActionKeys.extend([ord(a), ord(a.upper())])
for a in measureKeys:
    measureActionKeys.extend([ord(a), ord(a.upper())])

while True:
    try:
        directory = address_fix(r'' + input('Folder with your images:'))
        photos = [a for a in os.listdir(directory) if file_type(a) is True]
        break
    except Exception as WindowsError:
        print('Wrong folder directory, repeat input.')
global break_var, skip_var
break_var, skip_var, Photo_num = False, False, 0
while True:
    if Photo_num >= len(photos) or break_var is True:
        break
    photo_dir = directory + '/' + photos[Photo_num]; print(photo_dir)
    img = cv2.imread(photo_dir, 1)
    imgdsc = downscale(img)
    cv2.namedWindow(photos[Photo_num])
    cv2.setMouseCallback(photos[Photo_num], trim)
    t, l, b, r, Pressed = 0, 0, imgdsc.shape[0]-1, imgdsc.shape[1]-1, None
    while True:
        layer = copy.copy(imgdsc)
        layer[t:b, l], layer[t, l:r] = (0, 0, 255), (0, 0, 255)
        layer[t:b, r], layer[b, l:r] = (255, 0, 0), (255, 0, 0)
        cv2.imshow(photos[Photo_num], layer)
        Pressed = cv2.waitKey(Latency)
        if Pressed in trimmingActionKeys:
            if Pressed == ord('q') or Pressed == ord('Q'):
                Pressed = None
                skip_var = True
                break
            if Pressed == ord('r') or Pressed == ord('R'):
                Pressed = None
                imgdsc, img = cv2.transpose(imgdsc), cv2.transpose(img)
                imgdsc, img = cv2.flip(imgdsc, 1), cv2.flip(img, 1)
                t, l, b, r = 0, 0, imgdsc.shape[0] - 1, imgdsc.shape[1] - 1
            if Pressed == ord('p') or Pressed == ord('P'):
                break_var = True
                break
            if t < b and l < r:
                if Pressed == ord('c') or Pressed == ord('C'):
                    Pressed = None
                    break
    if break_var is True:
        break
    elif skip_var is True:
        Photo_num += 1
        skip_var = False
    else:
        l1, r1, t1, b1 = int(l*1/ratio), int(r*1/ratio), int(t*1/ratio), int(b*1/ratio)
        trimmed = downscale(img[t1:b1, l1:r1])
        print('Trimmed image shape is', trimmed.shape, '; view scale ratio ' + str(ratio))

        error_counter, order, table_row = 0, 0, [photos[Photo_num], Width, Height, t1, l1, b1, r1]
        cv2.namedWindow(photos[Photo_num])
        cv2.setMouseCallback(photos[Photo_num], lm_points)
        while True:
            measured = copy.copy(trimmed)
            sign = {9: str(SCALE) + ' mm SCALE', 13: 'A', 17: 'B', 21: 'V', 25: 'G', 29: 'D', 33: 'E'}
            color = [(255, 127, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0)]
            color_dict = {7: 0, 9: 0, 11: 1, 13: 1, 15: 1, 17: 1,
                          19: 2, 21: 2, 23: 2, 25: 2, 27: 3, 29: 3, 31: 3, 33: 3}
            for a in range(7, len(table_row)-1, 2):
                cv2.circle(measured, (int(table_row[a+1]), int(table_row[a])), 2, color[color_dict[a]], 1)
            for a in range(9, len(table_row)-1, 4):
                cv2.putText(measured, sign[a]+error_counter * '*', (int(table_row[a+1]), int(table_row[a])),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 100, 240), 1)
            for b in table:  # Does latency remain?
                if table_row[:11] == b[:11]:
                    for a in range(7, 34, 2):
                        cv2.circle(measured, (int(b[a + 1]), int(b[a])), 2, color[color_dict[a]], 1)
                    for a in range(9, 34, 4):
                        cv2.putText(measured, sign[a] + error_counter * '*', (int(b[a + 1]), int(b[a])),
                                    cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 100, 240), 1)
            cv2.imshow(photos[Photo_num], measured)
            Pressed = cv2.waitKey(Latency)
            if Pressed in measureActionKeys:
                if Pressed == ord('q') or Pressed == ord('Q'):
                    Photo_num += 1
                    Pressed = None
                    break
                elif Pressed == ord('t') or Pressed == ord('T'):
                    Pressed = None
                    break
                elif Pressed == ord('v') or Pressed == ord('V'):
                    if order > 2:
                        table = [a for a in table if table_row[7:11] != a[7:11]]
                        table_row, order = table_row[:7], 0
                        write_down(table, directory)
                        print('Scale and the associated beetles\' measures are reset')
                    elif order <= 2:
                        order, table_row = 0, table_row[:7]
                        error_counter += 1
                        print('Scale is reset')
                    elif order == 0:
                        print('No scale is set yet')
                    Pressed = None
                elif Pressed == ord('s') or Pressed == ord('S'):
                    if order < 14:
                        print('Measuring is unfinished')
                    else:
                        sex = input('beetle\'s sex:')
                        table_row.append(sex + '\n')
                        table.append(table_row)
                        write_down(table, directory)  # safe and ugly
                        order = 2
                        table_row = table_row[:11]
                        print('Proceed to the next beetle')
                        Pressed = None
                elif 2 <= order <= 12 and order % 2 == 0 and Pressed == ord('z') or Pressed == ord('Z'):
                    table_row.extend([0, 0, 0, 0])
                    order += 2
                    print('LM_#' + str(order-1) + ' 0 0\n', 'LM_#' + str(order) + ' 0 0')
                    Pressed = None
                elif Pressed == ord('p') or Pressed == ord('P'):
                    break_var = True
                    break
    cv2.destroyAllWindows()
quit()
