const { getDB } = require('../config/mongodb');
const { getDocumentById } = require('../services/fileService');
const path = require('path');
const fs = require('fs');

// Controller lấy chi tiết file
const getFileDetail = async (req, res) => {
  try {
    const { fileId } = req.params;
    const userId = req.user.userId; // Get current user
    
    // Lấy thông tin từ MongoDB - chỉ file của user hiện tại
    const db = getDB();
    const collection = db.collection('files');
    const fileMetadata = await collection.findOne({ 
      id: fileId,
      userId: userId // Ensure user can only access their own files
    });
    
    if (!fileMetadata) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy file'
      });
    }
    
    // Lấy thông tin đã index từ Meilisearch
    let searchData = null;
    try {
      searchData = await getDocumentById(fileId);
    } catch (error) {
      console.log('File chưa được index trong Meilisearch');
    }
    
    const fileDetail = {
      ...fileMetadata,
      searchData: searchData,
      downloadUrl: `/api/download/${fileId}`,
      previewUrl: `/uploads/${fileMetadata.filename}`
    };
    
    res.json({
      success: true,
      file: fileDetail
    });
    
  } catch (error) {
    console.error('Lỗi lấy chi tiết file:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi lấy chi tiết file'
    });
  }
};

// Controller download file
const downloadFile = async (req, res) => {
  try {
    const { fileId } = req.params;
    const userId = req.user.userId; // Get current user
    
    // Lấy thông tin file từ MongoDB - chỉ file của user hiện tại
    const db = getDB();
    const collection = db.collection('files');
    const fileMetadata = await collection.findOne({ 
      id: fileId,
      userId: userId // Ensure user can only download their own files
    });
    
    if (!fileMetadata) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy file'
      });
    }
    
    const filePath = path.resolve(fileMetadata.path);
    
    // Kiểm tra file có tồn tại không
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({
        success: false,
        message: 'File không tồn tại trên server'
      });
    }
    
    // Set headers cho download
    res.setHeader('Content-Disposition', `attachment; filename="${fileMetadata.originalName}"`);
    res.setHeader('Content-Type', fileMetadata.mimetype);
    res.setHeader('Content-Length', fileMetadata.size);
    
    // Stream file về client
    const fileStream = fs.createReadStream(filePath);
    fileStream.pipe(res);
    
    // Log download
    console.log(`File downloaded: ${fileMetadata.originalName} by ${req.ip}`);
    
  } catch (error) {
    console.error('Lỗi download file:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi download file'
    });
  }
};

// Controller xóa file
const deleteFile = async (req, res) => {
  try {
    const { fileId } = req.params;
    const userId = req.user.userId; // Get current user
    
    // Lấy thông tin file từ MongoDB - chỉ file của user hiện tại
    const db = getDB();
    const collection = db.collection('files');
    const fileMetadata = await collection.findOne({ 
      id: fileId,
      userId: userId // Ensure user can only delete their own files
    });
    
    if (!fileMetadata) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy file hoặc bạn không có quyền xóa file này'
      });
    }
    
    // Xóa file vật lý
    const filePath = path.resolve(fileMetadata.path);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    
    // Xóa từ MongoDB
    await collection.deleteOne({ 
      id: fileId,
      userId: userId // Double check user ownership
    });
    
    // Xóa từ Meilisearch
    try {
      const { meilisearchClient } = require('../config/meilisearch');
      const index = meilisearchClient.index('documents');
      await index.deleteDocument(fileId);
    } catch (error) {
      console.log('Lỗi xóa từ Meilisearch:', error);
    }
    
    res.json({
      success: true,
      message: 'File đã được xóa thành công'
    });
    
  } catch (error) {
    console.error('Lỗi xóa file:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi xóa file'
    });
  }
};

// Controller lấy danh sách tất cả file
const listFiles = async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      sortBy = 'uploadTime', 
      sortOrder = 'desc',
      fileType = '',
      indexed = ''
    } = req.query;
    
    // Get current user from authentication middleware
    const userId = req.user.userId;
    
    const db = getDB();
    const collection = db.collection('files');
    
    // Xây dựng query filter - chỉ lấy files của user hiện tại
    const filter = {
      userId: userId // Filter by current user only
    };
    
    if (fileType) {
      filter.mimetype = { $regex: fileType, $options: 'i' };
    }
    if (indexed !== '') {
      filter.indexed = indexed === 'true';
    }
    
    // Xây dựng sort object
    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    // Lấy danh sách file
    const files = await collection
      .find(filter)
      .sort(sort)
      .skip(skip)
      .limit(parseInt(limit))
      .toArray();
    
    // Đếm tổng số file
    const totalFiles = await collection.countDocuments(filter);
    
    res.json({
      success: true,
      data: {
        files: files.map(file => ({
          ...file,
          downloadUrl: `/api/download/${file.id}`,
          previewUrl: `/uploads/${file.filename}`,
          fileSize: formatFileSize(file.size)
        })),
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: totalFiles,
          totalPages: Math.ceil(totalFiles / parseInt(limit))
        }
      }
    });
    
  } catch (error) {
    console.error('Lỗi lấy danh sách file:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi lấy danh sách file'
    });
  }
};

// Utility function để format kích thước file
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

module.exports = {
  getFileDetail,
  downloadFile,
  deleteFile,
  listFiles
};
