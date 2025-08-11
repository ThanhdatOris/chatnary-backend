const axios = require('axios');

async function testAuth() {
  console.log('🧪 Testing Authentication...');
  
  const testUser = {
    fullName: 'Test User New',
    email: 'testuser@example.com',
    password: 'password123'
  };

  try {
    // Test Registration
    console.log('1. Testing Registration...');
    const registerResponse = await axios.post('http://localhost:5000/api/auth/register', testUser);
    console.log('✅ Registration successful:', registerResponse.data);
    
    // Test Login
    console.log('\n2. Testing Login...');
    const loginResponse = await axios.post('http://localhost:5000/api/auth/login', {
      email: testUser.email,
      password: testUser.password
    });
    console.log('✅ Login successful:', loginResponse.data);

  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
  }
}

testAuth();
