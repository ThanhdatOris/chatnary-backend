require('dotenv').config();
const { connectMongoDB } = require('./config/mongodb');
const { meilisearchClient, initMeilisearch } = require('./config/meilisearch');

async function testConnections() {
  console.log('🔍 Kiểm tra cấu hình kết nối...\n');
  
  // Test environment variables
  console.log('📋 Environment Variables:');
  console.log('  MONGODB_URI:', process.env.MONGODB_URI ? '✅ Đã cấu hình' : '❌ Chưa cấu hình');
  console.log('  DB_NAME:', process.env.DB_NAME || 'chatnary');
  console.log('  MEILISEARCH_HOST:', process.env.MEILISEARCH_HOST || 'http://localhost:7700');
  console.log('  MEILISEARCH_API_KEY:', process.env.MEILISEARCH_API_KEY ? '✅ Đã cấu hình' : '❌ Chưa cấu hình');
  console.log('');

  // Test MongoDB connection
  console.log('🍃 Kiểm tra kết nối MongoDB...');
  try {
    const db = await connectMongoDB();
    if (db) {
      console.log('✅ MongoDB: Kết nối thành công');
      console.log(`   Database: ${db.databaseName}`);
    } else {
      console.log('❌ MongoDB: Không thể kết nối');
    }
  } catch (error) {
    console.log('❌ MongoDB: Lỗi kết nối -', error.message);
  }
  console.log('');

  // Test Meilisearch connection
  console.log('🔍 Kiểm tra kết nối Meilisearch...');
  try {
    const health = await meilisearchClient.health();
    console.log('✅ Meilisearch: Kết nối thành công');
    console.log('   Status:', health.status);
    
    const version = await meilisearchClient.getVersion();
    console.log('   Version:', version.pkgVersion);
    
    // Test index initialization
    console.log('');
    console.log('🔧 Kiểm tra khởi tạo Meilisearch index...');
    await initMeilisearch();
    
    const indexes = await meilisearchClient.getIndexes();
    console.log('📁 Indexes có sẵn:', indexes.results.map(idx => idx.uid));
    
  } catch (error) {
    console.log('❌ Meilisearch: Lỗi kết nối -', error.message);
    console.log('💡 Đảm bảo Meilisearch đang chạy trên port 7700');
  }
  console.log('');

  console.log('✅ Kiểm tra hoàn tất!');

  process.exit(0);
}

testConnections().catch(console.error);
