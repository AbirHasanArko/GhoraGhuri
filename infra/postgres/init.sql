-- ============================================================
-- GhoraGhuri (ঘোরাঘুরি) — Database Schema
-- PostgreSQL 16 + PostGIS
-- ============================================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- for fuzzy text search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE user_language AS ENUM ('en', 'bn');
CREATE TYPE node_type AS ENUM (
    'bus_stop', 'hub', 'rickshaw_stand', 'launch_ghat',
    'cng_stand', 'intersection', 'tempo_stand', 'train_station'
);
CREATE TYPE transport_mode AS ENUM (
    'bus', 'rickshaw', 'cng', 'leguna', 'tempo',
    'walking', 'launch', 'train'
);
CREATE TYPE crowd_level AS ENUM ('low', 'medium', 'high', 'extreme');
CREATE TYPE payment_status AS ENUM ('pending', 'charged', 'failed', 'refunded');
CREATE TYPE transaction_type AS ENUM (
    'route_charge', 'contribution_reward',
    'airtime_redemption', 'bonus', 'refund'
);
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed');
CREATE TYPE contribution_type AS ENUM (
    'gps_track', 'crowd_report', 'route_verify', 'stop_report'
);
CREATE TYPE validation_status AS ENUM ('pending', 'validated', 'rejected');

-- ============================================================
-- USERS & AUTHENTICATION
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    msisdn VARCHAR(15) NOT NULL UNIQUE,           -- e.g. '01812345678'
    msisdn_full VARCHAR(20) NOT NULL,              -- e.g. 'tel:8801812345678'
    bdapps_subscriber_id VARCHAR(255),             -- masked subscriber ID from bdapps
    display_name VARCHAR(100),
    language_pref user_language NOT NULL DEFAULT 'bn',
    is_active BOOLEAN NOT NULL DEFAULT true,
    total_contributions INTEGER NOT NULL DEFAULT 0,
    reputation_score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jwt_token TEXT NOT NULL,
    refresh_token TEXT,
    device_info JSONB,                             -- {model, os, app_version}
    ip_address INET,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_revoked BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at) WHERE NOT is_revoked;

-- ============================================================
-- TRANSPORT GRAPH — NODES
-- ============================================================

CREATE TABLE transport_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,              -- e.g. 'MIR10', 'DHN27', 'FGT01'
    name_en VARCHAR(200) NOT NULL,
    name_bn VARCHAR(200) NOT NULL,
    node_type node_type NOT NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    address_en VARCHAR(500),
    address_bn VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB DEFAULT '{}',                   -- additional properties
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_nodes_location ON transport_nodes USING GIST(location);
CREATE INDEX idx_nodes_code ON transport_nodes(code);
CREATE INDEX idx_nodes_name_en_trgm ON transport_nodes USING GIN(name_en gin_trgm_ops);
CREATE INDEX idx_nodes_name_bn_trgm ON transport_nodes USING GIN(name_bn gin_trgm_ops);
CREATE INDEX idx_nodes_active ON transport_nodes(is_active) WHERE is_active = true;

-- ============================================================
-- TRANSPORT GRAPH — EDGES
-- ============================================================

CREATE TABLE transport_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_node_id UUID NOT NULL REFERENCES transport_nodes(id) ON DELETE CASCADE,
    to_node_id UUID NOT NULL REFERENCES transport_nodes(id) ON DELETE CASCADE,
    transport_mode transport_mode NOT NULL,
    route_name_en VARCHAR(200),                    -- e.g. 'Bus Route 7'
    route_name_bn VARCHAR(200),                    -- e.g. 'বাস রুট ৭'
    base_time_minutes FLOAT NOT NULL,
    base_fare_bdt FLOAT NOT NULL DEFAULT 0,
    distance_meters FLOAT NOT NULL DEFAULT 0,
    crowd_level crowd_level NOT NULL DEFAULT 'medium',
    reliability_score FLOAT NOT NULL DEFAULT 0.7,  -- 0.0 to 1.0
    is_bidirectional BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_verified_at TIMESTAMPTZ,
    verification_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_time_positive CHECK (base_time_minutes > 0),
    CONSTRAINT chk_fare_non_negative CHECK (base_fare_bdt >= 0),
    CONSTRAINT chk_reliability_range CHECK (reliability_score >= 0 AND reliability_score <= 1),
    CONSTRAINT chk_no_self_loop CHECK (from_node_id != to_node_id)
);

CREATE INDEX idx_edges_from_node ON transport_edges(from_node_id) WHERE is_active = true;
CREATE INDEX idx_edges_to_node ON transport_edges(to_node_id) WHERE is_active = true;
CREATE INDEX idx_edges_mode ON transport_edges(transport_mode);
CREATE UNIQUE INDEX idx_edges_unique_route ON transport_edges(from_node_id, to_node_id, transport_mode, route_name_en)
    WHERE is_active = true;

-- ============================================================
-- EDGE SCHEDULES (time-of-day availability)
-- ============================================================

CREATE TABLE edge_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    edge_id UUID NOT NULL REFERENCES transport_edges(id) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    frequency_minutes FLOAT,                       -- how often the transport runs
    fare_multiplier FLOAT NOT NULL DEFAULT 1.0,    -- peak pricing
    CONSTRAINT chk_time_order CHECK (start_time < end_time)
);

CREATE INDEX idx_schedules_edge ON edge_schedules(edge_id);

