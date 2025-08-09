const jwt = require('jsonwebtoken');
const { getDB } = require('../config/mongodb');

// Middleware xác thực JWT token
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Token xác thực không được cung cấp'
      });
    }
    
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'chatnary-secret-key-2025');
    
    // Kiểm tra user có tồn tại và active không
    const db = getDB();
    if (!db) {
      return res.status(500).json({
        success: false,
        message: 'Database không khả dụng'
      });
    }
    
    const usersCollection = db.collection('users');
    const { ObjectId } = require('mongodb');
    const user = await usersCollection.findOne({ 
      _id: new ObjectId(decoded.userId),
      isActive: true
    });
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Token không hợp lệ hoặc user đã bị vô hiệu hóa'
      });
    }
    
    // Gắn thông tin user vào request
    req.user = {
      userId: new ObjectId(decoded.userId),
      email: decoded.email,
      role: decoded.role
    };
    
    next();
    
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token đã hết hạn'
      });
    }
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Token không hợp lệ'
      });
    }
    
    console.error('Lỗi xác thực token:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi xác thực'
    });
  }
};

// Middleware kiểm tra quyền admin
const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: 'Bạn không có quyền truy cập chức năng này'
    });
  }
  next();
};

// Middleware tùy chọn - không bắt buộc đăng nhập
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
      req.user = null;
      return next();
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'chatnary-secret-key-2025');
    
    const db = getDB();
    if (!db) {
      req.user = null;
      return next();
    }
    
    const usersCollection = db.collection('users');
    const { ObjectId } = require('mongodb');
    const user = await usersCollection.findOne({ 
      _id: new ObjectId(decoded.userId),
      isActive: true
    });
    
    if (user) {
      req.user = {
        userId: new ObjectId(decoded.userId),
        email: decoded.email,
        role: decoded.role
      };
    } else {
      req.user = null;
    }
    
    next();
    
  } catch (error) {
    // Nếu có lỗi, coi như không có user
    req.user = null;
    next();
  }
};

module.exports = {
  authenticateToken,
  requireAdmin,
  optionalAuth
};
