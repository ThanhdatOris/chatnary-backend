const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

// Import configurations
const { connectMongoDB } = require('./config/mongodb');
const { initMeilisearch } = require('./config/meilisearch');

// Import middleware
const { errorHandler, notFound } = require('./middleware/errorHandler');
const { requestLogger, rateLimit } = require('./middleware/logger');

const app = express();

// Apply rate limiting
app.use(rateLimit());

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// Request logging
app.use(requestLogger);

// Serve static files từ thư mục uploads
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Routes
const fileRoutes = require('./routes/fileRoutes');
const authRoutes = require('./routes/authRoutes');
app.use('/api', fileRoutes);
app.use('/api/auth', authRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/', (req, res) => {
  res.json({
    message: 'Chatnary Backend API',
    version: '1.0.0',
    docs: '/api/docs',
    health: '/health'
  });
});

app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from backend!' });
});

// Handle 404
app.use(notFound);

// Error handling middleware
app.use(errorHandler);

// Khởi tạo server và databases
const startServer = async () => {
  try {
    console.log('🚀 Đang khởi động Chatnary Backend...');
    
    // Kết nối MongoDB (không bắt buộc)
    await connectMongoDB();
    
    // Khởi tạo Meilisearch (không bắt buộc)
    await initMeilisearch();
    
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
      console.log(`\n🚀 Server running on port ${PORT}`);
      console.log(`📖 API Documentation: http://localhost:${PORT}/`);
      console.log(`🔍 Health Check: http://localhost:${PORT}/health`);
      console.log(`📁 Upload endpoint: http://localhost:${PORT}/api/upload`);
      console.log(`🔎 Search endpoint: http://localhost:${PORT}/api/search`);
      console.log('\n✅ Backend đã sẵn sàng nhận requests');
      
      // Hiển thị hướng dẫn nếu thiếu dependencies
      if (!process.env.MONGODB_URI) {
        console.log('\n💡 Để sử dụng đầy đủ chức năng, hãy cấu hình:');
        console.log('   - MongoDB: Set MONGODB_URI trong .env');
        console.log('   - Meilisearch: Cài đặt và chạy Meilisearch server');
      }
    });
  } catch (error) {
    console.error('❌ Lỗi khởi động server:', error);
    console.log('💡 Server sẽ thử khởi động với chức năng cơ bản...');
    
    // Fallback: chạy server cơ bản
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
      console.log(`🚀 Server (basic mode) running on port ${PORT}`);
      console.log('⚠️  Một số chức năng có thể bị hạn chế do thiếu dependencies');
    });
  }
};

startServer();
