// Test Meilisearch connection
const { MeiliSearch } = require('meilisearch');

const client = new MeiliSearch({
  host: 'http://localhost:7700',
  apiKey: 'chatnary_master_key_2025'
});

async function testConnection() {
  try {
    const health = await client.health();
    console.log('✅ Meilisearch connected:', health);
    
    const version = await client.getVersion();
    console.log('📊 Version:', version);
    
    const indexes = await client.getIndexes();
    console.log('📂 Indexes:', indexes);
    
  } catch (error) {
    console.error('❌ Connection failed:', error.message);
  }
}

testConnection();
