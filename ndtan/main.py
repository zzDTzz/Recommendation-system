import csv
import random
import uvicorn
from fastapi import FastAPI, Request, Response, status, HTTPException
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient


# Initialize MongoDB
mongodb_uri = 'mongodb+srv://Dauthan:Dauthan2911@cluster0.p0hgt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
port = 80
client = MongoClient(mongodb_uri, port)
db = client['Recommendation_Template']
collection = db['User_Click_Template']
collection = db['User_Search_Template']


def readfile(path):
    template_value_of_user = []
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            template_value_of_user.append(row[0:])
    return template_value_of_user


def save_data(path, collection_name):
    json_data = {"data": []}
    csv_data = readfile(path)

    # Parser
    for row in range(1, len(csv_data)):
        temp = {}
        temp.update({"_id": int(csv_data[row][0])})
        for col in range(0, len(csv_data[0])):
            temp.update({csv_data[0][col]: int(csv_data[row][col])})
        json_data["data"].append(temp)

    # Save database
    for i in range(len(json_data["data"])):
        db[collection_name].insert_one(json_data["data"][i])



def calculate_rate():
    value = {}

    template_click_value_of_user = readfile("user_click.csv")
    template_search_value_of_user = readfile("user_search.csv")

    for i in range(1, len(template_click_value_of_user[0])):
        sum = 0
        for j in range(1, len(template_click_value_of_user)):
            sum += int(template_click_value_of_user[j][i]) + \
                int(template_search_value_of_user[j][i])
        value.update({template_click_value_of_user[0][i]: sum})
        rank = sorted(value.items(), key=lambda x: x[1], reverse=True)
    return rank


def select_top_rank(K):
    top_rank = {}
    rank = calculate_rate()
    for i in range(0, K):
        top_rank.update({rank[i][0]: rank[i][1]})
    return top_rank


def select_random_low_rank(L, K):
    low_rank = {}

    rank = calculate_rate()
    for i in range(0, K):
        rank.pop(0)
    random_rank = (random.sample(rank, k=L))
    random_rank.sort(key=lambda x: x[1], reverse=True)
    for i in range(0, L):
        low_rank.update({random_rank[i][0]: random_rank[i][1]})
    return low_rank


def recommened_template():
    rank_1 = select_top_rank(K=5)
    rank_2 = select_random_low_rank(L=4, K=5)
    rank_1.update(rank_2)
    return rank_1


# Initialize FastAPI
app = FastAPI()


@app.get("/")
def Home():
    return {"Messege": "successful connection!"}

@app.get("/user/{id}/template")
def get_recommended_templates(id: int, page: str, per_page: str, query: Optional[str] = None):
    try:
        data_rank = []
        rank = recommened_template()
        count_total = 0
        for item in rank.items():
            rate = {}
            rate.update({"template_id": item[0]})
            rate.update({"rate": item[1]})
            data_rank.append(rate)
            count_total += 1
        return {"data": data_rank, "total": count_total, "page": page, "per_page": per_page}
    except:
        raise HTTPException(status_code=404, detail="User Not Found")
        

if __name__ == "__main__":
    # save_data("user_click.csv", "User_Click_Template")
    # save_data("user_search.csv", "User_Search_Template")
    uvicorn.run("main:app", host= "0.0.0.0", port= 80)