const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

async function testAuthentication() {
  console.log('🔐 Testing Authentication System...');
  console.log('=' .repeat(50));
  
  try {
    // Test 1: Register new user
    console.log('\n1️⃣ Testing User Registration...');
    const registerData = {
      email: 'test@chatnary.com',
      password: 'testpassword123',
      fullName: 'Test User'
    };
    
    const registerResponse = await axios.post(`${BASE_URL}/api/auth/register`, registerData);
    console.log('✅ Registration successful:', {
      user: registerResponse.data.user,
      hasToken: !!registerResponse.data.token
    });
    
    const token = registerResponse.data.token;
    
    // Test 2: Verify token
    console.log('\n2️⃣ Testing Token Verification...');
    const verifyResponse = await axios.get(`${BASE_URL}/api/auth/verify`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('✅ Token verification successful:', verifyResponse.data);
    
    // Test 3: Get profile
    console.log('\n3️⃣ Testing Get Profile...');
    const profileResponse = await axios.get(`${BASE_URL}/api/auth/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('✅ Get profile successful:', profileResponse.data.user);
    
    // Test 4: Update profile
    console.log('\n4️⃣ Testing Update Profile...');
    const updateResponse = await axios.put(`${BASE_URL}/api/auth/profile`, 
      { fullName: 'Updated Test User' },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    console.log('✅ Update profile successful:', updateResponse.data.message);
    
    // Test 5: Login with same credentials
    console.log('\n5️⃣ Testing User Login...');
    const loginResponse = await axios.post(`${BASE_URL}/api/auth/login`, {
      email: 'test@chatnary.com',
      password: 'testpassword123'
    });
    console.log('✅ Login successful:', {
      user: loginResponse.data.user,
      hasToken: !!loginResponse.data.token
    });
    
    // Test 6: Protected file operations
    console.log('\n6️⃣ Testing Protected File Operations...');
    
    // Test accessing files without token (should fail)
    try {
      await axios.get(`${BASE_URL}/api/files`);
      console.log('❌ Unexpected: Access files without token should fail');
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('✅ Correctly blocked access without token');
      } else {
        console.log('❌ Unexpected error:', error.message);
      }
    }
    
    // Test accessing files with token (should work)
    const filesResponse = await axios.get(`${BASE_URL}/api/files`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('✅ Access files with token successful:', {
      totalFiles: filesResponse.data.data.pagination.total
    });
    
    console.log('\n🎉 All authentication tests passed!');
    
    return token; // Return token for further tests
    
  } catch (error) {
    console.log('❌ Authentication test failed:', error.response?.data || error.message);
    throw error;
  }
}

// Test duplicate registration
async function testDuplicateRegistration() {
  console.log('\n7️⃣ Testing Duplicate Registration...');
  try {
    await axios.post(`${BASE_URL}/api/auth/register`, {
      email: 'test@chatnary.com', // Same email
      password: 'anotherpassword',
      fullName: 'Another User'
    });
    console.log('❌ Unexpected: Duplicate registration should fail');
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Correctly blocked duplicate registration:', error.response.data.message);
    } else {
      console.log('❌ Unexpected error:', error.message);
    }
  }
}

// Test invalid login
async function testInvalidLogin() {
  console.log('\n8️⃣ Testing Invalid Login...');
  try {
    await axios.post(`${BASE_URL}/api/auth/login`, {
      email: 'test@chatnary.com',
      password: 'wrongpassword'
    });
    console.log('❌ Unexpected: Invalid login should fail');
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('✅ Correctly blocked invalid login:', error.response.data.message);
    } else {
      console.log('❌ Unexpected error:', error.message);
    }
  }
}

// Main test runner
async function runAuthTests() {
  try {
    const token = await testAuthentication();
    await testDuplicateRegistration();
    await testInvalidLogin();
    
    console.log('\n' + '=' .repeat(50));
    console.log('🎯 Next Steps:');
    console.log('   1. Build Frontend Login/Register pages');
    console.log('   2. Test file upload with authentication');
    console.log('   3. Implement user-specific file filtering');
    console.log('   4. Start working on Chat API');
    console.log('\n💡 Save this token for testing:');
    console.log(`   Bearer ${token}`);
    
  } catch (error) {
    console.log('\n❌ Test suite failed');
  }
}

runAuthTests();
