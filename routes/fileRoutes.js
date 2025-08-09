const express = require('express');
const router = express.Router();
const { upload, uploadFile } = require('../controllers/fileController');
const { searchController, getSuggestions, getFileStats } = require('../controllers/searchController');
const { getFileDetail, downloadFile, deleteFile, listFiles } = require('../controllers/fileDetailController');
const { authenticateToken, optionalAuth } = require('../middleware/auth');

// Route upload file (cần authentication)
router.post('/upload', authenticateToken, upload.single('file'), uploadFile);

// Route tìm kiếm file (public, nhưng có thể có user context)
router.get('/search', optionalAuth, searchController);

// Route lấy gợi ý tìm kiếm (public)
router.get('/suggestions', getSuggestions);

// Route lấy thống kê file (public)
router.get('/stats', getFileStats);

// Route lấy danh sách tất cả file (cần authentication để filter theo user)
router.get('/files', authenticateToken, listFiles);

// Route lấy chi tiết file (cần authentication)
router.get('/files/:fileId', authenticateToken, getFileDetail);

// Route download file (cần authentication)
router.get('/download/:fileId', authenticateToken, downloadFile);

// Route xóa file (cần authentication)
router.delete('/files/:fileId', authenticateToken, deleteFile);

// Route chat với document (cần authentication - TODO)
router.post('/chat', authenticateToken, (req, res) => {
  res.json({ message: 'Chat API - Coming soon' });
});

module.exports = router;
