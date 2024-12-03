class CrawlerError extends Error {
    constructor(message, type, url) {
      super(message);
      this.name = 'CrawlerError';
      this.type = type;
      this.url = url;
      this.timestamp = new Date();
    }
  }
  
  class NetworkError extends CrawlerError {
    constructor(message, url) {
      super(message, 'NetworkError', url);
      this.name = 'NetworkError';
    }
  }
  
  class ParseError extends CrawlerError {
    constructor(message, url) {
      super(message, 'ParseError', url);
      this.name = 'ParseError';
    }
  }
  
  module.exports = {
    CrawlerError,
    NetworkError,
    ParseError
  };