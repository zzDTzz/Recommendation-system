import csv
import json
import math
import uvicorn
from fastapi import FastAPI, status, HTTPException
from typing import Optional
from distance_feature_extractor import screen_parser, similarity_calculator


def component_extractor(data):
    return screen_parser(data)


def load_similar_components(component_list):
    return similarity_calculator(component_list)


def get_top_k_similar(similar_list, k):
    top_k_similar = []

    # Sắp xếp danh sách similar tăng dần.
    temp = []
    for i in range(0, len(similar_list)):
        for j in range(0, len(similar_list)):
            if similar_list[i]['similarity'] < similar_list[j]['similarity']:
                temp = similar_list[i]
                similar_list[i] = similar_list[j]
                similar_list[j] = temp

    # Lấy top k similar từ danh sách similar.
    for i in range(0, k):
        top_k_similar.append(similar_list[i])

    return top_k_similar


#############################################
# Từ màn hình của người dùng đang thiết kế:
# - Trích ra các component
# - Lấy những loại component tương tự với loại đang có từ cơ sở dữ liệu
# - Lọc lại top k thằng có độ tương tự nhất
# - Chuyển đổi thành json và trả về cho người dùng
#############################################


def recommend_component():
    file = open('C:/Users/Tan/Desktop/Recommendation System/vdquan/data.json')
    data = json.load(file)
    component_list = component_extractor(data)
    similar_list = load_similar_components(component_list)
    top_k_list_similar = get_top_k_similar(similar_list, 5)

    # print('Total of recommended components is ' + str(len(top_k_list)))
    # print(top_k_list_similar)

    # convert to Json
    # top_k_list_json = ....

    # return top_k_list_json

    return top_k_list_similar


# Đưa dữ liệu lên server
app = FastAPI()


@app.get("/")
def Home():
    try:
        return {"Messege": "successful connection!"}
    except:
        raise HTTPException(status_code=404, detail="User Not Found")


@app.get("/user/{id}/component")
def get_recommended_components(id: int, page: str, per_page: str, query: Optional[str] = None):
    try:
        top_k_list_similar = recommend_component()
        count_total = len(top_k_list_similar)
        return {"data": top_k_list_similar, "total": count_total, "page": page, "per_page": per_page}
    except:
        raise HTTPException(status_code=404, detail="User Not Found")


if __name__ == '__main__':
    # current_screen_json = ....
    # recommend(current_screen_json)
    uvicorn.run('recommender:app', host='0.0.0.0', port=80)