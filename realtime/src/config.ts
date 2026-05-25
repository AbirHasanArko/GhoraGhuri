/**
 * GhoraGhuri — Realtime Server Configuration
 */
import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379/0',
  jwtSecret: process.env.JWT_SECRET || 'jwt-secret-change-in-production',

  // GPS batch settings
  gpsBatchIntervalMs: parseInt(process.env.GPS_BATCH_INTERVAL_MS || '10000', 10), // 10 seconds
  gpsMaxBufferSize: parseInt(process.env.GPS_MAX_BUFFER_SIZE || '1000', 10),

  // CORS
  corsOrigin: process.env.CORS_ORIGIN || '*',
};
