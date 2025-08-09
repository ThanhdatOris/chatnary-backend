const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5000';

// Test functions
async function testHealthCheck() {
  console.log('\n🔍 Testing Health Check...');
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Health check passed:', response.data);
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
  }
}

async function testApiInfo() {
  console.log('\n📖 Testing API Info...');
  try {
    const response = await axios.get(`${BASE_URL}/`);
    console.log('✅ API info:', response.data);
  } catch (error) {
    console.log('❌ API info failed:', error.message);
  }
}

async function testHelloEndpoint() {
  console.log('\n👋 Testing Hello Endpoint...');
  try {
    const response = await axios.get(`${BASE_URL}/api/hello`);
    console.log('✅ Hello endpoint:', response.data);
  } catch (error) {
    console.log('❌ Hello endpoint failed:', error.message);
  }
}

async function testFileStats() {
  console.log('\n📊 Testing File Stats...');
  try {
    const response = await axios.get(`${BASE_URL}/api/stats`);
    console.log('✅ File stats:', response.data);
  } catch (error) {
    console.log('❌ File stats failed:', error.message);
  }
}

async function testFileList() {
  console.log('\n📁 Testing File List...');
  try {
    const response = await axios.get(`${BASE_URL}/api/files`);
    console.log('✅ File list:', response.data);
  } catch (error) {
    console.log('❌ File list failed:', error.message);
  }
}

async function testSearch() {
  console.log('\n🔎 Testing Search...');
  try {
    const response = await axios.get(`${BASE_URL}/api/search?query=test`);
    console.log('✅ Search result:', response.data);
  } catch (error) {
    console.log('❌ Search failed:', error.message);
  }
}

async function testUpload() {
  console.log('\n📤 Testing File Upload...');
  
  // Tạo một file test đơn giản
  const testContent = 'This is a test file for Chatnary.\nIt contains some sample text for testing search functionality.';
  const testFilePath = path.join(__dirname, 'test-upload.txt');
  
  try {
    // Tạo file test
    fs.writeFileSync(testFilePath, testContent);
    
    // Tạo form data
    const formData = new FormData();
    formData.append('file', fs.createReadStream(testFilePath));
    
    const response = await axios.post(`${BASE_URL}/api/upload`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });
    
    console.log('✅ Upload successful:', response.data);
    
    // Cleanup
    fs.unlinkSync(testFilePath);
    
    return response.data.file;
    
  } catch (error) {
    console.log('❌ Upload failed:', error.response?.data || error.message);
    
    // Cleanup on error
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
  }
}

// Main test runner
async function runTests() {
  console.log('🧪 Starting Chatnary Backend API Tests...');
  console.log('=' .repeat(50));
  
  await testHealthCheck();
  await testApiInfo();
  await testHelloEndpoint();
  await testFileStats();
  await testFileList();
  await testSearch();
  
  // Test upload (this creates a real file)
  const uploadedFile = await testUpload();
  
  if (uploadedFile) {
    console.log('\n🎉 All basic tests completed!');
    console.log('\n💡 Next steps:');
    console.log('   1. Install and run Meilisearch for search functionality');
    console.log('   2. Setup MongoDB for persistent storage');
    console.log('   3. Test the uploaded file with search API');
  }
  
  console.log('\n' + '=' .repeat(50));
}

// Error handling
process.on('unhandledRejection', (error) => {
  console.error('❌ Unhandled error:', error.message);
});

// Run tests
runTests().catch(console.error);