-- ============================================================
-- ROUTE QUERIES
-- ============================================================

CREATE TABLE route_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    origin_location GEOGRAPHY(Point, 4326),
    destination_location GEOGRAPHY(Point, 4326),
    origin_text VARCHAR(500),
    destination_text VARCHAR(500),
    origin_node_id UUID REFERENCES transport_nodes(id),
    destination_node_id UUID REFERENCES transport_nodes(id),
    preferences JSONB DEFAULT '{"optimize": "time"}',
    result_json JSONB,                             -- full route result
    total_time_min FLOAT,
    total_time_max FLOAT,
    total_fare_min FLOAT,
    total_fare_max FLOAT,
    confidence_score FLOAT,
    charge_bdt FLOAT NOT NULL DEFAULT 2.0,
    payment_status payment_status NOT NULL DEFAULT 'pending',
    bdapps_trx_id VARCHAR(255),
    source VARCHAR(20) DEFAULT 'app',              -- 'app' or 'sms'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_queries_user ON route_queries(user_id, created_at DESC);
CREATE INDEX idx_queries_payment ON route_queries(payment_status);

-- ============================================================
-- ROUTE STEPS (individual legs of a route)
-- ============================================================

CREATE TABLE route_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES route_queries(id) ON DELETE CASCADE,
    step_order SMALLINT NOT NULL,
    from_node_id UUID NOT NULL REFERENCES transport_nodes(id),
    to_node_id UUID NOT NULL REFERENCES transport_nodes(id),
    edge_id UUID REFERENCES transport_edges(id),
    transport_mode transport_mode NOT NULL,
    instruction_en TEXT NOT NULL,
    instruction_bn TEXT NOT NULL,
    duration_minutes FLOAT NOT NULL,
    fare_bdt FLOAT NOT NULL DEFAULT 0,
    distance_meters FLOAT NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_steps_query ON route_steps(query_id, step_order);

-- ============================================================
-- WALLET & ECONOMY
-- ============================================================

CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    balance_coins INTEGER NOT NULL DEFAULT 0,
    total_earned INTEGER NOT NULL DEFAULT 0,
    total_spent INTEGER NOT NULL DEFAULT 0,
    total_redeemed_bdt FLOAT NOT NULL DEFAULT 0,
    last_transaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_balance_non_negative CHECK (balance_coins >= 0)
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    type transaction_type NOT NULL,
    amount_coins INTEGER NOT NULL,
    amount_bdt FLOAT,
    description_en VARCHAR(500),
    description_bn VARCHAR(500),
    reference_id UUID,                             -- FK to route_query or contribution
    bdapps_trx_id VARCHAR(255),
    status transaction_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_wallet ON transactions(wallet_id, created_at DESC);
CREATE INDEX idx_transactions_status ON transactions(status);

-- ============================================================
-- CONTRIBUTIONS
-- ============================================================

CREATE TABLE contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type contribution_type NOT NULL,
    location GEOGRAPHY(Point, 4326),
    related_edge_id UUID REFERENCES transport_edges(id),
    related_node_id UUID REFERENCES transport_nodes(id),
    data_json JSONB NOT NULL DEFAULT '{}',         -- type-specific payload
    validation_status validation_status NOT NULL DEFAULT 'pending',
    validated_by UUID REFERENCES users(id),
    reward_coins INTEGER NOT NULL DEFAULT 0,
    is_rewarded BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contributions_user ON contributions(user_id, created_at DESC);
CREATE INDEX idx_contributions_type ON contributions(type, validation_status);
CREATE INDEX idx_contributions_location ON contributions USING GIST(location);

-- ============================================================
-- GPS TRACKS (detailed point data for GPS contributions)
-- ============================================================

CREATE TABLE gps_tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contribution_id UUID NOT NULL REFERENCES contributions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points JSONB NOT NULL DEFAULT '[]',            -- [{lat, lng, timestamp, accuracy, speed}]
    total_points INTEGER NOT NULL DEFAULT 0,
    distance_meters FLOAT NOT NULL DEFAULT 0,
    duration_seconds FLOAT NOT NULL DEFAULT 0,
    avg_speed_kmh FLOAT,
    bounding_box GEOGRAPHY(Polygon, 4326),
    is_complete BOOLEAN NOT NULL DEFAULT false,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_gps_tracks_contribution ON gps_tracks(contribution_id);
CREATE INDEX idx_gps_tracks_user ON gps_tracks(user_id);
CREATE INDEX idx_gps_tracks_bbox ON gps_tracks USING GIST(bounding_box);

-- ============================================================
-- SMS MESSAGE LOG (for SMS fallback feature)
-- ============================================================

CREATE TABLE sms_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    msisdn VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,                -- 'inbound' or 'outbound'
    message TEXT NOT NULL,
    bdapps_request_id VARCHAR(255),
    related_query_id UUID REFERENCES route_queries(id),
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sms_msisdn ON sms_messages(msisdn, created_at DESC);

-- ============================================================
-- AUTO-UPDATE TIMESTAMPS
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_nodes_updated_at
    BEFORE UPDATE ON transport_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_edges_updated_at
    BEFORE UPDATE ON transport_edges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_wallets_updated_at
    BEFORE UPDATE ON wallets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- AUTO-CREATE WALLET ON USER INSERT
-- ============================================================

CREATE OR REPLACE FUNCTION create_user_wallet()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO wallets (user_id) VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_wallet
    AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION create_user_wallet();
