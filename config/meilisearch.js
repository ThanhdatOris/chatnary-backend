const { MeiliSearch } = require('meilisearch');

// Khởi tạo Meilisearch client
const meilisearchClient = new MeiliSearch({
  host: process.env.MEILISEARCH_HOST || 'http://localhost:7700',
  apiKey: process.env.MEILISEARCH_API_KEY || ''
});

// Tạo index cho documents
const initMeilisearch = async () => {
  try {
    const index = await meilisearchClient.createIndex('documents', {
      primaryKey: 'id'
    });
    
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
    if (error.code === 'index_already_exists') {
      console.log('✅ Meilisearch index đã tồn tại, đang cập nhật cấu hình...');
      
      // Cập nhật cấu hình cho index đã tồn tại
      try {
        const index = meilisearchClient.index('documents');
        
        await index.updateSearchableAttributes([
          'title',
          'content',
          'originalName'
        ]);
        
        await index.updateFilterableAttributes([
          'uploadTime',
          'fileType',
          'size'
        ]);
        
        await index.updateSortableAttributes([
          'uploadTime',
          'size',
          'title'
        ]);
        
        console.log('✅ Cấu hình Meilisearch đã được cập nhật');
      } catch (updateError) {
        console.error('⚠️  Lỗi cập nhật cấu hình Meilisearch:', updateError.message);
      }
    } else {
      console.error('⚠️  Lỗi khởi tạo Meilisearch:', error.message);
      console.log('💡 Tip: Hãy cài đặt và khởi động Meilisearch server');
      console.log('💡 Download: https://github.com/meilisearch/meilisearch/releases');
      console.log('💡 Server sẽ chạy mà không có search (chức năng bị hạn chế)');
    }
  }
};

module.exports = {
  meilisearchClient,
  initMeilisearch
};
