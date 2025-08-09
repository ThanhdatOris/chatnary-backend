const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { saveFileMetadata, indexFileContent } = require('../services/fileService');

// Cấu hình multer để upload file
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Tạo tên file unique với timestamp
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// Kiểm tra loại file được phép upload
const fileFilter = (req, file, cb) => {
  const allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.md'];
  const fileExt = path.extname(file.originalname).toLowerCase();
  
  if (allowedTypes.includes(fileExt)) {
    cb(null, true);
  } else {
    cb(new Error('Chỉ cho phép upload file PDF, DOCX, DOC, TXT, MD'), false);
  }
};

const upload = multer({ 
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024 // Giới hạn 10MB
  }
});

// Controller xử lý upload file
const uploadFile = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ 
        success: false, 
        message: 'Không có file nào được upload' 
      });
    }

    const fileMetadata = {
      originalName: req.file.originalname,
      filename: req.file.filename,
      size: req.file.size,
      mimetype: req.file.mimetype,
      path: req.file.path,
      uploadTime: new Date().toISOString(),
      userId: req.user.userId, // Thêm userId từ authentication
      userEmail: req.user.email
    };

    // Lưu metadata vào MongoDB
    const savedMetadata = await saveFileMetadata(fileMetadata);
    
    // Index nội dung file vào Meilisearch (background task)
    indexFileContent(savedMetadata).catch(error => {
      console.error('Lỗi index file:', error);
    });
    
    res.json({
      success: true,
      message: 'File đã được upload thành công',
      file: savedMetadata
    });

  } catch (error) {
    console.error('Lỗi upload file:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi server khi upload file' 
    });
  }
};

module.exports = {
  upload,
  uploadFile
};
