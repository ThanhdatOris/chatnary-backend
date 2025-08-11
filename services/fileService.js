const fs = require('fs');
const path = require('path');
const { getDB } = require('../config/mongodb');
const { meilisearchClient } = require('../config/meilisearch');

// Service để lưu metadata file vào MongoDB với user subcollection
const saveFileMetadata = async (fileData) => {
  try {
    const db = getDB();
    
    // Create users collection if not exists
    const usersCollection = db.collection('users');
    
    // Ensure user document exists
    await usersCollection.updateOne(
      { _id: fileData.userId },
      { 
        $setOnInsert: { 
          _id: fileData.userId,
          email: fileData.userEmail,
          createdAt: new Date()
        }
      },
      { upsert: true }
    );
    
    // Use files as subcollection within the main files collection
    // but with clear user ownership
    const filesCollection = db.collection('files');
    
    const metadata = {
      ...fileData,
      id: fileData.filename, // Dùng filename làm unique ID
      uploadTime: new Date(),
      indexed: false, // Đánh dấu chưa được index
      userId: fileData.userId, // Ensure userId is always present
      userEmail: fileData.userEmail
    };
    
    const result = await filesCollection.insertOne(metadata);
    console.log('File metadata đã được lưu với user subcollection structure:', result.insertedId);
    
    return metadata;
  } catch (error) {
    console.error('Lỗi lưu file metadata:', error);
    throw error;
  }
};

// Service để index file content vào Meilisearch
const indexFileContent = async (fileMetadata) => {
  try {
    // TODO: Implement text extraction từ các loại file khác nhau
    let content = '';
    
    if (fileMetadata.mimetype === 'text/plain' || path.extname(fileMetadata.originalName) === '.txt') {
      content = fs.readFileSync(fileMetadata.path, 'utf8');
    } else {
      // Placeholder cho các loại file khác (PDF, DOCX)
      content = `Content from ${fileMetadata.originalName}`;
    }
    
    const document = {
      id: fileMetadata.id,
      title: fileMetadata.originalName,
      content: content,
      originalName: fileMetadata.originalName,
      fileType: path.extname(fileMetadata.originalName),
      size: fileMetadata.size,
      uploadTime: fileMetadata.uploadTime,
      path: fileMetadata.path
    };
    
    const index = meilisearchClient.index('documents');
    await index.addDocuments([document]);
    
    // Cập nhật trạng thái indexed trong MongoDB
    const db = getDB();
    await db.collection('files').updateOne(
      { id: fileMetadata.id },
      { $set: { indexed: true } }
    );
    
    console.log('File đã được index vào Meilisearch:', fileMetadata.originalName);
    
  } catch (error) {
    console.error('Lỗi index file:', error);
    throw error;
  }
};

// Service tìm kiếm file
const searchFiles = async (query, options = {}) => {
  try {
    const index = meilisearchClient.index('documents');
    
    const defaultOptions = {
      limit: 20,
      offset: 0,
      attributesToHighlight: ['title', 'content'],
      attributesToCrop: ['content'],
      cropLength: 200,
      attributesToRetrieve: ['*'],
      showMatchesPosition: true
    };
    
    const searchOptions = { ...defaultOptions, ...options };
    
    // Nếu query rỗng, trả về tất cả documents
    if (!query || query.trim() === '') {
      const results = await index.getDocuments(searchOptions);
      return {
        hits: results.results || [],
        query: '',
        processingTimeMs: 0,
        estimatedTotalHits: results.total || 0,
        offset: searchOptions.offset,
        limit: searchOptions.limit
      };
    }
    
    const results = await index.search(query, searchOptions);
    return results;
  } catch (error) {
    console.error('Lỗi tìm kiếm:', error);
    throw error;
  }
};

// Service tìm kiếm với facets (lọc theo thuộc tính)
const searchWithFacets = async (query, facets = [], filters = []) => {
  try {
    const index = meilisearchClient.index('documents');
    
    const searchOptions = {
      facets: facets,
      filter: filters.length > 0 ? filters.join(' AND ') : undefined,
      limit: 50,
      attributesToHighlight: ['title', 'content'],
      attributesToCrop: ['content'],
      cropLength: 150
    };
    
    const results = await index.search(query, searchOptions);
    return results;
  } catch (error) {
    console.error('Lỗi tìm kiếm với facets:', error);
    throw error;
  }
};

// Service lấy document theo ID
const getDocumentById = async (documentId) => {
  try {
    const index = meilisearchClient.index('documents');
    const document = await index.getDocument(documentId);
    return document;
  } catch (error) {
    console.error('Lỗi lấy document:', error);
    throw error;
  }
};

module.exports = {
  saveFileMetadata,
  indexFileContent,
  searchFiles,
  searchWithFacets,
  getDocumentById
};
