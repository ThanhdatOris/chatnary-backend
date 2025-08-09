const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { getDB } = require('../config/mongodb');

// Controller đăng ký user mới
const register = async (req, res) => {
  try {
    const { email, password, fullName } = req.body;
    
    // Validation
    if (!email || !password || !fullName) {
      return res.status(400).json({
        success: false,
        message: 'Email, password và tên đầy đủ là bắt buộc'
      });
    }
    
    if (password.length < 6) {
      return res.status(400).json({
        success: false,
        message: 'Mật khẩu phải có ít nhất 6 ký tự'
      });
    }
    
    const db = getDB();
    if (!db) {
      return res.status(500).json({
        success: false,
        message: 'Database không khả dụng'
      });
    }
    const usersCollection = db.collection('users');
    
    // Kiểm tra email đã tồn tại
    const existingUser = await usersCollection.findOne({ email: email.toLowerCase() });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'Email đã được sử dụng'
      });
    }
    
    // Hash password
    const saltRounds = 12;
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    
    // Tạo user mới
    const newUser = {
      email: email.toLowerCase(),
      password: hashedPassword,
      fullName: fullName.trim(),
      createdAt: new Date(),
      isActive: true,
      role: 'user' // Default role
    };
    
    const result = await usersCollection.insertOne(newUser);
    
    // Tạo JWT token
    const token = jwt.sign(
      { 
        userId: result.insertedId, 
        email: newUser.email,
        role: newUser.role
      },
      process.env.JWT_SECRET || 'chatnary-secret-key-2025',
      { expiresIn: '7d' }
    );
    
    // Trả response không bao gồm password
    const userResponse = {
      id: result.insertedId,
      email: newUser.email,
      fullName: newUser.fullName,
      role: newUser.role,
      createdAt: newUser.createdAt
    };
    
    res.status(201).json({
      success: true,
      message: 'Đăng ký thành công',
      user: userResponse,
      token: token
    });
    
  } catch (error) {
    console.error('Lỗi đăng ký:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi đăng ký'
    });
  }
};

// Controller đăng nhập
const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Validation
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Email và password là bắt buộc'
      });
    }
    
    const db = getDB();
    const usersCollection = db.collection('users');
    
    // Tìm user theo email
    const user = await usersCollection.findOne({ email: email.toLowerCase() });
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Email hoặc mật khẩu không đúng'
      });
    }
    
    // Kiểm tra account có active không
    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Tài khoản đã bị vô hiệu hóa'
      });
    }
    
    // Kiểm tra password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Email hoặc mật khẩu không đúng'
      });
    }
    
    // Tạo JWT token
    const token = jwt.sign(
      { 
        userId: user._id, 
        email: user.email,
        role: user.role
      },
      process.env.JWT_SECRET || 'chatnary-secret-key-2025',
      { expiresIn: '7d' }
    );
    
    // Update last login
    await usersCollection.updateOne(
      { _id: user._id },
      { $set: { lastLogin: new Date() } }
    );
    
    // Trả response không bao gồm password
    const userResponse = {
      id: user._id,
      email: user.email,
      fullName: user.fullName,
      role: user.role,
      lastLogin: new Date()
    };
    
    res.json({
      success: true,
      message: 'Đăng nhập thành công',
      user: userResponse,
      token: token
    });
    
  } catch (error) {
    console.error('Lỗi đăng nhập:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi đăng nhập'
    });
  }
};

// Controller lấy thông tin profile user
const getProfile = async (req, res) => {
  try {
    const userId = req.user.userId;
    
    const db = getDB();
    const usersCollection = db.collection('users');
    
    const user = await usersCollection.findOne(
      { _id: userId },
      { projection: { password: 0 } } // Không trả password
    );
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy user'
      });
    }
    
    res.json({
      success: true,
      user: user
    });
    
  } catch (error) {
    console.error('Lỗi lấy profile:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi lấy thông tin profile'
    });
  }
};

// Controller cập nhật profile
const updateProfile = async (req, res) => {
  try {
    const userId = req.user.userId;
    const { fullName } = req.body;
    
    if (!fullName || fullName.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Tên đầy đủ không được để trống'
      });
    }
    
    const db = getDB();
    const usersCollection = db.collection('users');
    
    const result = await usersCollection.updateOne(
      { _id: userId },
      { 
        $set: { 
          fullName: fullName.trim(),
          updatedAt: new Date()
        }
      }
    );
    
    if (result.matchedCount === 0) {
      return res.status(404).json({
        success: false,
        message: 'Không tìm thấy user'
      });
    }
    
    res.json({
      success: true,
      message: 'Cập nhật profile thành công'
    });
    
  } catch (error) {
    console.error('Lỗi cập nhật profile:', error);
    res.status(500).json({
      success: false,
      message: 'Lỗi server khi cập nhật profile'
    });
  }
};

module.exports = {
  register,
  login,
  getProfile,
  updateProfile
};
