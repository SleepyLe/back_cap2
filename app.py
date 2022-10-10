from flask import *
import pandas as pd
import config
from transformers import AutoTokenizer
import json
# from model import model_infer
import torch
from statistics import mean, stdev, variance

firebase = config.connection()
app = Flask(__name__)
app.secret_key = "Abcd1234"

# tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
# model = model_infer.SentimentClassifier()
# model.load_state_dict(torch.load(f'package\last_step.pth',map_location=torch.device('cpu')))
# model.eval()
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def save_df(df, id):
    postdata = df.to_dict()
    result = firebase.put("/input", id, postdata)
    return result


def create_new(df):
    df2 = pd.DataFrame()
    df2["Review"] = df["Review"]
    df2["country_id"] = df["country"]
    df2["giai_tri"] = df["giai_tri"]
    df2["luu_tru"] = df["luu_tru"]
    df2["nha_hang"] = df["nha_hang"]
    df2["an_uong"] = df["an_uong"]
    df2["di_chuyen"] = df["di_chuyen"]
    df2["mua_sam"] = df["mua_sam"]
    df2["status"] = False
    grouped = df2.groupby(df2.country_id)
    country_code = df2["country_id"].to_list()
    country_code = list(set(country_code))
    for i in country_code:
        df_new = grouped.get_group(int(i))
        save_df(df_new, i)
    # postdata = df2.to_dict()
    # result = firebase.post('/input', postdata, {'print': 'pretty'})
    return True


def query(page, typ_inp):
    val = firebase.get("/input/" + str(page), typ_inp)
    return val


def get_value_by_status(dic, status):
    temp = []
    for x, y in dic.items():
        if x not in status:
            temp.append(y)
    return temp


def save_cal(page, an_uong_cal, di_chuyen_cal, giai_tri, luu_tru, mua_sam, nha_hang):
    dict_save = {
        "mean":{
            "an_uong" : mean(an_uong_cal),
            "di_chuyen": mean(di_chuyen_cal),
            "giai_tri" : mean(giai_tri),
            "luu_tru" : mean(luu_tru),
            "mua_sam" : mean(mua_sam),
            "nha_hang" : mean(nha_hang)
        },
        "std":{
            "an_uong" : stdev(an_uong_cal),
            "di_chuyen": stdev(di_chuyen_cal),
            "giai_tri" : stdev(giai_tri),
            "luu_tru" : stdev(luu_tru),
            "mua_sam" : stdev(mua_sam),
            "nha_hang" : stdev(nha_hang)
        },
        "var":{
            "an_uong" : variance(an_uong_cal),
            "di_chuyen": variance(di_chuyen_cal),
            "giai_tri" : variance(giai_tri),
            "luu_tru" : variance(luu_tru),
            "mua_sam" : variance(mua_sam),
            "nha_hang" : variance(nha_hang)
        },
    }
    result = firebase.put("/cal", page, dict_save)

@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/confirm", methods=["POST"])
def upload():
    file = request.files["file"]
    if file:
        df = pd.read_csv(file)
        res = create_new(df)
        if res:
            return render_template("csv_table.html", tables=[df.to_html()], titles=[""])
    flash("fail")
    return render_template("index.html")


@app.route("/cal", methods=["GET"])
def cal():
    status = []
    an_uong = []
    di_chuyen = []
    giai_tri = []
    luu_tru = []
    mua_sam = []
    nha_hang = []
    # test = firebase.get('/input/1/Review',2)
    # print(test)
    for i in range(1, 5):
        boo_val = query(i, "status")
        for x, y in boo_val.items():
            if y == True:
                status.append(x)
        an_uong = get_value_by_status(query(i, "an_uong"), status)
        di_chuyen = get_value_by_status(query(i, "di_chuyen"), status)
        giai_tri = get_value_by_status(query(i, "giai_tri"), status)
        luu_tru = get_value_by_status(query(i, "luu_tru"), status)
        mua_sam = get_value_by_status(query(i, "mua_sam"), status)
        nha_hang = get_value_by_status(query(i, "nha_hang"), status)
        save_cal(i, an_uong, di_chuyen, giai_tri, luu_tru, mua_sam, nha_hang)
    return "hello"


if __name__ == "__main__":
    app.run(debug=True)
