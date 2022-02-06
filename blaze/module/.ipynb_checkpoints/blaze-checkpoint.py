"""blazeデータの加工モジュール"""
import os
import math

def arrange_file(input_path, output_path):
    """
    blazeのデータをの要らないところを切り取る
    Args:
        input_path : 読み込むファイルのパス
        output_path : 書き込む先のファイルパス
    """
    with open(input_path, 'r') as f:
        lines = f.readlines()

    start_index = lines.index('end_header\n')
    end_index = lines.index('0\n')

    os.makedirs(os.path.split(output_path)[0], exist_ok=True)
    with open(output_path, 'w') as f:
        for i in range(start_index+1, end_index):
            line = lines[i]
            f.write(line)

def read_blazedata(filepath):
    """
    blazeのテキストデータを読み込む
    Args:
        filepath (str) : 読み込むファイルのパス 
    Reterns:
        points (list) : [[x, y, z], ...]の点群データ
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    points = [line.split()[:3] for line in lines]
    
    return points

def write_data(output_path, _res):
    """
    処理したデータを書き込む
    Args:
        output_path (str) : 書き込む先のファイルパス
        _res (list) : [[x, y, z], ...]の点群データ
    """
    with open(output_path, 'w') as f:
        for i in range(len(_res)):
            f.write(str(_res[i][0]) + " "
                    + str(_res[i][1]) + " "
                    + str(_res[i][2]) + "\n"  )            

def set_origin(points, origin):
    """
    原点を設定する
    Args:
        points (list) : [[x, y, z], ...]の点群データ
        origin (list) : [x, y, z]の原点にしたい座標データ
    """
    x, y, z = origin
    for point in points:
        point[0] = float(point[0]) - x
        point[1] = float(point[1]) - y
        point[2] = float(point[2]) - z
        
def calculate_degree(origin, point, axis):
    """
    任意の二点を原点とある座標軸上の点にしたいときに必要とする回転角を算出する
    Args:
        origin (list) : [x, y, z]の原点にしたい座標データ
        point (list) : [x, y, z]の座標軸上の点にしたい座標データ
        axis (str) : pointを乗せる座標軸
    Reterns:
        deg (float) : 回転角
    """
    x_o, y_o, z_o = origin
    x_p, y_p, z_p = point
    if axis == 'x':
        r1 = y_o - y_p
        r2 = z_o - z_p
    elif axis == 'y':
        r1 = z_o - z_p
        r2 = x_o - x_p
    elif axis == 'z':
        r1 = x_o - x_p
        r2 = y_o - y_p
    r = abs(math.sqrt((r1)**2 + (r2)**2))
    cos = r1 / r
    deg = math.degrees(math.acos(cos))
    
    return deg

def rotate_with_x(points, deg, pn):
    """
    x軸に対して点群を回転させる
    Args:
        points (list) : [[x, y, z], ...]の点群データ
        deg (float) : 回転角
        pn (int) : 回転させる方向（-1 or 1）
    Reterns:
        _res (list) : [[x, y, z], ...]の点群データ
    """
    _res = []
    cos = math.cos(math.radians(deg))
    sin = math.sin(math.radians(deg))
    for point in points:
        x, y, z = point
        X = x
        Y = (y*cos) + (-z*sin*pn)
        Z = (y*sin*pn) + (z*cos)
        _res.append([X, Y, Z])
        
    return _res      

def rotate_with_z(points, deg, pn):
    """
    x軸に対して点群を回転させる
    Args:
        points (list) : [[x, y, z], ...]の点群データ
        deg (float) : 回転角
        pn (int) : 回転させる方向（-1 or 1）
    Reterns:
        _res (list) : [[x, y, z], ...]の点群データ
    """
    _res = []
    cos = math.cos(math.radians(deg))
    sin = math.sin(math.radians(deg))
    for point in points:
        x, y, z = point
        Z = z
        X = (x*cos) + (-y*sin*pn)
        Y = (x*sin*pn) + (y*cos)
        _res.append([X, Y, Z])
        
    return _res

def scaling(points, ratio):
    """
    縮尺を変更する
    Args:
        points (list) : [[x, y, z], ...]の点群データ
        ratio (float) : 縮尺率
    """
    for point in points:
        point[0] = point[0] * ratio
        point[1] = point[1] * ratio
        point[2] = point[2] * ratio
        
def thinning(points, _range, axis):
    """
    データを間引く
    Args:
        points (list) : [[x, y, z], ...]の点群データ
        _range (list) : [lower, upper]の点群データの必要な部分
        axis (str) : データを間引く基準の軸
    Reterns:
        _res (list) : [[x, y, z], ...]の点群データ
    """
    daxis = {"x": 0, "y":1, "z":2}
    _res = [point for point in points 
            if _range[0]<=point[daxis[axis]]<=_range[1]]
    
    return _res

def grid(points):
    """
    xy平面に格子を作り、格子の周りの点をひとまとめにする
    Args:
        points (list) : [[x, y, z], ...]の点群データ 
    """
    for point in points:
        point[0] = round(float(point[0]))
        point[1] = round(float(point[1]))
        point[2] = float(point[2])
        
def averaging(points):
    """
    一つの格子内で平均値をとって格子データ化する
    Args:
        points (list) : [[x, y, z], ...]の点群データ
    """
    unique_x = set([point[0] for point in points])
    sort_xs = [[point for point in points if point[0]==x] for x in unique_x]
    unique_y = set([point[1] for point in sort_xs[0]])
    sort_ys = [[[point for point in sort_x if point[1]==y] for y in unique_y] for sort_x in sort_xs]

    _average = []
    for x_len in range(len(unique_x)):
        for y_len in range(len(unique_y)):
            s = 0
            for i in range(len(sort_ys[x_len][y_len])):
                s += sort_ys[x_len][y_len][i][2]
               
            if s!=0:
                z_mean = s / len(sort_ys[x_len][y_len])
                _average.append([sort_ys[x_len][y_len][0][0],
                            sort_ys[x_len][y_len][0][1],
                            z_mean])
    
    return _average

