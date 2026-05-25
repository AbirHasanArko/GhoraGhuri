/**
 * GhoraGhuri — GPS Streaming Socket Handler
 *
 * Protocol:
 * 1. Client connects to /gps namespace with JWT auth
 * 2. Client emits 'gps:start' with {contributionId, transportMode}
 * 3. Client emits 'gps:point' every 3-5 seconds: {lat, lng, accuracy, speed, timestamp}
 * 4. Server buffers in Redis (RPUSH gps:{contributionId})
 * 5. Client emits 'gps:stop' → server finalizes
 */
import { Namespace, Socket } from 'socket.io';
import { GpsPoint, SocketData } from '../types';
import {
  bufferGpsPoint,
  registerSession,
  removeSession,
} from '../services/redis.service';

export function setupGpsHandler(nsp: Namespace): void {
  nsp.on('connection', (socket: Socket) => {
    const data = socket.data as SocketData;
    console.log(`📍 GPS client connected: ${data.userId}`);

    // ── Start GPS tracking ──────────────────────────────
    socket.on('gps:start', async (payload: { contributionId: string; transportMode?: string }) => {
      try {
        const { contributionId, transportMode } = payload;

        data.gpsSession = {
          contributionId,
          userId: data.userId,
          startedAt: new Date(),
          pointCount: 0,
        };

        await registerSession(data.userId, contributionId);

        socket.emit('gps:started', {
          contributionId,
          message: 'GPS tracking started',
        });

        console.log(`▶️ GPS session started: user=${data.userId} contribution=${contributionId}`);
      } catch (err) {
        console.error('GPS start error:', err);
        socket.emit('gps:error', { message: 'Failed to start GPS tracking' });
      }
    });

    // ── Receive GPS point ───────────────────────────────
    socket.on('gps:point', async (point: GpsPoint) => {
      try {
        if (!data.gpsSession) {
          socket.emit('gps:error', { message: 'No active GPS session. Call gps:start first.' });
          return;
        }

        // Validate point
        if (!point.lat || !point.lng || point.lat < -90 || point.lat > 90) {
          return; // silently drop invalid points
        }

        // Add timestamp if missing
        if (!point.timestamp) {
          point.timestamp = new Date().toISOString();
        }

        const bufferSize = await bufferGpsPoint(data.gpsSession.contributionId, point);
        data.gpsSession.pointCount++;

        // Send ack every 10 points
        if (data.gpsSession.pointCount % 10 === 0) {
          socket.emit('gps:ack', {
            pointCount: data.gpsSession.pointCount,
            bufferSize,
          });
        }
      } catch (err) {
        console.error('GPS point error:', err);
      }
    });

    // ── Stop GPS tracking ───────────────────────────────
    socket.on('gps:stop', async () => {
      try {
        if (data.gpsSession) {
          await removeSession(data.userId);

          socket.emit('gps:stopped', {
            contributionId: data.gpsSession.contributionId,
            totalPoints: data.gpsSession.pointCount,
            message: 'GPS tracking stopped. Complete the track via API to earn coins.',
          });

          console.log(
            `⏹️ GPS session stopped: user=${data.userId} ` +
            `contribution=${data.gpsSession.contributionId} ` +
            `points=${data.gpsSession.pointCount}`,
          );

          data.gpsSession = undefined;
        }
      } catch (err) {
        console.error('GPS stop error:', err);
      }
    });

    // ── Disconnect ──────────────────────────────────────
    socket.on('disconnect', async (reason) => {
      console.log(`📍 GPS client disconnected: ${data.userId} (${reason})`);

      if (data.gpsSession) {
        await removeSession(data.userId);
        console.log(`⚠️ GPS session orphaned: ${data.gpsSession.contributionId}`);
      }
    });
  });
}
