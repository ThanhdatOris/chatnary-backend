const express = require('express');
const router = express.Router();
const { upload, uploadFile } = require('../controllers/fileController');
const { searchController, getSuggestions, getFileStats } = require('../controllers/searchController');
const { getFileDetail, downloadFile, deleteFile, listFiles } = require('../controllers/fileDetailController');

// Route upload file
router.post('/upload', upload.single('file'), uploadFile);

// Route tìm kiếm file
router.get('/search', searchController);

// Route lấy gợi ý tìm kiếm
router.get('/suggestions', getSuggestions);

// Route lấy thống kê file
router.get('/stats', getFileStats);

// Route lấy danh sách tất cả file
router.get('/files', listFiles);

// Route lấy chi tiết file
router.get('/files/:fileId', getFileDetail);

// Route download file
router.get('/download/:fileId', downloadFile);

// Route xóa file
router.delete('/files/:fileId', deleteFile);

// Route chat với document (TODO)
router.post('/chat', (req, res) => {
  res.json({ message: 'Chat API - Coming soon' });
});

module.exports = router;
