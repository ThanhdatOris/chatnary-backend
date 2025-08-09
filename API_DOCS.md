# Chatnary Backend API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Hiện tại chưa có authentication. Sẽ được thêm trong phiên bản sau.

---

## Endpoints

### 1. Health Check
**GET** `/health`
```json
{
  "status": "ok",
  "timestamp": "2024-08-09T10:30:00.000Z",
  "uptime": 3600
}
```

### 2. Upload File
**POST** `/api/upload`

**Content-Type:** `multipart/form-data`

**Body:**
- `file`: File to upload (PDF, DOCX, DOC, TXT, MD)

**Response:**
```json
{
  "success": true,
  "message": "File đã được upload thành công",
  "file": {
    "id": "file-1691578200000-123456789",
    "originalName": "document.pdf",
    "filename": "file-1691578200000-123456789.pdf",
    "size": 1024000,
    "mimetype": "application/pdf",
    "uploadTime": "2024-08-09T10:30:00.000Z",
    "indexed": false
  }
}
```

### 3. Search Files
**GET** `/api/search`

**Query Parameters:**
- `query` (string): Search query
- `limit` (number): Results per page (default: 20)
- `offset` (number): Offset for pagination (default: 0)
- `fileType` (string): Filter by file extension
- `dateFrom` (string): Filter from date (ISO string)
- `dateTo` (string): Filter to date (ISO string)
- `sortBy` (string): Sort field (default: uploadTime)
- `sortOrder` (string): asc|desc (default: desc)

**Example:**
```
GET /api/search?query=nodejs&limit=10&fileType=.pdf&sortBy=uploadTime&sortOrder=desc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hits": [
      {
        "id": "file-123",
        "title": "Node.js Guide",
        "content": "This is a comprehensive guide to Node.js...",
        "originalName": "nodejs-guide.pdf",
        "fileType": ".pdf",
        "size": 1024000,
        "uploadTime": "2024-08-09T10:30:00.000Z",
        "_formatted": {
          "title": "<em>Node.js</em> Guide",
          "content": "This is a comprehensive guide to <em>Node.js</em>..."
        },
        "metadata": {
          "downloadUrl": "/api/download/file-123",
          "fileSize": "1.02 MB"
        }
      }
    ],
    "query": "nodejs",
    "processingTimeMs": 15,
    "hitsCount": 1,
    "offset": 0,
    "limit": 10
  }
}
```

### 4. Get Search Suggestions
**GET** `/api/suggestions`

**Query Parameters:**
- `q` (string): Query string for suggestions

**Example:**
```
GET /api/suggestions?q=node
```

**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "text": "nodejs-guide.pdf",
      "type": "file"
    },
    {
      "text": "node-modules-explained.docx",
      "type": "file"
    }
  ]
}
```

### 5. Get File Statistics
**GET** `/api/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "totalFiles": 25,
    "indexedFiles": 23,
    "recentFiles": 5,
    "fileTypes": [
      {
        "extension": "pdf",
        "count": 12,
        "totalSize": "15.6 MB"
      },
      {
        "extension": "docx",
        "count": 8,
        "totalSize": "8.2 MB"
      },
      {
        "extension": "txt",
        "count": 5,
        "totalSize": "0.5 MB"
      }
    ]
  }
}
```

### 6. List All Files
**GET** `/api/files`

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Results per page (default: 20)
- `sortBy` (string): Sort field (default: uploadTime)
- `sortOrder` (string): asc|desc (default: desc)
- `fileType` (string): Filter by MIME type
- `indexed` (boolean): Filter by indexed status

**Example:**
```
GET /api/files?page=1&limit=10&sortBy=uploadTime&sortOrder=desc&indexed=true
```

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "file-123",
        "originalName": "document.pdf",
        "filename": "file-1691578200000-123456789.pdf",
        "size": 1024000,
        "mimetype": "application/pdf",
        "uploadTime": "2024-08-09T10:30:00.000Z",
        "indexed": true,
        "downloadUrl": "/api/download/file-123",
        "previewUrl": "/uploads/file-1691578200000-123456789.pdf",
        "fileSize": "1.02 MB"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

### 7. Get File Detail
**GET** `/api/files/:fileId`

**Response:**
```json
{
  "success": true,
  "file": {
    "id": "file-123",
    "originalName": "document.pdf",
    "filename": "file-1691578200000-123456789.pdf",
    "size": 1024000,
    "mimetype": "application/pdf",
    "uploadTime": "2024-08-09T10:30:00.000Z",
    "indexed": true,
    "searchData": {
      "title": "Document Title",
      "content": "Full document content...",
      "fileType": ".pdf"
    },
    "downloadUrl": "/api/download/file-123",
    "previewUrl": "/uploads/file-1691578200000-123456789.pdf"
  }
}
```

### 8. Download File
**GET** `/api/download/:fileId`

Returns the file as attachment with appropriate headers.

### 9. Delete File
**DELETE** `/api/files/:fileId`

**Response:**
```json
{
  "success": true,
  "message": "File đã được xóa thành công"
}
```

---

## Error Responses

All error responses follow this format:
```json
{
  "success": false,
  "message": "Error description",
  "error": "Optional error details"
}
```

### Common Error Codes:
- `400` - Bad Request (invalid input, file too large, etc.)
- `404` - Not Found (file not found, route not found)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error

---

## File Upload Limitations:
- Maximum file size: 10MB
- Supported formats: PDF, DOCX, DOC, TXT, MD
- Files are stored locally in `/uploads` directory
- Metadata stored in MongoDB
- Content indexed in Meilisearch for search

---

## Coming Soon:
- `/api/chat` - Chat with documents
- Authentication & authorization
- File content extraction for PDF/DOCX
- Advanced search filters
- File tagging system
