import json
import math
import csv
from itertools import groupby


# open json
# class Component(object):
#     def __init__(self, id, name, type, x_c, y_c):
#         self.id = id
#         self.name = name
#         self.type = type
#         self.x_c = x_c
#         self.y_c = y_c
#     def print_item(self):
#         print(self.id, self.name, self.type, self.x_c, self.y_c)

def add_item(data, output):
    for i in data:
        if ("height" not in i["data"] or "width" not in i["data"]):
            height = 0
            width = abs(i["data"]["to"]["x"] - i["data"]["from"]
                        ["x"]) if "to" in i["data"] else 0
        else:
            height = i["data"]["height"] if i["data"]["height"] else 0
            width = i["data"]["width"] if i["data"]["width"] else 0

        x_c = width / 2 + i["data"]["position"]["x"]
        y_c = height / 2 + i["data"]["position"]["y"]
        output.append({
            "id": i["id"],
            "name": i["data"]["name"],
            "type": i["type"],
            "x_c": x_c,
            "y_c": y_c
        })
        if("children" in i and len(i["children"]) > 0):
            add_item(i["children"], output)


###########################################
# Lấy các component và các thành phần cần thiết của mỗi component:
# - id của màn hình mà nó thuộc về
# - tên component
# - loại component
# - Tọa độ điểm trung tâm
# Kết quả trả về là một mảng với mỗi phần tử là thông tin của 1 component được đóng gói trong kiểu từ điển
# Ví dụ: [ {id: 1, name: "submit", type: "button", x_c: 12, y_c: 89}, {...}, ... ]
# ###########################################
def screen_parser(screen_json):
    # parse the screen to extract components
    components = []
    add_item(screen_json, components)
    return components


#########################################
# Tính toán khoảng cách giữa một cặp component trong 1 màn hình, lưu kết quả lên database
# Kết quả trả về là một mảng các phần tử với mỗi phần tử chứa thông tin:
# - id của màn hình mà nó thuộc về
# - tên component 1
# - loại component 1
# - tên component 2
# - loại component 2
# - khoảng cách
# Ví dụ: [ { id: 1, com1_name: "submit", com1_type: "button", com2_name: "username", com2_type: "textbox", distance: 150.25}, ...]
# Kết quả cần lưu lên DB trước khi trả vể
#########################################
def distance_calculator(screen_components):
    result = []
    # calculate distance
    for index, item in enumerate(screen_components):
        for next in screen_components[index+1:]:
            result.append({
                "id": 1,
                "com1_name": item['name'],
                "com1_type": item['type'],
                "com2_name": next['name'],
                "com2_type": next['type'],
                "distance": math.sqrt((item["x_c"] - next["x_c"]) ** 2 + (item["y_c"] - next["y_c"]) ** 2)
            })

    #print('Total of distance is ' + str(len(result)))
    title = ["id", "com1_name", "com1_type",
             "com2_name", "com2_type", "distance"]
    data_values = [list(i.values()) for i in result]
    # store to DB
    with open('distance.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(title)
        write.writerows(data_values)

    return result


##########################################
# Tính toán độ tương tự giữa một cặp "loại" component dựa trên khoảng cách
# Kết quả trả về là một mảng các độ tương tự giữa một cặp loại component:
# - loại của component 1
# - loại của component 2
# - độ tương tự
# Vi dụ: [ {com1_type: "button", com2_type: "textbox", similarity: 34.23}, ...]
# Cũng lưu kết quả lên DB trước khi trả về
##########################################
def key_func(k):
    return k["type"]


def similarity_calculator(data):
    result = []
    sorted_data = sorted(data, key=key_func)
    groupby_data = groupby(sorted_data, key_func)
    converted = [{"key": key, "value": list(value)}
                 for key, value in groupby_data]
    for index, item in enumerate(converted[:-1]):
        n = len(item["value"]) * len(converted[index+1]["value"])
        sum_distance = 0
        for current in item["value"]:
            for next in converted[index+1]["value"]:
                sum_distance += math.sqrt((current["x_c"] - next["x_c"])
                                          ** 2 + (current["y_c"] - next["y_c"]) ** 2)
        result.append({
            "com1_type": item["key"],
            "com2_type": converted[index+1]["key"],
            "similarity": sum_distance / n
        })
    # title = ["com1_type", "com2_type", "similarity"]
    # data_values = [list(i.values()) for i in result]
    # with open('similarity.csv', 'w') as f:
    #     write = csv.writer(f)
    #     write.writerow(title)
    #     write.writerows(data_values)
    return result


##########################################
# Đọc và xử lý lần lượt các màn hình
##########################################
def training():
    all_distances = []

    # for ....
    #        component_list = screen_parser(s1_json)
    #        distance_list = distance_calculator(component_list)
    #        all_distances.append(distance_list)

    components_similarity = similarity_calculator(all_distances)

    return 1