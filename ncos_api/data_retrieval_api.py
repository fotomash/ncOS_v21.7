import os

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="ZBAR Data Retrieval API", version="1.0")

@app.get("/data/retrieve")
def retrieve_data(symbol: str = Query(...), tf: str = Query(...), limit: int = Query(200)):
    base_path = f"/mnt/data/BAR_DATA/{symbol.upper()}/"
    tf = tf.upper()
    filename = f"{tf}.csv"
    file_path = os.path.join(base_path, filename)

    if not os.path.exists(file_path):
        return JSONResponse(content={"error": f"Data for {symbol} {tf} not found."}, status_code=404)

    try:
        df = pd.read_csv(file_path)
        df = df.tail(limit).reset_index(drop=True)
        return df.to_dict(orient="records")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
