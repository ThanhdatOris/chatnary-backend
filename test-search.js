const axios = require('axios');

async function testSearchAfterUpload() {
  console.log('🔍 Testing search functionality...');
  
  try {
    // Wait 2 seconds for indexing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test search for "Node.js"
    const response = await axios.get('http://localhost:5000/api/search?query=Node.js');
    console.log('✅ Search results for "Node.js":');
    console.log(JSON.stringify(response.data, null, 2));
    
    // Test search for "Express"
    const response2 = await axios.get('http://localhost:5000/api/search?query=Express');
    console.log('\n✅ Search results for "Express":');
    console.log(JSON.stringify(response2.data, null, 2));
    
    // Test empty search (get all files)
    const response3 = await axios.get('http://localhost:5000/api/search?query=');
    console.log('\n✅ All indexed files:');
    console.log(JSON.stringify(response3.data, null, 2));
    
  } catch (error) {
    console.log('❌ Search test failed:', error.response?.data || error.message);
  }
}

testSearchAfterUpload();
