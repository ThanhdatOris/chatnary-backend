const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function uploadTestDocument() {
  console.log('📤 Uploading test document...');
  
  try {
    const formData = new FormData();
    formData.append('file', fs.createReadStream('test-document.txt'));
    
    const response = await axios.post('http://localhost:5000/api/upload', formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });
    
    console.log('✅ Upload successful:', response.data);
    
    // Wait for indexing
    console.log('⏳ Waiting for indexing...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Test search
    console.log('🔍 Testing search...');
    const searchResponse = await axios.get('http://localhost:5000/api/search?query=Node.js');
    console.log('✅ Search result:', JSON.stringify(searchResponse.data, null, 2));
    
  } catch (error) {
    console.log('❌ Error:', error.response?.data || error.message);
  }
}

uploadTestDocument();
