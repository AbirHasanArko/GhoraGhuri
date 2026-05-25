/**
 * GhoraGhuri — Type Definitions
 */

export interface GpsPoint {
  lat: number;
  lng: number;
  accuracy?: number;
  speed?: number;
  timestamp: string;
}

export interface CrowdReport {
  edgeId?: string;
  nodeCode?: string;
  crowdLevel: 'low' | 'medium' | 'high' | 'extreme';
  lat?: number;
  lng?: number;
  notes?: string;
}

export interface GpsSession {
  contributionId: string;
  userId: string;
  startedAt: Date;
  pointCount: number;
}

export interface AuthPayload {
  sub: string;      // user ID
  msisdn: string;
  iat: number;
  exp: number;
}

export interface SocketData {
  userId: string;
  msisdn: string;
  gpsSession?: GpsSession;
}
