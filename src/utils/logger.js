const { createLogger, format, transports } = require('winston');
const { Log } = require('../models');

// MongoDB transport for Winston
class MongoDBTransport extends transports.Transport {
  constructor(opts) {
    super(opts);
    this.name = 'MongoDBTransport';
  }

  async log(info, callback) {
    try {
      await Log.create({
        level: info.level,
        message: info.message,
        context: info.context || 'general',
        metadata: info.metadata || {},
        timestamp: new Date(),
        ...info
      });
      callback();
    } catch (error) {
      console.error('Error saving log to MongoDB:', error);
      callback();
    }
  }
}

// 로그 포맷 정의
const logFormat = format.combine(
  format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  format.errors({ stack: true }),
  format.splat(),
  format.json()
);

// 로거 생성
const logger = createLogger({
  format: logFormat,
  transports: [
    // Console transport
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.printf(
          ({ timestamp, level, message, context, ...metadata }) => {
            let msg = `${timestamp} [${level}] ${context ? `[${context}] ` : ''}${message}`;
            if (Object.keys(metadata).length > 0) {
              msg += '\n' + JSON.stringify(metadata, null, 2);
            }
            return msg;
          }
        )
      )
    }),
    // File transport for errors
    new transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // File transport for all logs
    new transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // MongoDB transport
    new MongoDBTransport()
  ]
});

module.exports = logger;