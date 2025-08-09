const { MongoClient } = require('mongodb');

let db;

const connectMongoDB = async () => {
  try {
    // Nếu không có MONGODB_URI, sử dụng in-memory store tạm thời
    if (!process.env.MONGODB_URI) {
      console.log('⚠️  MongoDB URI không được cấu hình, sử dụng in-memory store');
      return null;
    }

    const { MongoClient } = require('mongodb');
    const client = new MongoClient(process.env.MONGODB_URI);
    await client.connect();
    
    db = client.db(process.env.DB_NAME || 'chatnary');
    console.log('✅ Kết nối MongoDB thành công');
    
    return db;
  } catch (error) {
    console.error('⚠️  Lỗi kết nối MongoDB:', error.message);
    console.log('💡 Tip: Hãy cài đặt MongoDB hoặc sử dụng MongoDB Atlas');
    console.log('💡 Server sẽ chạy mà không có database (chức năng bị hạn chế)');
    return null;
  }
};

const getDB = () => {
  if (!db) {
    throw new Error('Database chưa được khởi tạo');
  }
  return db;
};

module.exports = {
  connectMongoDB,
  getDB
};
