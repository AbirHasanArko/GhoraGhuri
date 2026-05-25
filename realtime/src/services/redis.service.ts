/**
 * GhoraGhuri — Redis Service
 * Handles GPS point buffering, pub/sub, and cache operations.
 */
import Redis from 'ioredis';
import { config } from '../config';
import { GpsPoint } from '../types';

let redis: Redis | null = null;

export function getRedis(): Redis {
  if (!redis) {
    redis = new Redis(config.redisUrl, {
      maxRetriesPerRequest: 3,
      lazyConnect: true,
      retryStrategy: () => null, // Do not retry connection if Redis is missing
    });

    redis.on('connect', () => console.log('✅ Redis connected (realtime)'));
    redis.on('error', (err) => console.error('❌ Redis error:', err.message));
  }
  return redis;
}

export async function connectRedis(): Promise<void> {
  const r = getRedis();
  await r.connect();
}

export async function closeRedis(): Promise<void> {
  if (redis) {
    await redis.quit();
    redis = null;
  }
}

/**
 * Buffer a GPS point for a contribution in Redis.
 * Points are stored in a list: gps:{contributionId}
 */
export async function bufferGpsPoint(
  contributionId: string,
  point: GpsPoint,
): Promise<number> {
  const r = getRedis();
  const key = `gps:${contributionId}`;

  // Add point to Redis list
  const length = await r.rpush(key, JSON.stringify(point));

  // Set TTL (1 hour) to prevent orphaned data
  if (length === 1) {
    await r.expire(key, 3600);
  }

  return length;
}

/**
 * Get all buffered GPS points for a contribution.
 */
export async function getBufferedPoints(
  contributionId: string,
): Promise<GpsPoint[]> {
  const r = getRedis();
  const key = `gps:${contributionId}`;
  const raw = await r.lrange(key, 0, -1);
  return raw.map((s) => JSON.parse(s) as GpsPoint);
}

/**
 * Flush GPS points from Redis (after writing to DB).
 */
export async function flushGpsBuffer(contributionId: string): Promise<void> {
  const r = getRedis();
  await r.del(`gps:${contributionId}`);
}

/**
 * Get the number of active GPS sessions.
 */
export async function getActiveSessionCount(): Promise<number> {
  const r = getRedis();
  const keys = await r.keys('gps_session:*');
  return keys.length;
}

/**
 * Register an active GPS session.
 */
export async function registerSession(
  userId: string,
  contributionId: string,
): Promise<void> {
  const r = getRedis();
  await r.setex(
    `gps_session:${userId}`,
    3600,
    JSON.stringify({ contributionId, startedAt: new Date().toISOString() }),
  );
}

/**
 * Remove a GPS session.
 */
export async function removeSession(userId: string): Promise<void> {
  const r = getRedis();
  await r.del(`gps_session:${userId}`);
}
