/**
 * GhoraGhuri (ঘোরাঘুরি) — Realtime Server
 * Socket.io server for GPS streaming and crowd reporting.
 */
import http from 'http';
import { Server } from 'socket.io';
import { config } from './config';
import { authMiddleware } from './socket/auth.middleware';
import { setupGpsHandler } from './socket/gps.handler';
import { connectRedis, closeRedis } from './services/redis.service';

async function main(): Promise<void> {
  console.log('🚀 Starting GhoraGhuri Realtime Server...');

  // Connect to Redis
  try {
    await connectRedis();
  } catch (err) {
    console.error('❌ Failed to connect to Redis:', (err as Error).message);
    console.warn('⚠️ Running without Redis — GPS buffering will not work');
  }

  // Create HTTP + Socket.io server
  const httpServer = http.createServer((req, res) => {
    // Basic health check
    if (req.url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'healthy',
        service: 'ghoraghuri-realtime',
        version: '1.0.0',
      }));
      return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'GhoraGhuri Realtime',
      name_bn: 'ঘোরাঘুরি রিয়েলটাইম',
      description: 'Socket.io server for GPS streaming and crowd reporting',
    }));
  });

  const io = new Server(httpServer, {
    cors: {
      origin: config.corsOrigin,
      methods: ['GET', 'POST'],
      credentials: true,
    },
    pingTimeout: 60000,
    pingInterval: 25000,
    maxHttpBufferSize: 1e6, // 1MB
  });

  // ── GPS Namespace (/gps) ──────────────────────────────
  const gpsNamespace = io.of('/gps');
  gpsNamespace.use(authMiddleware);
  setupGpsHandler(gpsNamespace);

  // ── Crowd Namespace (/crowd) ──────────────────────────
  const crowdNamespace = io.of('/crowd');
  crowdNamespace.use(authMiddleware);

  crowdNamespace.on('connection', (socket) => {
    const data = socket.data;
    console.log(`👥 Crowd client connected: ${data.userId}`);

    socket.on('crowd:report', (report) => {
      console.log(`📊 Crowd report from ${data.userId}:`, report);
      // Broadcast to other clients for real-time crowd display
      socket.broadcast.emit('crowd:update', {
        ...report,
        reportedBy: data.userId,
        timestamp: new Date().toISOString(),
      });
    });

    socket.on('disconnect', () => {
      console.log(`👥 Crowd client disconnected: ${data.userId}`);
    });
  });

  // ── Connection stats ──────────────────────────────────
  setInterval(() => {
    const gpsCount = gpsNamespace.sockets.size;
    const crowdCount = crowdNamespace.sockets.size;
    if (gpsCount > 0 || crowdCount > 0) {
      console.log(`📊 Active connections — GPS: ${gpsCount} | Crowd: ${crowdCount}`);
    }
  }, 30000);

  // ── Start server ──────────────────────────────────────
  httpServer.listen(config.port, () => {
    console.log(`🟢 GhoraGhuri Realtime running on port ${config.port}`);
    console.log(`   GPS namespace:   ws://localhost:${config.port}/gps`);
    console.log(`   Crowd namespace: ws://localhost:${config.port}/crowd`);
  });

  // ── Graceful shutdown ─────────────────────────────────
  const shutdown = async () => {
    console.log('\n🔴 Shutting down realtime server...');
    io.close();
    await closeRedis();
    httpServer.close();
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch(console.error);
