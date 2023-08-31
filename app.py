from flask import Flask, render_template, request, url_for
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
model = pickle.load(open("Model_placement_full_data_class.pkl","rb"))
output =None

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        df = pd.DataFrame(columns=["gender","ssc_p","ssc_b","hsc_p","hsc_b","hsc_s","degree_p","degree_t","workex","etest_p","specialisation","mba_p","total_academic_performance"])
        df["gender"] = [request.form.get('gender')]
        df["ssc_p"]  = [float(request.form.get('secondaryEducation'))]
        df["ssc_b"]  = [request.form.get('boardSecondary')]
        df["hsc_p"]  = [float(request.form.get('higherSecondaryEducation'))]
        df["hsc_b"]  = [request.form.get('boardHigherSecondary')]
        df["hsc_s"]  = [request.form.get('specialization')]
        df["degree_p"]  = [float(request.form.get('degreePercentage'))]
        df["degree_t"]  = [request.form.get('undergraduate')]
        df["workex"] = [request.form.get('workexperience')]
        df["etest_p"]  = [float(request.form.get('employtest'))]
        df["specialisation"]  = [request.form.get('pgmba')]
        df["mba_p"]  = [float(request.form.get('mbapercentage'))]
        df["total_academic_performance"] = df["ssc_p"] + df["hsc_p"] + df["degree_p"]
        #Transform the string categories into numerical using label encoder
        le = LabelEncoder()
        categories = ['gender','ssc_b','hsc_b','degree_t','workex','specialisation','hsc_s']
        for i in categories:
            df[i] = le.fit_transform(df[i])

        X = list(df.iloc[0])
        # Predicted Output
        import requests

        # NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
        API_KEY = "tFBuuLr97Th30-at10K9ydYQHm67WjsWxOKGKw8RZhDS"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
        API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        # NOTE: manually define and pass the array(s) of values to be scored in the next line
        payload_scoring = {"input_data": [{"fields": ["gender","ssc_p","ssc_b","hsc_p","hsc_b","hsc_s","degree_p","degree_t","workex","etest_p","specialisation","mba_p","total_academic_performance"],
                                            "values": [X]}]}

        response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/ml/v4/deployments/2d12b253-b110-412e-a3e4-82ba17316272/predictions?version=2021-05-01', json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        # output with API response
        res = response_scoring.json()
        print("Scoring response")
        print(res)
        output = res["predictions"][0]['values'][0][0]

        if output == 1:
            return render_template("index.html", output="You are PLACED!!", flag=True, res=res)
        return render_template("index.html", output="NOT PLACED", flag=True, res=res)
    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)