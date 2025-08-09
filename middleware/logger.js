// Middleware logging cho API requests
const requestLogger = (req, res, next) => {
  const startTime = Date.now();
  
  // Log request
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl} - IP: ${req.ip}`);
  
  // Log request body cho POST/PUT requests (nhưng không log file data)
  if ((req.method === 'POST' || req.method === 'PUT') && req.body) {
    const logBody = { ...req.body };
    // Xóa sensitive data
    delete logBody.password;
    delete logBody.token;
    console.log('Request body:', JSON.stringify(logBody, null, 2));
  }
  
  // Override res.json để log response
  const originalJson = res.json;
  res.json = function(data) {
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl} - ${res.statusCode} - ${duration}ms`);
    
    // Log response cho development
    if (process.env.NODE_ENV === 'development' && res.statusCode >= 400) {
      console.log('Error response:', JSON.stringify(data, null, 2));
    }
    
    return originalJson.call(this, data);
  };
  
  next();
};

// Middleware để validate API key (nếu cần)
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  const validApiKey = process.env.API_KEY;
  
  // Nếu không có API_KEY trong env, bỏ qua validation
  if (!validApiKey) {
    return next();
  }
  
  if (!apiKey || apiKey !== validApiKey) {
    return res.status(401).json({
      success: false,
      message: 'API key không hợp lệ'
    });
  }
  
  next();
};

// Middleware rate limiting cơ bản
const rateLimit = () => {
  const requests = new Map();
  
  return (req, res, next) => {
    const clientIP = req.ip;
    const now = Date.now();
    const windowMs = 15 * 60 * 1000; // 15 phút
    const maxRequests = 100; // 100 requests mỗi 15 phút
    
    if (!requests.has(clientIP)) {
      requests.set(clientIP, []);
    }
    
    const clientRequests = requests.get(clientIP);
    
    // Xóa requests cũ
    const validRequests = clientRequests.filter(time => now - time < windowMs);
    
    if (validRequests.length >= maxRequests) {
      return res.status(429).json({
        success: false,
        message: 'Quá nhiều requests. Vui lòng thử lại sau.'
      });
    }
    
    validRequests.push(now);
    requests.set(clientIP, validRequests);
    
    next();
  };
};

module.exports = {
  requestLogger,
  validateApiKey,
  rateLimit
};
