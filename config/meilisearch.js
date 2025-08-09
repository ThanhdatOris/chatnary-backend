const { MeiliSearch } = require('meilisearch');

// Khởi tạo Meilisearch client
const meilisearchClient = new MeiliSearch({
  host: process.env.MEILISEARCH_HOST || 'http://localhost:7700',
  apiKey: process.env.MEILISEARCH_API_KEY || ''
});

// Tạo index cho documents
const initMeilisearch = async () => {
  try {
    // Thử lấy index trước, nếu không có thì tạo mới
    let index;
    try {
      index = meilisearchClient.index('documents');
      await index.getStats(); // Test xem index có tồn tại không
      console.log('✅ Meilisearch index đã tồn tại, đang cập nhật cấu hình...');
    } catch (getError) {
      // Index chưa tồn tại, tạo mới
      const createResult = await meilisearchClient.createIndex('documents', {
        primaryKey: 'id'
      });
      // Đợi task hoàn thành
      await meilisearchClient.waitForTask(createResult.taskUid);
      index = meilisearchClient.index('documents');
      console.log('✅ Meilisearch index mới đã được tạo');
    }
    
    // Cấu hình searchable attributes
    await index.updateSearchableAttributes([
      'title',
      'content',
      'originalName'
    ]);

    // Cấu hình filterable attributes
    await index.updateFilterableAttributes([
      'uploadTime',
      'fileType',
      'size'
    ]);

    // Cấu hình sortable attributes
    await index.updateSortableAttributes([
      'uploadTime',
      'size',
      'title'
    ]);

    // Cấu hình faceting (cho filter UI)
    await index.updateFaceting({
      maxValuesPerFacet: 100
    });

    // Cấu hình ranking rules
    await index.updateRankingRules([
      'words',
      'typo',
      'proximity',
      'attribute',
      'sort',
      'exactness'
    ]);

    console.log('✅ Meilisearch index đã được khởi tạo và cấu hình');
  } catch (error) {
    console.error('⚠️  Lỗi khởi tạo Meilisearch:', error.message);
    console.log('💡 Tip: Hãy cài đặt và khởi động Meilisearch server');
    console.log('💡 Download: https://github.com/meilisearch/meilisearch/releases');
    console.log('💡 Server sẽ chạy mà không có search (chức năng bị hạn chế)');
  }
};

module.exports = {
  meilisearchClient,
  initMeilisearch
};
