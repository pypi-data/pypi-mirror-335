# botrun_flow_lang

## 開發環境安裝
- 使用 Python 3.11.9
- 安裝 poetry 來管理 python 套件
  - 安裝 Poetry 可以參考: [Python 套件管理器——Poetry 完全入門指南](https://blog.kyomind.tw/python-poetry/#%E7%AE%A1%E7%90%86-Poetry-%E8%99%9B%E6%93%AC%E7%92%B0%E5%A2%83)
  - 在 /project_folder/ 下執行
  ```bash
  poetry install
  ```

## 開發建議
- 先安裝 LangGraph Studio
- 在 LangGraph Studio 中開啟 botrun_flow_lang 資料夾

# 以下是備份用，先保留
## 本地端執行測試
```bash
uvicorn botrun_flow_lang.main:app --reload --host 0.0.0.0 --port 8080
```

## 輸出可用的 requirements.txt
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes --without-urls
```

### 建立 dev 的 index
```bash
gcloud firestore indexes composite create \
  --collection-group=botrun-hatch-dev-hatch \
  --field-config=field-path=user_id,order=ascending \
  --field-config=field-path=name,order=ascending \
  --field-config=field-path=__name__,order=ascending \
  --project=scoop-386004
```

### 打包 dev
```bash
gcloud builds submit --config cloudbuild_fastapi_dev.yaml --project=scoop-386004
```
### deploy cloud run, dev 的版本
```bash
gcloud run deploy botrun-flow-lang-fastapi-dev \
  --image asia-east1-docker.pkg.dev/scoop-386004/botrun-flow-lang/botrun-flow-lang-fastapi-dev \
  --port 8080 \
  --platform managed \
  --allow-unauthenticated \
  --project=scoop-386004 \
  --region=asia-east1 \
  --cpu 2 \
  --memory 8Gi \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 3600s \
  --concurrency 300 \
  --cpu-boost \
```

### 建立 staging 的 index
```bash
gcloud firestore indexes composite create \
  --collection-group=botrun-hatch-hatch \
  --field-config=field-path=user_id,order=ascending \
  --field-config=field-path=name,order=ascending \
  --field-config=field-path=__name__,order=ascending \
  --project=scoop-386004
```

### 打包 Cloud Run, staging 的版本
```bash
gcloud builds submit --config cloudbuild_fastapi.yaml --project=scoop-386004
```

### 佈署 cloud run, staging 的版本
```bash
gcloud run deploy botrun-flow-lang-fastapi \
  --image asia-east1-docker.pkg.dev/scoop-386004/botrun-flow-lang/botrun-flow-lang-fastapi \
  --port 8080 \
  --platform managed \
  --allow-unauthenticated \
  --project=scoop-386004 \
  --region=asia-east1 \
  --cpu 2 \
  --memory 8Gi \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 3600s \
  --concurrency 300 \
  --cpu-boost \
```

## 為了要減少冷啟動的時間，每十分鐘呼叫一次 heartbeat
```bash
gcloud scheduler jobs create http botrun-flow-lang-heartbeat-job-$ENV \
  --schedule "*/10 * * * *" \
  --time-zone "Asia/Taipei" \
  --uri "https://botrun-flow-lang-fastapi-$ENV-36186877499.asia-east1.run.app/heartbeat" \
  --http-method GET \
  --location "asia-east1" \
  --project "scoop-386004"
```
測試 scheduler
```bash
gcloud scheduler jobs run botrun-flow-lang-heartbeat-job-$ENV --location "asia-east1" --project "scoop-386004"
```
