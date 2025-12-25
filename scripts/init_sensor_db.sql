-- PostgreSQL 초기화 스크립트 (센서 데이터)
-- Database: sensor_data

-- UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 센서 데이터 테이블
CREATE TABLE IF NOT EXISTS sensor_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    equipment_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_sensor_type CHECK (
        sensor_type IN ('temperature', 'pressure', 'vacuum', 'gas_flow', 'rf_power')
    )
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_type_time ON sensor_readings (sensor_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_equipment ON sensor_readings (equipment_id, sensor_type, timestamp DESC);

-- 장비 메타데이터 테이블
CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 센서 임계치 설정 테이블
CREATE TABLE IF NOT EXISTS sensor_thresholds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_type VARCHAR(50) NOT NULL,
    equipment_id VARCHAR(100),
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    warning_min DOUBLE PRECISION,
    warning_max DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (sensor_type, equipment_id)
);

-- 샘플 장비 데이터
INSERT INTO equipment (id, name, type, location) VALUES
('EQP-CVD-001', 'CVD Chamber 1', 'CVD', 'FAB1-Zone A'),
('EQP-CVD-002', 'CVD Chamber 2', 'CVD', 'FAB1-Zone A'),
('EQP-ETCH-001', 'Plasma Etcher 1', 'Etcher', 'FAB1-Zone B'),
('EQP-ETCH-002', 'Plasma Etcher 2', 'Etcher', 'FAB1-Zone B'),
('EQP-IMP-001', 'Ion Implanter 1', 'Implanter', 'FAB1-Zone C')
ON CONFLICT (id) DO NOTHING;

-- 센서 임계치 기본값
INSERT INTO sensor_thresholds (sensor_type, min_value, max_value, warning_min, warning_max) VALUES
('temperature', 0, 500, 50, 450),
('pressure', 0, 1000, 10, 900),
('vacuum', 0, 100, 5, 95),
('gas_flow', 0, 500, 10, 450),
('rf_power', 0, 5000, 100, 4500)
ON CONFLICT (sensor_type, equipment_id) DO NOTHING;

-- 샘플 센서 데이터 생성 함수
CREATE OR REPLACE FUNCTION generate_sample_sensor_data()
RETURNS void AS $$
DECLARE
    eq_id VARCHAR(100);
    sensor VARCHAR(50);
    base_value DOUBLE PRECISION;
    unit_val VARCHAR(20);
    i INTEGER;
    ts TIMESTAMPTZ;
BEGIN
    -- 각 장비에 대해 샘플 데이터 생성
    FOR eq_id IN SELECT id FROM equipment LOOP
        FOR sensor IN SELECT unnest(ARRAY['temperature', 'pressure', 'vacuum', 'gas_flow', 'rf_power']) LOOP
            -- 센서 타입별 기본값 및 단위 설정
            CASE sensor
                WHEN 'temperature' THEN base_value := 350; unit_val := '°C';
                WHEN 'pressure' THEN base_value := 500; unit_val := 'mTorr';
                WHEN 'vacuum' THEN base_value := 50; unit_val := 'Pa';
                WHEN 'gas_flow' THEN base_value := 200; unit_val := 'sccm';
                WHEN 'rf_power' THEN base_value := 2000; unit_val := 'W';
            END CASE;

            -- 최근 24시간 동안 5분 간격으로 데이터 생성
            FOR i IN 0..288 LOOP
                ts := NOW() - (i * INTERVAL '5 minutes');
                INSERT INTO sensor_readings (sensor_type, value, unit, equipment_id, timestamp)
                VALUES (
                    sensor,
                    base_value + (random() * 20 - 10),  -- ±10 랜덤 변동
                    unit_val,
                    eq_id,
                    ts
                );
            END LOOP;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 샘플 데이터 생성 실행
SELECT generate_sample_sensor_data();
