/**
 * GhoraGhuri — Socket Authentication Middleware
 * Verifies JWT token on socket connection.
 */
import jwt from 'jsonwebtoken';
import { Socket } from 'socket.io';
import { config } from '../config';
import { AuthPayload, SocketData } from '../types';

export function authMiddleware(socket: Socket, next: (err?: Error) => void): void {
  try {
    const token =
      socket.handshake.auth?.token ||
      socket.handshake.headers?.authorization?.replace('Bearer ', '');

    if (!token) {
      return next(new Error('Authentication required'));
    }

    const payload = jwt.verify(token, config.jwtSecret) as AuthPayload;

    // Attach user data to socket
    (socket.data as SocketData) = {
      userId: payload.sub,
      msisdn: payload.msisdn,
    };

    next();
  } catch (err) {
    console.error('Socket auth failed:', (err as Error).message);
    next(new Error('Invalid or expired token'));
  }
}
