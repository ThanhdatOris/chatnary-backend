const express = require('express');
const router = express.Router();
const { register, login, getProfile, updateProfile } = require('../controllers/authController');
const { authenticateToken } = require('../middleware/auth');

// Public routes (không cần authentication)
router.post('/register', register);
router.post('/login', login);

// Protected routes (cần authentication)
router.get('/profile', authenticateToken, getProfile);
router.put('/profile', authenticateToken, updateProfile);

// Test route để verify token
router.get('/verify', authenticateToken, (req, res) => {
  res.json({
    success: true,
    message: 'Token hợp lệ',
    user: {
      userId: req.user.userId,
      email: req.user.email,
      role: req.user.role
    }
  });
});

module.exports = router;
