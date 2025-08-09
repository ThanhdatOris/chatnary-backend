const { searchFiles } = require('../services/fileService');
const { getDB } = require('../config/mongodb');

// Controller tìm kiếm file
const searchController = async (req, res) => {
  try {
    const { 
      query = '', 
      limit = 20, 
      offset = 0,
      fileType = '',
      dateFrom = '',
      dateTo = '',
      sortBy = 'uploadTime',
      sortOrder = 'desc'
    } = req.query;

    // Xây dựng filters cho Meilisearch
    const filters = [];
    
    if (fileType) {
      filters.push(`fileType = "${fileType}"`);
    }
    
    if (dateFrom) {
      filters.push(`uploadTime >= ${new Date(dateFrom).getTime()}`);
    }
    
    if (dateTo) {
      filters.push(`uploadTime <= ${new Date(dateTo).getTime()}`);
    }

    const searchOptions = {
      limit: parseInt(limit),
      offset: parseInt(offset),
      attributesToHighlight: ['title', 'content'],
      attributesToCrop: ['content'],
      cropLength: 200,
      filter: filters.length > 0 ? filters.join(' AND ') : undefined,
      sort: [`${sortBy}:${sortOrder}`]
    };

    // Thực hiện tìm kiếm
    const results = await searchFiles(query, searchOptions);
    
    // Lấy thêm metadata từ MongoDB nếu cần
    const enrichedResults = await enrichSearchResults(results.hits);

    res.json({
      success: true,
      data: {
        hits: enrichedResults,
        query: query,
        processingTimeMs: results.processingTimeMs,
        hitsCount: results.estimatedTotalHits || results.hits.length,
        offset: results.offset,
        limit: results.limit,
        facetDistribution: results.facetDistribution || {}
      }
    });

  } catch (error) {
    console.error('Lỗi tìm kiếm:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi server khi tìm kiếm',
      error: error.message 
    });
  }
};

// Làm giàu kết quả tìm kiếm với metadata từ MongoDB
const enrichSearchResults = async (hits) => {
  try {
    const db = getDB();
    const collection = db.collection('files');
    
    const enrichedHits = await Promise.all(
      hits.map(async (hit) => {
        const fileMetadata = await collection.findOne({ id: hit.id });
        
        return {
          ...hit,
          metadata: fileMetadata ? {
            uploadTime: fileMetadata.uploadTime,
            indexed: fileMetadata.indexed,
            downloadUrl: `/uploads/${fileMetadata.filename}`,
            fileSize: formatFileSize(fileMetadata.size)
          } : null
        };
      })
    );
    
    return enrichedHits;
  } catch (error) {
    console.error('Lỗi làm giàu kết quả tìm kiếm:', error);
    return hits; // Trả về kết quả gốc nếu có lỗi
  }
};

// Controller lấy gợi ý tìm kiếm
const getSuggestions = async (req, res) => {
  try {
    const { q = '' } = req.query;
    
    if (q.length < 2) {
      return res.json({
        success: true,
        suggestions: []
      });
    }

    // Tìm kiếm với limit nhỏ để lấy gợi ý
    const results = await searchFiles(q, {
      limit: 5,
      attributesToRetrieve: ['title', 'originalName'],
      attributesToHighlight: []
    });

    const suggestions = results.hits.map(hit => ({
      text: hit.originalName || hit.title,
      type: 'file'
    }));

    res.json({
      success: true,
      suggestions: suggestions
    });

  } catch (error) {
    console.error('Lỗi lấy gợi ý:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi server khi lấy gợi ý' 
    });
  }
};

// Controller lấy thống kê file
const getFileStats = async (req, res) => {
  try {
    const db = getDB();
    const collection = db.collection('files');
    
    // Đếm tổng số file
    const totalFiles = await collection.countDocuments();
    
    // Đếm file theo loại
    const fileTypeStats = await collection.aggregate([
      {
        $group: {
          _id: {
            $arrayElemAt: [
              { $split: ["$originalName", "."] },
              -1
            ]
          },
          count: { $sum: 1 },
          totalSize: { $sum: "$size" }
        }
      },
      { $sort: { count: -1 } }
    ]).toArray();

    // Đếm file đã indexed
    const indexedFiles = await collection.countDocuments({ indexed: true });
    
    // File upload gần đây (7 ngày)
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const recentFiles = await collection.countDocuments({
      uploadTime: { $gte: sevenDaysAgo }
    });

    res.json({
      success: true,
      stats: {
        totalFiles,
        indexedFiles,
        recentFiles,
        fileTypes: fileTypeStats.map(stat => ({
          extension: stat._id,
          count: stat.count,
          totalSize: formatFileSize(stat.totalSize)
        }))
      }
    });

  } catch (error) {
    console.error('Lỗi lấy thống kê:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Lỗi server khi lấy thống kê' 
    });
  }
};

// Utility function để format kích thước file
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

module.exports = {
  searchController,
  getSuggestions,
  getFileStats
};
