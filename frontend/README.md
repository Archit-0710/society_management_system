# Society Maintenance Tracker Frontend

Start the FastAPI backend on port `8000`, then run:

```powershell
npm install
npm run dev
```

The Vite development server proxies `/api` and `/uploads` to the backend, so local development works without changing backend CORS. For production, set `VITE_API_BASE_URL` to the deployed API URL and configure the backend to allow the frontend origin.
