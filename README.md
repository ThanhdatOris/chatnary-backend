# Chatnary Backend

Backend API cho ứng dụng Chatnary - File management và search system.

## 🚀 Khởi động nhanh

### 1. Cài đặt dependencies
```bash
npm install
```

### 2. Cấu hình environment
Sao chép `.env.example` thành `.env` và cập nhật các giá trị:
```bash
cp .env.example .env
```

### 3. Khởi động Meilisearch
**Terminal 1:**
```bash
npm run meilisearch
```
Hoặc chạy file batch:
```bash
start-meilisearch.bat
```

### 4. Khởi động Backend API
**Terminal 2:**
```bash
npm start
```

### 5. Kiểm tra kết nối
```bash
npm test
```

## 📁 Cấu trúc thư mục

```
chatnary-backend/
├── config/              # Cấu hình database
├── controllers/         # API controllers
├── middleware/          # Express middleware
├── routes/             # API routes
├── services/           # Business logic
├── uploads/            # File uploads (tự động tạo)
├── meili_data/         # Meilisearch data (tự động tạo)
├── meilisearch.exe     # Meilisearch executable
├── server.js           # Entry point
└── .env               # Environment variables
```

## 🔧 Scripts có sẵn

- `npm start` - Khởi động server
- `npm run dev` - Khởi động development mode  
- `npm test` - Kiểm tra kết nối DB
- `npm run meilisearch` - Khởi động Meilisearch
- `npm run setup` - Cài đặt và test toàn bộ

## 🌐 API Endpoints

- `GET /` - API Documentation
- `GET /health` - Health check
- `POST /api/upload` - Upload files
- `GET /api/search` - Search files
- `GET /api/files` - List files

## 🔗 Dependencies

- **Express** - Web framework
- **MongoDB** - Database (Atlas)
- **Meilisearch** - Search engine
- **Multer** - File upload handling
- **CORS** - Cross-origin requests
