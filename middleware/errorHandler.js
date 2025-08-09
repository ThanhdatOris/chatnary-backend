const multer = require('multer');

// Middleware xử lý lỗi toàn cục
const errorHandler = (err, req, res, next) => {
  console.error('Error stack:', err.stack);
  
  // Lỗi Multer (upload file)
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        message: 'File quá lớn. Kích thước tối đa cho phép là 10MB'
      });
    }
    if (err.code === 'LIMIT_UNEXPECTED_FILE') {
      return res.status(400).json({
        success: false,
        message: 'Trường file không hợp lệ'
      });
    }
  }
  
  // Lỗi MongoDB
  if (err.name === 'MongoError' || err.name === 'MongoServerError') {
    return res.status(500).json({
      success: false,
      message: 'Lỗi cơ sở dữ liệu'
    });
  }
  
  // Lỗi Meilisearch
  if (err.message && err.message.includes('MeiliSearch')) {
    return res.status(500).json({
      success: false,
      message: 'Lỗi hệ thống tìm kiếm'
    });
  }
  
  // Lỗi validation
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      success: false,
      message: 'Dữ liệu đầu vào không hợp lệ',
      errors: err.errors
    });
  }
  
  // Lỗi 404
  if (err.status === 404) {
    return res.status(404).json({
      success: false,
      message: 'Không tìm thấy tài nguyên'
    });
  }
  
  // Lỗi mặc định
  const status = err.status || 500;
  const message = err.message || 'Lỗi server nội bộ';
  
  res.status(status).json({
    success: false,
    message: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

// Middleware xử lý route không tồn tại
const notFound = (req, res, next) => {
  const error = new Error(`Không tìm thấy route ${req.originalUrl}`);
  error.status = 404;
  next(error);
};

module.exports = {
  errorHandler,
  notFound
};
