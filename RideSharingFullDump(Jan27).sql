--
-- PostgreSQL database dump
--

\restrict cDmxPLdvpaVPanmV06gzcRkkyapq3RNaCuFjlT8oOlpin13lm1fBZbIJRlJFzIs

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

-- Started on 2026-01-27 09:16:04

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 28075)
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    user_id bigint NOT NULL,
    full_name character varying(150) NOT NULL,
    phone character varying(15),
    email character varying(150),
    country_code character(2) NOT NULL,
    city_id bigint,
    gender text,
    role text NOT NULL,
    status text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 28081)
-- Name: app_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_user_user_id_seq OWNER TO postgres;

--
-- TOC entry 5501 (class 0 OID 0)
-- Dependencies: 218
-- Name: app_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_user_id_seq OWNED BY public.app_user.user_id;


--
-- TOC entry 219 (class 1259 OID 28082)
-- Name: city; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.city (
    city_id bigint NOT NULL,
    country_code character(2) NOT NULL,
    name character varying(120) NOT NULL,
    timezone character varying(50) NOT NULL,
    currency character(3) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.city OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 28086)
-- Name: city_city_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.city_city_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.city_city_id_seq OWNER TO postgres;

--
-- TOC entry 5502 (class 0 OID 0)
-- Dependencies: 220
-- Name: city_city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.city_city_id_seq OWNED BY public.city.city_id;


--
-- TOC entry 221 (class 1259 OID 28087)
-- Name: country; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.country (
    country_code character(2) NOT NULL,
    name character varying(100) NOT NULL,
    phone_code character varying(5) NOT NULL,
    default_timezone character varying(50) NOT NULL,
    default_currency character(3) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.country OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 28091)
-- Name: coupon; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coupon (
    coupon_id bigint NOT NULL,
    code character varying(50) NOT NULL,
    coupon_type text NOT NULL,
    value numeric(10,2) NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    max_uses integer,
    per_user_limit integer,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.coupon OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 28097)
-- Name: coupon_coupon_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coupon_coupon_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coupon_coupon_id_seq OWNER TO postgres;

--
-- TOC entry 5503 (class 0 OID 0)
-- Dependencies: 223
-- Name: coupon_coupon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coupon_coupon_id_seq OWNED BY public.coupon.coupon_id;


--
-- TOC entry 224 (class 1259 OID 28098)
-- Name: coupon_redemption; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coupon_redemption (
    redemption_id bigint NOT NULL,
    coupon_id bigint NOT NULL,
    user_id bigint NOT NULL,
    trip_id bigint,
    redeemed_at timestamp with time zone NOT NULL,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.coupon_redemption OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 28102)
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coupon_redemption_redemption_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coupon_redemption_redemption_id_seq OWNER TO postgres;

--
-- TOC entry 5504 (class 0 OID 0)
-- Dependencies: 225
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coupon_redemption_redemption_id_seq OWNED BY public.coupon_redemption.redemption_id;


--
-- TOC entry 226 (class 1259 OID 28103)
-- Name: coupon_tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coupon_tenant (
    coupon_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.coupon_tenant OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 28107)
-- Name: dispatch_attempt; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dispatch_attempt (
    attempt_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    responded_at timestamp with time zone,
    response text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.dispatch_attempt OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 28113)
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatch_attempt_attempt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dispatch_attempt_attempt_id_seq OWNER TO postgres;

--
-- TOC entry 5505 (class 0 OID 0)
-- Dependencies: 228
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatch_attempt_attempt_id_seq OWNED BY public.dispatch_attempt.attempt_id;


--
-- TOC entry 229 (class 1259 OID 28114)
-- Name: dispatcher_assignment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dispatcher_assignment (
    assignment_id bigint NOT NULL,
    dispatcher_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    city_id bigint,
    zone_id bigint,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.dispatcher_assignment OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 28118)
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatcher_assignment_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dispatcher_assignment_assignment_id_seq OWNER TO postgres;

--
-- TOC entry 5506 (class 0 OID 0)
-- Dependencies: 230
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatcher_assignment_assignment_id_seq OWNED BY public.dispatcher_assignment.assignment_id;


--
-- TOC entry 231 (class 1259 OID 28119)
-- Name: driver_incentive_progress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_incentive_progress (
    id bigint NOT NULL,
    scheme_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    progress_value integer DEFAULT 0 NOT NULL,
    achieved boolean DEFAULT false NOT NULL,
    updated_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.driver_incentive_progress OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 28125)
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_progress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_incentive_progress_id_seq OWNER TO postgres;

--
-- TOC entry 5507 (class 0 OID 0)
-- Dependencies: 232
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_progress_id_seq OWNED BY public.driver_incentive_progress.id;


--
-- TOC entry 233 (class 1259 OID 28126)
-- Name: driver_incentive_reward; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_incentive_reward (
    reward_id bigint NOT NULL,
    scheme_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    paid boolean DEFAULT false NOT NULL,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.driver_incentive_reward OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 28131)
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_reward_reward_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_incentive_reward_reward_id_seq OWNER TO postgres;

--
-- TOC entry 5508 (class 0 OID 0)
-- Dependencies: 234
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_reward_reward_id_seq OWNED BY public.driver_incentive_reward.reward_id;


--
-- TOC entry 235 (class 1259 OID 28132)
-- Name: driver_incentive_scheme; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_incentive_scheme (
    scheme_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    criteria jsonb NOT NULL,
    reward_amount numeric(10,2) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_incentive_scheme OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 28138)
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_scheme_scheme_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_incentive_scheme_scheme_id_seq OWNER TO postgres;

--
-- TOC entry 5509 (class 0 OID 0)
-- Dependencies: 236
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_scheme_scheme_id_seq OWNED BY public.driver_incentive_scheme.scheme_id;


--
-- TOC entry 237 (class 1259 OID 28139)
-- Name: driver_location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_location (
    driver_id bigint NOT NULL,
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL,
    last_updated timestamp with time zone NOT NULL
);


ALTER TABLE public.driver_location OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 28142)
-- Name: driver_location_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_location_history (
    id bigint NOT NULL,
    driver_id bigint NOT NULL,
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL,
    recorded_at timestamp with time zone NOT NULL
);


ALTER TABLE public.driver_location_history OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 28145)
-- Name: driver_location_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_location_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_location_history_id_seq OWNER TO postgres;

--
-- TOC entry 5510 (class 0 OID 0)
-- Dependencies: 239
-- Name: driver_location_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_location_history_id_seq OWNED BY public.driver_location_history.id;


--
-- TOC entry 240 (class 1259 OID 28146)
-- Name: driver_profile; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_profile (
    driver_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    driver_type text NOT NULL,
    approval_status text NOT NULL,
    rating numeric(3,2) DEFAULT 5.00,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone,
    alternate_phone_number character varying(15),
    allowed_vehicle_categories text[]
);


ALTER TABLE public.driver_profile OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 28153)
-- Name: driver_rating_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_rating_summary (
    driver_id bigint NOT NULL,
    avg_rating numeric(3,2),
    total_ratings integer,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_rating_summary OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 28156)
-- Name: driver_shift; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_shift (
    shift_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    status text NOT NULL,
    started_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone,
    last_latitude numeric(9,6),
    last_longitude numeric(9,6),
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_shift OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 28162)
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_shift_shift_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_shift_shift_id_seq OWNER TO postgres;

--
-- TOC entry 5511 (class 0 OID 0)
-- Dependencies: 243
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_shift_shift_id_seq OWNED BY public.driver_shift.shift_id;


--
-- TOC entry 244 (class 1259 OID 28163)
-- Name: driver_vehicle_assignment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_vehicle_assignment (
    assignment_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    vehicle_id bigint NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_vehicle_assignment OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 28167)
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_vehicle_assignment_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_vehicle_assignment_assignment_id_seq OWNER TO postgres;

--
-- TOC entry 5512 (class 0 OID 0)
-- Dependencies: 245
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_vehicle_assignment_assignment_id_seq OWNED BY public.driver_vehicle_assignment.assignment_id;


--
-- TOC entry 246 (class 1259 OID 28168)
-- Name: driver_wallet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_wallet (
    driver_id bigint NOT NULL,
    balance numeric(12,2) DEFAULT 0 NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_wallet OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 28173)
-- Name: driver_work_availability; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver_work_availability (
    id bigint NOT NULL,
    driver_id bigint NOT NULL,
    fleet_id bigint NOT NULL,
    date date NOT NULL,
    is_available boolean NOT NULL,
    note text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.driver_work_availability OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 28179)
-- Name: driver_work_availability_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_work_availability_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_work_availability_id_seq OWNER TO postgres;

--
-- TOC entry 5513 (class 0 OID 0)
-- Dependencies: 248
-- Name: driver_work_availability_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_work_availability_id_seq OWNED BY public.driver_work_availability.id;


--
-- TOC entry 249 (class 1259 OID 28180)
-- Name: fare_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fare_config (
    fare_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    city_id bigint NOT NULL,
    vehicle_category text NOT NULL,
    base_fare numeric(10,2) NOT NULL,
    per_km numeric(10,2) NOT NULL,
    per_minute numeric(10,2) NOT NULL,
    minimum_fare numeric(10,2) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.fare_config OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 28186)
-- Name: fare_config_fare_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fare_config_fare_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fare_config_fare_id_seq OWNER TO postgres;

--
-- TOC entry 5514 (class 0 OID 0)
-- Dependencies: 250
-- Name: fare_config_fare_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fare_config_fare_id_seq OWNED BY public.fare_config.fare_id;


--
-- TOC entry 251 (class 1259 OID 28187)
-- Name: fleet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet (
    fleet_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    owner_user_id bigint NOT NULL,
    fleet_name character varying(150) NOT NULL,
    status text NOT NULL,
    approval_status text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone,
    fleet_type text DEFAULT 'BUSINESS'::text NOT NULL
);


ALTER TABLE public.fleet OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 28194)
-- Name: fleet_city; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet_city (
    fleet_id bigint NOT NULL,
    city_id bigint NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.fleet_city OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 28198)
-- Name: fleet_document; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet_document (
    document_id bigint NOT NULL,
    fleet_id bigint NOT NULL,
    document_type character varying(50) NOT NULL,
    file_url text NOT NULL,
    verification_status text NOT NULL,
    verified_by bigint,
    verified_on timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.fleet_document OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 28204)
-- Name: fleet_document_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_document_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fleet_document_document_id_seq OWNER TO postgres;

--
-- TOC entry 5515 (class 0 OID 0)
-- Dependencies: 254
-- Name: fleet_document_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_document_document_id_seq OWNED BY public.fleet_document.document_id;


--
-- TOC entry 255 (class 1259 OID 28205)
-- Name: fleet_driver; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet_driver (
    id bigint NOT NULL,
    fleet_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.fleet_driver OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 28209)
-- Name: fleet_driver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_driver_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fleet_driver_id_seq OWNER TO postgres;

--
-- TOC entry 5516 (class 0 OID 0)
-- Dependencies: 256
-- Name: fleet_driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_driver_id_seq OWNED BY public.fleet_driver.id;


--
-- TOC entry 340 (class 1259 OID 28657)
-- Name: fleet_driver_invite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet_driver_invite (
    invite_id bigint NOT NULL,
    fleet_id bigint NOT NULL,
    driver_id bigint NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    invited_at timestamp with time zone DEFAULT now() NOT NULL,
    responded_at timestamp with time zone
);


ALTER TABLE public.fleet_driver_invite OWNER TO postgres;

--
-- TOC entry 339 (class 1259 OID 28656)
-- Name: fleet_driver_invite_invite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_driver_invite_invite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fleet_driver_invite_invite_id_seq OWNER TO postgres;

--
-- TOC entry 5517 (class 0 OID 0)
-- Dependencies: 339
-- Name: fleet_driver_invite_invite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_driver_invite_invite_id_seq OWNED BY public.fleet_driver_invite.invite_id;


--
-- TOC entry 257 (class 1259 OID 28210)
-- Name: fleet_fleet_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_fleet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fleet_fleet_id_seq OWNER TO postgres;

--
-- TOC entry 5518 (class 0 OID 0)
-- Dependencies: 257
-- Name: fleet_fleet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_fleet_id_seq OWNED BY public.fleet.fleet_id;


--
-- TOC entry 258 (class 1259 OID 28211)
-- Name: fleet_ledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fleet_ledger (
    entry_id bigint NOT NULL,
    fleet_id bigint NOT NULL,
    trip_id bigint,
    amount numeric(12,2) NOT NULL,
    entry_type text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.fleet_ledger OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 28217)
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fleet_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 5519 (class 0 OID 0)
-- Dependencies: 259
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_ledger_entry_id_seq OWNED BY public.fleet_ledger.entry_id;


--
-- TOC entry 260 (class 1259 OID 28218)
-- Name: lost_item_report; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lost_item_report (
    report_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    user_id bigint NOT NULL,
    description text NOT NULL,
    status character varying(50),
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.lost_item_report OWNER TO postgres;

--
-- TOC entry 261 (class 1259 OID 28224)
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lost_item_report_report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lost_item_report_report_id_seq OWNER TO postgres;

--
-- TOC entry 5520 (class 0 OID 0)
-- Dependencies: 261
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lost_item_report_report_id_seq OWNED BY public.lost_item_report.report_id;


--
-- TOC entry 262 (class 1259 OID 28225)
-- Name: lu_account_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_account_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_account_status OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 28230)
-- Name: lu_approval_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_approval_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_approval_status OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 28235)
-- Name: lu_coupon_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_coupon_type (
    type_code text NOT NULL
);


ALTER TABLE public.lu_coupon_type OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 28240)
-- Name: lu_driver_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_driver_type (
    type_code text NOT NULL
);


ALTER TABLE public.lu_driver_type OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 28245)
-- Name: lu_fleet_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_fleet_type (
    fleet_type_code text NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.lu_fleet_type OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 28250)
-- Name: lu_fuel_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_fuel_type (
    fuel_code character varying(20) NOT NULL,
    description character varying(100) NOT NULL
);


ALTER TABLE public.lu_fuel_type OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 28253)
-- Name: lu_gender; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_gender (
    gender_code text NOT NULL
);


ALTER TABLE public.lu_gender OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 28258)
-- Name: lu_payment_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_payment_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_payment_status OWNER TO postgres;

--
-- TOC entry 270 (class 1259 OID 28263)
-- Name: lu_settlement_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_settlement_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_settlement_status OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 28268)
-- Name: lu_support_ticket_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_support_ticket_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_support_ticket_status OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 28273)
-- Name: lu_tenant_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_tenant_role (
    role_code text NOT NULL
);


ALTER TABLE public.lu_tenant_role OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 28278)
-- Name: lu_trip_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_trip_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_trip_status OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 28283)
-- Name: lu_vehicle_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_vehicle_category (
    category_code text NOT NULL
);


ALTER TABLE public.lu_vehicle_category OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 28288)
-- Name: lu_vehicle_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_vehicle_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_vehicle_status OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 28293)
-- Name: payment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment (
    payment_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character(3) NOT NULL,
    payment_mode text NOT NULL,
    status text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.payment OWNER TO postgres;

--
-- TOC entry 277 (class 1259 OID 28299)
-- Name: payment_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_payment_id_seq OWNER TO postgres;

--
-- TOC entry 5521 (class 0 OID 0)
-- Dependencies: 277
-- Name: payment_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_payment_id_seq OWNED BY public.payment.payment_id;


--
-- TOC entry 278 (class 1259 OID 28300)
-- Name: platform_ledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_ledger (
    entry_id bigint NOT NULL,
    trip_id bigint,
    amount numeric(12,2) NOT NULL,
    entry_type text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.platform_ledger OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 28306)
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 5522 (class 0 OID 0)
-- Dependencies: 279
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_ledger_entry_id_seq OWNED BY public.platform_ledger.entry_id;


--
-- TOC entry 280 (class 1259 OID 28307)
-- Name: platform_wallet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_wallet (
    id smallint DEFAULT 1 NOT NULL,
    balance numeric(14,2) DEFAULT 0 NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.platform_wallet OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 28313)
-- Name: pricing_time_rule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pricing_time_rule (
    rule_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    city_id bigint NOT NULL,
    rule_type character varying(50) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    multiplier numeric(5,2) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.pricing_time_rule OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 28317)
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pricing_time_rule_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pricing_time_rule_rule_id_seq OWNER TO postgres;

--
-- TOC entry 5523 (class 0 OID 0)
-- Dependencies: 282
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pricing_time_rule_rule_id_seq OWNED BY public.pricing_time_rule.rule_id;


--
-- TOC entry 283 (class 1259 OID 28318)
-- Name: refund; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refund (
    refund_id bigint NOT NULL,
    payment_id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    reason text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.refund OWNER TO postgres;

--
-- TOC entry 284 (class 1259 OID 28324)
-- Name: refund_refund_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.refund_refund_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.refund_refund_id_seq OWNER TO postgres;

--
-- TOC entry 5524 (class 0 OID 0)
-- Dependencies: 284
-- Name: refund_refund_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.refund_refund_id_seq OWNED BY public.refund.refund_id;


--
-- TOC entry 285 (class 1259 OID 28325)
-- Name: ride_request; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ride_request (
    request_id bigint NOT NULL,
    rider_id bigint NOT NULL,
    city_id bigint NOT NULL,
    pickup_lat numeric(9,6) NOT NULL,
    pickup_lng numeric(9,6) NOT NULL,
    drop_lat numeric(9,6) NOT NULL,
    drop_lng numeric(9,6) NOT NULL,
    status text NOT NULL,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ride_request OWNER TO postgres;

--
-- TOC entry 286 (class 1259 OID 28331)
-- Name: ride_request_request_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ride_request_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ride_request_request_id_seq OWNER TO postgres;

--
-- TOC entry 5525 (class 0 OID 0)
-- Dependencies: 286
-- Name: ride_request_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ride_request_request_id_seq OWNED BY public.ride_request.request_id;


--
-- TOC entry 287 (class 1259 OID 28332)
-- Name: rider_rating_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rider_rating_summary (
    rider_id bigint NOT NULL,
    avg_rating numeric(3,2),
    total_ratings integer,
    updated_on timestamp with time zone
);


ALTER TABLE public.rider_rating_summary OWNER TO postgres;

--
-- TOC entry 288 (class 1259 OID 28335)
-- Name: sos_event; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sos_event (
    sos_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    triggered_by bigint NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    triggered_at timestamp with time zone NOT NULL,
    resolved_at timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.sos_event OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 28339)
-- Name: sos_event_sos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sos_event_sos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sos_event_sos_id_seq OWNER TO postgres;

--
-- TOC entry 5526 (class 0 OID 0)
-- Dependencies: 289
-- Name: sos_event_sos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sos_event_sos_id_seq OWNED BY public.sos_event.sos_id;


--
-- TOC entry 290 (class 1259 OID 28340)
-- Name: support_ticket; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.support_ticket (
    ticket_id bigint NOT NULL,
    user_id bigint NOT NULL,
    trip_id bigint,
    sos_id bigint,
    issue_type character varying(100),
    severity character varying(20),
    status text NOT NULL,
    assigned_to bigint,
    assigned_at timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.support_ticket OWNER TO postgres;

--
-- TOC entry 291 (class 1259 OID 28346)
-- Name: support_ticket_assignment_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.support_ticket_assignment_history (
    history_id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    assigned_to bigint,
    assigned_at timestamp with time zone NOT NULL,
    unassigned_at timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.support_ticket_assignment_history OWNER TO postgres;

--
-- TOC entry 292 (class 1259 OID 28350)
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_assignment_history_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.support_ticket_assignment_history_history_id_seq OWNER TO postgres;

--
-- TOC entry 5527 (class 0 OID 0)
-- Dependencies: 292
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_assignment_history_history_id_seq OWNED BY public.support_ticket_assignment_history.history_id;


--
-- TOC entry 293 (class 1259 OID 28351)
-- Name: support_ticket_conversation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.support_ticket_conversation (
    message_id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    sender_id bigint NOT NULL,
    message_text text NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.support_ticket_conversation OWNER TO postgres;

--
-- TOC entry 294 (class 1259 OID 28357)
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_conversation_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.support_ticket_conversation_message_id_seq OWNER TO postgres;

--
-- TOC entry 5528 (class 0 OID 0)
-- Dependencies: 294
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_conversation_message_id_seq OWNED BY public.support_ticket_conversation.message_id;


--
-- TOC entry 295 (class 1259 OID 28358)
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.support_ticket_ticket_id_seq OWNER TO postgres;

--
-- TOC entry 5529 (class 0 OID 0)
-- Dependencies: 295
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_ticket_id_seq OWNED BY public.support_ticket.ticket_id;


--
-- TOC entry 296 (class 1259 OID 28359)
-- Name: surge_event; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.surge_event (
    surge_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    surge_zone_id bigint NOT NULL,
    multiplier numeric(5,2) NOT NULL,
    demand_index integer,
    supply_index integer,
    started_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.surge_event OWNER TO postgres;

--
-- TOC entry 297 (class 1259 OID 28363)
-- Name: surge_event_surge_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.surge_event_surge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.surge_event_surge_id_seq OWNER TO postgres;

--
-- TOC entry 5530 (class 0 OID 0)
-- Dependencies: 297
-- Name: surge_event_surge_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.surge_event_surge_id_seq OWNED BY public.surge_event.surge_id;


--
-- TOC entry 298 (class 1259 OID 28364)
-- Name: surge_zone; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.surge_zone (
    surge_zone_id bigint NOT NULL,
    zone_id bigint NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.surge_zone OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 28368)
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.surge_zone_surge_zone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.surge_zone_surge_zone_id_seq OWNER TO postgres;

--
-- TOC entry 5531 (class 0 OID 0)
-- Dependencies: 299
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.surge_zone_surge_zone_id_seq OWNED BY public.surge_zone.surge_zone_id;


--
-- TOC entry 300 (class 1259 OID 28369)
-- Name: tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant (
    tenant_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    default_currency character(3) NOT NULL,
    default_timezone character varying(50) NOT NULL,
    status text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone,
    tenant_code character varying(50) NOT NULL
);


ALTER TABLE public.tenant OWNER TO postgres;

--
-- TOC entry 301 (class 1259 OID 28375)
-- Name: tenant_admin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_admin (
    tenant_admin_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    user_id bigint NOT NULL,
    is_primary boolean DEFAULT false,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_admin OWNER TO postgres;

--
-- TOC entry 302 (class 1259 OID 28380)
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_admin_tenant_admin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_admin_tenant_admin_id_seq OWNER TO postgres;

--
-- TOC entry 5532 (class 0 OID 0)
-- Dependencies: 302
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_admin_tenant_admin_id_seq OWNED BY public.tenant_admin.tenant_admin_id;


--
-- TOC entry 303 (class 1259 OID 28381)
-- Name: tenant_city; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_city (
    tenant_id bigint NOT NULL,
    city_id bigint NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_city OWNER TO postgres;

--
-- TOC entry 304 (class 1259 OID 28385)
-- Name: tenant_country; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_country (
    tenant_id bigint NOT NULL,
    country_code character(2) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_country OWNER TO postgres;

--
-- TOC entry 305 (class 1259 OID 28389)
-- Name: tenant_document; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_document (
    tenant_document_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    document_type character varying(50) NOT NULL,
    file_name text NOT NULL,
    file_url text NOT NULL,
    file_hash text,
    is_active boolean DEFAULT true,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenant_document OWNER TO postgres;

--
-- TOC entry 306 (class 1259 OID 28396)
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_document_tenant_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_document_tenant_document_id_seq OWNER TO postgres;

--
-- TOC entry 5533 (class 0 OID 0)
-- Dependencies: 306
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_document_tenant_document_id_seq OWNED BY public.tenant_document.tenant_document_id;


--
-- TOC entry 307 (class 1259 OID 28397)
-- Name: tenant_ledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_ledger (
    entry_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    trip_id bigint,
    amount numeric(12,2) NOT NULL,
    entry_type text NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenant_ledger OWNER TO postgres;

--
-- TOC entry 308 (class 1259 OID 28403)
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 5534 (class 0 OID 0)
-- Dependencies: 308
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_ledger_entry_id_seq OWNED BY public.tenant_ledger.entry_id;


--
-- TOC entry 309 (class 1259 OID 28404)
-- Name: tenant_rating_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_rating_summary (
    tenant_id bigint NOT NULL,
    avg_rating numeric(3,2),
    total_ratings integer,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_rating_summary OWNER TO postgres;

--
-- TOC entry 310 (class 1259 OID 28407)
-- Name: tenant_settlement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_settlement (
    settlement_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    amount numeric(12,2) NOT NULL,
    status text NOT NULL,
    requested_at timestamp with time zone NOT NULL,
    processed_at timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_settlement OWNER TO postgres;

--
-- TOC entry 311 (class 1259 OID 28413)
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_settlement_settlement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_settlement_settlement_id_seq OWNER TO postgres;

--
-- TOC entry 5535 (class 0 OID 0)
-- Dependencies: 311
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_settlement_settlement_id_seq OWNED BY public.tenant_settlement.settlement_id;


--
-- TOC entry 312 (class 1259 OID 28414)
-- Name: tenant_tax_rule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_tax_rule (
    tax_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    country_code character(2) NOT NULL,
    tax_type character varying(50),
    rate numeric(5,2) NOT NULL,
    effective_from timestamp with time zone NOT NULL,
    effective_to timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true
);


ALTER TABLE public.tenant_tax_rule OWNER TO postgres;

--
-- TOC entry 313 (class 1259 OID 28419)
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_tax_rule_tax_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_tax_rule_tax_id_seq OWNER TO postgres;

--
-- TOC entry 5536 (class 0 OID 0)
-- Dependencies: 313
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_tax_rule_tax_id_seq OWNED BY public.tenant_tax_rule.tax_id;


--
-- TOC entry 314 (class 1259 OID 28420)
-- Name: tenant_tenant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_tenant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tenant_tenant_id_seq OWNER TO postgres;

--
-- TOC entry 5537 (class 0 OID 0)
-- Dependencies: 314
-- Name: tenant_tenant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_tenant_id_seq OWNED BY public.tenant.tenant_id;


--
-- TOC entry 315 (class 1259 OID 28421)
-- Name: tenant_wallet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_wallet (
    tenant_id bigint NOT NULL,
    balance numeric(12,2) DEFAULT 0 NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.tenant_wallet OWNER TO postgres;

--
-- TOC entry 316 (class 1259 OID 28426)
-- Name: trip; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip (
    trip_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    rider_id bigint NOT NULL,
    driver_id bigint,
    vehicle_id bigint,
    city_id bigint NOT NULL,
    zone_id bigint,
    pickup_lat numeric(9,6) NOT NULL,
    pickup_lng numeric(9,6) NOT NULL,
    drop_lat numeric(9,6),
    drop_lng numeric(9,6),
    status text NOT NULL,
    requested_at timestamp with time zone DEFAULT now() NOT NULL,
    assigned_at timestamp with time zone,
    picked_up_at timestamp with time zone,
    completed_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    fare_amount numeric(10,2),
    driver_earning numeric(10,2),
    platform_fee numeric(10,2),
    payment_status text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.trip OWNER TO postgres;

--
-- TOC entry 317 (class 1259 OID 28433)
-- Name: trip_cancellation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_cancellation (
    cancel_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    cancelled_by bigint NOT NULL,
    reason text,
    cancelled_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trip_cancellation OWNER TO postgres;

--
-- TOC entry 318 (class 1259 OID 28439)
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_cancellation_cancel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_cancellation_cancel_id_seq OWNER TO postgres;

--
-- TOC entry 5538 (class 0 OID 0)
-- Dependencies: 318
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_cancellation_cancel_id_seq OWNED BY public.trip_cancellation.cancel_id;


--
-- TOC entry 319 (class 1259 OID 28440)
-- Name: trip_fare_breakdown; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_fare_breakdown (
    id bigint NOT NULL,
    trip_id bigint NOT NULL,
    base_fare numeric(10,2),
    distance_fare numeric(10,2),
    time_fare numeric(10,2),
    surge_amount numeric(10,2),
    night_charge numeric(10,2),
    tax_amount numeric(10,2),
    discount_amount numeric(10,2),
    final_fare numeric(10,2) NOT NULL,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trip_fare_breakdown OWNER TO postgres;

--
-- TOC entry 320 (class 1259 OID 28444)
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_fare_breakdown_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_fare_breakdown_id_seq OWNER TO postgres;

--
-- TOC entry 5539 (class 0 OID 0)
-- Dependencies: 320
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_fare_breakdown_id_seq OWNED BY public.trip_fare_breakdown.id;


--
-- TOC entry 321 (class 1259 OID 28445)
-- Name: trip_otp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_otp (
    otp_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    otp_code character varying(10) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    verified boolean DEFAULT false NOT NULL,
    created_on timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trip_otp OWNER TO postgres;

--
-- TOC entry 322 (class 1259 OID 28450)
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_otp_otp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_otp_otp_id_seq OWNER TO postgres;

--
-- TOC entry 5540 (class 0 OID 0)
-- Dependencies: 322
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_otp_otp_id_seq OWNED BY public.trip_otp.otp_id;


--
-- TOC entry 323 (class 1259 OID 28451)
-- Name: trip_rating; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_rating (
    rating_id bigint NOT NULL,
    trip_id bigint NOT NULL,
    rater_id bigint NOT NULL,
    ratee_id bigint NOT NULL,
    rating integer,
    comment text,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT trip_rating_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.trip_rating OWNER TO postgres;

--
-- TOC entry 324 (class 1259 OID 28458)
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_rating_rating_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_rating_rating_id_seq OWNER TO postgres;

--
-- TOC entry 5541 (class 0 OID 0)
-- Dependencies: 324
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_rating_rating_id_seq OWNED BY public.trip_rating.rating_id;


--
-- TOC entry 325 (class 1259 OID 28459)
-- Name: trip_route_point; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip_route_point (
    id bigint NOT NULL,
    trip_id bigint NOT NULL,
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL,
    recorded_at timestamp with time zone NOT NULL
);


ALTER TABLE public.trip_route_point OWNER TO postgres;

--
-- TOC entry 326 (class 1259 OID 28462)
-- Name: trip_route_point_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_route_point_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_route_point_id_seq OWNER TO postgres;

--
-- TOC entry 5542 (class 0 OID 0)
-- Dependencies: 326
-- Name: trip_route_point_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_route_point_id_seq OWNED BY public.trip_route_point.id;


--
-- TOC entry 327 (class 1259 OID 28463)
-- Name: trip_trip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_trip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_trip_id_seq OWNER TO postgres;

--
-- TOC entry 5543 (class 0 OID 0)
-- Dependencies: 327
-- Name: trip_trip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_trip_id_seq OWNED BY public.trip.trip_id;


--
-- TOC entry 328 (class 1259 OID 28464)
-- Name: user_auth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_auth (
    user_id bigint NOT NULL,
    password_hash character varying NOT NULL,
    is_locked boolean NOT NULL,
    last_password_change timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.user_auth OWNER TO postgres;

--
-- TOC entry 329 (class 1259 OID 28470)
-- Name: user_kyc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_kyc (
    kyc_id bigint NOT NULL,
    user_id bigint NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(100) NOT NULL,
    verification_status text NOT NULL,
    verified_by bigint,
    verified_on timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone,
    file_url text
);


ALTER TABLE public.user_kyc OWNER TO postgres;

--
-- TOC entry 330 (class 1259 OID 28476)
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_kyc_kyc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_kyc_kyc_id_seq OWNER TO postgres;

--
-- TOC entry 5544 (class 0 OID 0)
-- Dependencies: 330
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_kyc_kyc_id_seq OWNED BY public.user_kyc.kyc_id;


--
-- TOC entry 331 (class 1259 OID 28477)
-- Name: user_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_session (
    session_id uuid NOT NULL,
    user_id bigint NOT NULL,
    login_at timestamp with time zone DEFAULT now() NOT NULL,
    logout_at timestamp with time zone,
    ip_address inet,
    user_agent text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.user_session OWNER TO postgres;

--
-- TOC entry 332 (class 1259 OID 28484)
-- Name: vehicle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle (
    vehicle_id bigint NOT NULL,
    tenant_id bigint NOT NULL,
    fleet_id bigint,
    category text NOT NULL,
    status text NOT NULL,
    registration_no character varying(50) NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone,
    approval_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    CONSTRAINT vehicle_approval_status_check CHECK (((approval_status)::text = ANY ((ARRAY['PENDING'::character varying, 'APPROVED'::character varying, 'REJECTED'::character varying])::text[])))
);


ALTER TABLE public.vehicle OWNER TO postgres;

--
-- TOC entry 333 (class 1259 OID 28490)
-- Name: vehicle_document; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle_document (
    document_id bigint NOT NULL,
    vehicle_id bigint NOT NULL,
    document_type character varying(50) NOT NULL,
    file_url text NOT NULL,
    verification_status text NOT NULL,
    verified_by bigint,
    verified_on timestamp with time zone,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.vehicle_document OWNER TO postgres;

--
-- TOC entry 334 (class 1259 OID 28496)
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_document_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_document_document_id_seq OWNER TO postgres;

--
-- TOC entry 5545 (class 0 OID 0)
-- Dependencies: 334
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_document_document_id_seq OWNED BY public.vehicle_document.document_id;


--
-- TOC entry 335 (class 1259 OID 28497)
-- Name: vehicle_spec; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle_spec (
    vehicle_id bigint NOT NULL,
    manufacturer character varying(100) NOT NULL,
    model_name character varying(100) NOT NULL,
    manufacture_year integer NOT NULL,
    fuel_type character varying(20) NOT NULL,
    seating_capacity integer NOT NULL,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.vehicle_spec OWNER TO postgres;

--
-- TOC entry 336 (class 1259 OID 28501)
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_vehicle_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_vehicle_id_seq OWNER TO postgres;

--
-- TOC entry 5546 (class 0 OID 0)
-- Dependencies: 336
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_vehicle_id_seq OWNED BY public.vehicle.vehicle_id;


--
-- TOC entry 337 (class 1259 OID 28502)
-- Name: zone; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zone (
    zone_id bigint NOT NULL,
    city_id bigint NOT NULL,
    name character varying(120) NOT NULL,
    center_lat numeric(9,6),
    center_lng numeric(9,6),
    boundary text,
    created_by bigint,
    created_on timestamp with time zone DEFAULT now() NOT NULL,
    updated_by bigint,
    updated_on timestamp with time zone
);


ALTER TABLE public.zone OWNER TO postgres;

--
-- TOC entry 338 (class 1259 OID 28508)
-- Name: zone_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zone_zone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zone_zone_id_seq OWNER TO postgres;

--
-- TOC entry 5547 (class 0 OID 0)
-- Dependencies: 338
-- Name: zone_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zone_zone_id_seq OWNED BY public.zone.zone_id;


--
-- TOC entry 5092 (class 2604 OID 28509)
-- Name: app_user user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN user_id SET DEFAULT nextval('public.app_user_user_id_seq'::regclass);


--
-- TOC entry 5094 (class 2604 OID 28510)
-- Name: city city_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.city ALTER COLUMN city_id SET DEFAULT nextval('public.city_city_id_seq'::regclass);


--
-- TOC entry 5097 (class 2604 OID 28511)
-- Name: coupon coupon_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coupon ALTER COLUMN coupon_id SET DEFAULT nextval('public.coupon_coupon_id_seq'::regclass);


--
-- TOC entry 5099 (class 2604 OID 28512)
-- Name: coupon_redemption redemption_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coupon_redemption ALTER COLUMN redemption_id SET DEFAULT nextval('public.coupon_redemption_redemption_id_seq'::regclass);


--
-- TOC entry 5102 (class 2604 OID 28513)
-- Name: dispatch_attempt attempt_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_attempt ALTER COLUMN attempt_id SET DEFAULT nextval('public.dispatch_attempt_attempt_id_seq'::regclass);


--
-- TOC entry 5104 (class 2604 OID 28514)
-- Name: dispatcher_assignment assignment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatcher_assignment ALTER COLUMN assignment_id SET DEFAULT nextval('public.dispatcher_assignment_assignment_id_seq'::regclass);


--
-- TOC entry 5106 (class 2604 OID 28515)
-- Name: driver_incentive_progress id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_progress ALTER COLUMN id SET DEFAULT nextval('public.driver_incentive_progress_id_seq'::regclass);


--
-- TOC entry 5110 (class 2604 OID 28516)
-- Name: driver_incentive_reward reward_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_reward ALTER COLUMN reward_id SET DEFAULT nextval('public.driver_incentive_reward_reward_id_seq'::regclass);


--
-- TOC entry 5113 (class 2604 OID 28517)
-- Name: driver_incentive_scheme scheme_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_scheme ALTER COLUMN scheme_id SET DEFAULT nextval('public.driver_incentive_scheme_scheme_id_seq'::regclass);


--
-- TOC entry 5115 (class 2604 OID 28518)
-- Name: driver_location_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_location_history ALTER COLUMN id SET DEFAULT nextval('public.driver_location_history_id_seq'::regclass);


--
-- TOC entry 5118 (class 2604 OID 28519)
-- Name: driver_shift shift_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_shift ALTER COLUMN shift_id SET DEFAULT nextval('public.driver_shift_shift_id_seq'::regclass);


--
-- TOC entry 5120 (class 2604 OID 28520)
-- Name: driver_vehicle_assignment assignment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_vehicle_assignment ALTER COLUMN assignment_id SET DEFAULT nextval('public.driver_vehicle_assignment_assignment_id_seq'::regclass);


--
-- TOC entry 5124 (class 2604 OID 28521)
-- Name: driver_work_availability id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_work_availability ALTER COLUMN id SET DEFAULT nextval('public.driver_work_availability_id_seq'::regclass);


--
-- TOC entry 5126 (class 2604 OID 28522)
-- Name: fare_config fare_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fare_config ALTER COLUMN fare_id SET DEFAULT nextval('public.fare_config_fare_id_seq'::regclass);


--
-- TOC entry 5128 (class 2604 OID 28523)
-- Name: fleet fleet_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet ALTER COLUMN fleet_id SET DEFAULT nextval('public.fleet_fleet_id_seq'::regclass);


--
-- TOC entry 5132 (class 2604 OID 28524)
-- Name: fleet_document document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_document ALTER COLUMN document_id SET DEFAULT nextval('public.fleet_document_document_id_seq'::regclass);


--
-- TOC entry 5134 (class 2604 OID 28525)
-- Name: fleet_driver id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver ALTER COLUMN id SET DEFAULT nextval('public.fleet_driver_id_seq'::regclass);


--
-- TOC entry 5210 (class 2604 OID 28660)
-- Name: fleet_driver_invite invite_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver_invite ALTER COLUMN invite_id SET DEFAULT nextval('public.fleet_driver_invite_invite_id_seq'::regclass);


--
-- TOC entry 5136 (class 2604 OID 28526)
-- Name: fleet_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.fleet_ledger_entry_id_seq'::regclass);


--
-- TOC entry 5138 (class 2604 OID 28527)
-- Name: lost_item_report report_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lost_item_report ALTER COLUMN report_id SET DEFAULT nextval('public.lost_item_report_report_id_seq'::regclass);


--
-- TOC entry 5140 (class 2604 OID 28528)
-- Name: payment payment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment ALTER COLUMN payment_id SET DEFAULT nextval('public.payment_payment_id_seq'::regclass);


--
-- TOC entry 5142 (class 2604 OID 28529)
-- Name: platform_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.platform_ledger_entry_id_seq'::regclass);


--
-- TOC entry 5147 (class 2604 OID 28530)
-- Name: pricing_time_rule rule_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pricing_time_rule ALTER COLUMN rule_id SET DEFAULT nextval('public.pricing_time_rule_rule_id_seq'::regclass);


--
-- TOC entry 5149 (class 2604 OID 28531)
-- Name: refund refund_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refund ALTER COLUMN refund_id SET DEFAULT nextval('public.refund_refund_id_seq'::regclass);


--
-- TOC entry 5151 (class 2604 OID 28532)
-- Name: ride_request request_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ride_request ALTER COLUMN request_id SET DEFAULT nextval('public.ride_request_request_id_seq'::regclass);


--
-- TOC entry 5153 (class 2604 OID 28533)
-- Name: sos_event sos_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sos_event ALTER COLUMN sos_id SET DEFAULT nextval('public.sos_event_sos_id_seq'::regclass);


--
-- TOC entry 5155 (class 2604 OID 28534)
-- Name: support_ticket ticket_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket ALTER COLUMN ticket_id SET DEFAULT nextval('public.support_ticket_ticket_id_seq'::regclass);


--
-- TOC entry 5157 (class 2604 OID 28535)
-- Name: support_ticket_assignment_history history_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket_assignment_history ALTER COLUMN history_id SET DEFAULT nextval('public.support_ticket_assignment_history_history_id_seq'::regclass);


--
-- TOC entry 5159 (class 2604 OID 28536)
-- Name: support_ticket_conversation message_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket_conversation ALTER COLUMN message_id SET DEFAULT nextval('public.support_ticket_conversation_message_id_seq'::regclass);


--
-- TOC entry 5161 (class 2604 OID 28537)
-- Name: surge_event surge_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surge_event ALTER COLUMN surge_id SET DEFAULT nextval('public.surge_event_surge_id_seq'::regclass);


--
-- TOC entry 5163 (class 2604 OID 28538)
-- Name: surge_zone surge_zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surge_zone ALTER COLUMN surge_zone_id SET DEFAULT nextval('public.surge_zone_surge_zone_id_seq'::regclass);


--
-- TOC entry 5165 (class 2604 OID 28539)
-- Name: tenant tenant_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant ALTER COLUMN tenant_id SET DEFAULT nextval('public.tenant_tenant_id_seq'::regclass);


--
-- TOC entry 5167 (class 2604 OID 28540)
-- Name: tenant_admin tenant_admin_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_admin ALTER COLUMN tenant_admin_id SET DEFAULT nextval('public.tenant_admin_tenant_admin_id_seq'::regclass);


--
-- TOC entry 5172 (class 2604 OID 28541)
-- Name: tenant_document tenant_document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_document ALTER COLUMN tenant_document_id SET DEFAULT nextval('public.tenant_document_tenant_document_id_seq'::regclass);


--
-- TOC entry 5175 (class 2604 OID 28542)
-- Name: tenant_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.tenant_ledger_entry_id_seq'::regclass);


--
-- TOC entry 5177 (class 2604 OID 28543)
-- Name: tenant_settlement settlement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_settlement ALTER COLUMN settlement_id SET DEFAULT nextval('public.tenant_settlement_settlement_id_seq'::regclass);


--
-- TOC entry 5179 (class 2604 OID 28544)
-- Name: tenant_tax_rule tax_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_tax_rule ALTER COLUMN tax_id SET DEFAULT nextval('public.tenant_tax_rule_tax_id_seq'::regclass);


--
-- TOC entry 5184 (class 2604 OID 28545)
-- Name: trip trip_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip ALTER COLUMN trip_id SET DEFAULT nextval('public.trip_trip_id_seq'::regclass);


--
-- TOC entry 5187 (class 2604 OID 28546)
-- Name: trip_cancellation cancel_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_cancellation ALTER COLUMN cancel_id SET DEFAULT nextval('public.trip_cancellation_cancel_id_seq'::regclass);


--
-- TOC entry 5189 (class 2604 OID 28547)
-- Name: trip_fare_breakdown id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_fare_breakdown ALTER COLUMN id SET DEFAULT nextval('public.trip_fare_breakdown_id_seq'::regclass);


--
-- TOC entry 5191 (class 2604 OID 28548)
-- Name: trip_otp otp_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_otp ALTER COLUMN otp_id SET DEFAULT nextval('public.trip_otp_otp_id_seq'::regclass);


--
-- TOC entry 5194 (class 2604 OID 28549)
-- Name: trip_rating rating_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_rating ALTER COLUMN rating_id SET DEFAULT nextval('public.trip_rating_rating_id_seq'::regclass);


--
-- TOC entry 5196 (class 2604 OID 28550)
-- Name: trip_route_point id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_route_point ALTER COLUMN id SET DEFAULT nextval('public.trip_route_point_id_seq'::regclass);


--
-- TOC entry 5198 (class 2604 OID 28551)
-- Name: user_kyc kyc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_kyc ALTER COLUMN kyc_id SET DEFAULT nextval('public.user_kyc_kyc_id_seq'::regclass);


--
-- TOC entry 5202 (class 2604 OID 28552)
-- Name: vehicle vehicle_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN vehicle_id SET DEFAULT nextval('public.vehicle_vehicle_id_seq'::regclass);


--
-- TOC entry 5205 (class 2604 OID 28553)
-- Name: vehicle_document document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_document ALTER COLUMN document_id SET DEFAULT nextval('public.vehicle_document_document_id_seq'::regclass);


--
-- TOC entry 5208 (class 2604 OID 28554)
-- Name: zone zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone ALTER COLUMN zone_id SET DEFAULT nextval('public.zone_zone_id_seq'::regclass);


--
-- TOC entry 5372 (class 0 OID 28075)
-- Dependencies: 217
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (user_id, full_name, phone, email, country_code, city_id, gender, role, status, created_by, created_on, updated_by, updated_on) FROM stdin;
1	Platform Admin	\N	admin@test.com	IN	\N	\N	PLATFORM_ADMIN	ACTIVE	\N	2026-01-14 12:24:30.318588+05:30	\N	\N
2	Dummy_Rider1	\N	rider1@test.com	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-14 13:25:47.123617+05:30	\N	\N
3	TenantAdmin	\N	tenantadmin@test.com	IN	1	\N	TENANT_ADMIN	ACTIVE	\N	2026-01-19 11:27:59.05167+05:30	\N	\N
9	Rider A	\N	ridera@test.com	IN	1	\N	RIDER	ACTIVE	\N	2026-01-19 11:35:14.928646+05:30	\N	\N
11	Rider C	\N	riderc@test.com	IN	1	\N	RIDER	ACTIVE	\N	2026-01-19 11:37:06.027042+05:30	\N	\N
10	Rider B	\N	riderb@test.com	IN	1	\N	RIDER	ACTIVE	\N	2026-01-19 11:36:05.282577+05:30	\N	2026-01-19 12:30:35.604389+05:30
4	Test Driver	\N	driver@test.com	IN	1	\N	DRIVER	ACTIVE	\N	2026-01-19 11:30:46.774878+05:30	\N	\N
6	Test Driver1	\N	driverone@test.com	IN	1	\N	DRIVER	ACTIVE	\N	2026-01-19 11:31:24.062301+05:30	\N	\N
7	Test Driver2	\N	drivertwo@test.com	IN	1	\N	DRIVER	ACTIVE	\N	2026-01-19 11:31:42.462434+05:30	\N	\N
8	Test Driver3	\N	driverthree@test.com	IN	1	\N	DRIVER	ACTIVE	\N	2026-01-19 11:33:47.871949+05:30	\N	\N
13	Test Driver4	9000000001	driver4@test.com	IN	1	\N	DRIVER	INACTIVE	\N	2026-01-20 14:58:57.429009+05:30	\N	\N
14	User 8062	+918498858062	\N	IN	\N	\N	DRIVER	ACTIVE	\N	2026-01-21 17:09:09.182405+05:30	\N	\N
15	User 8063	+918498858063	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-21 18:56:12.691585+05:30	\N	\N
16	User 8061	+918498858061	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-24 18:30:21.008212+05:30	\N	\N
17	Tejaswi	\N	tenantadmin2@test.com	IN	\N	\N	TENANT_ADMIN	ACTIVE	\N	2026-01-25 00:42:16.359176+05:30	\N	2026-01-25 00:42:16.359176+05:30
18	User 8060	+918498858060	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-25 09:45:50.981396+05:30	\N	\N
20	User 8069	+918498858069	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-26 00:32:33.032806+05:30	\N	\N
22	User 9723	+919705939723	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-26 13:23:30.83766+05:30	\N	\N
21	Radhika	+919705939724	\N	IN	1	FEMALE	RIDER	ACTIVE	\N	2026-01-26 10:19:35.679989+05:30	\N	2026-01-26 16:26:37.942363+05:30
23	User 8067	+918498858067	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-26 23:31:34.191777+05:30	\N	\N
24	User 8065	+918498858065	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-26 23:32:38.170226+05:30	\N	\N
25	User 1130	+919966451130	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-26 23:56:18.000127+05:30	\N	\N
26	User 8042	+918498858042	\N	IN	\N	\N	RIDER	ACTIVE	\N	2026-01-27 00:08:00.274142+05:30	\N	\N
19	User 8066	+918498858066	tenant5admin@test.com	IN	\N	\N	TENANT_ADMIN	ACTIVE	\N	2026-01-26 00:17:35.61024+05:30	\N	\N
\.


--
-- TOC entry 5374 (class 0 OID 28082)
-- Dependencies: 219
-- Data for Name: city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.city (city_id, country_code, name, timezone, currency, created_by, created_on, updated_by, updated_on) FROM stdin;
1	IN	Hyderabad	Asia/Kolkata	INR	\N	2026-01-13 16:16:53.621268+05:30	\N	\N
\.


--
-- TOC entry 5376 (class 0 OID 28087)
-- Dependencies: 221
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.country (country_code, name, phone_code, default_timezone, default_currency, created_by, created_on, updated_by, updated_on) FROM stdin;
IN	India	+91	Asia/Kolkata	INR	\N	2026-01-13 16:15:27.367924+05:30	\N	\N
\.


--
-- TOC entry 5377 (class 0 OID 28091)
-- Dependencies: 222
-- Data for Name: coupon; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon (coupon_id, code, coupon_type, value, start_date, end_date, max_uses, per_user_limit, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5379 (class 0 OID 28098)
-- Dependencies: 224
-- Data for Name: coupon_redemption; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon_redemption (redemption_id, coupon_id, user_id, trip_id, redeemed_at, created_on) FROM stdin;
\.


--
-- TOC entry 5381 (class 0 OID 28103)
-- Dependencies: 226
-- Data for Name: coupon_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon_tenant (coupon_id, tenant_id, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5382 (class 0 OID 28107)
-- Dependencies: 227
-- Data for Name: dispatch_attempt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dispatch_attempt (attempt_id, trip_id, driver_id, sent_at, responded_at, response, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	4	2026-01-19 16:45:16.498276+05:30	\N	SENT	9	2026-01-19 16:45:16.466253+05:30	\N	\N
\.


--
-- TOC entry 5384 (class 0 OID 28114)
-- Dependencies: 229
-- Data for Name: dispatcher_assignment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dispatcher_assignment (assignment_id, dispatcher_id, tenant_id, city_id, zone_id, start_time, end_time, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5386 (class 0 OID 28119)
-- Dependencies: 231
-- Data for Name: driver_incentive_progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_progress (id, scheme_id, driver_id, progress_value, achieved, updated_on) FROM stdin;
\.


--
-- TOC entry 5388 (class 0 OID 28126)
-- Dependencies: 233
-- Data for Name: driver_incentive_reward; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_reward (reward_id, scheme_id, driver_id, amount, paid, created_on) FROM stdin;
\.


--
-- TOC entry 5390 (class 0 OID 28132)
-- Dependencies: 235
-- Data for Name: driver_incentive_scheme; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_scheme (scheme_id, tenant_id, name, description, start_date, end_date, criteria, reward_amount, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5392 (class 0 OID 28139)
-- Dependencies: 237
-- Data for Name: driver_location; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_location (driver_id, latitude, longitude, last_updated) FROM stdin;
4	12.970000	77.980000	2026-01-19 16:27:05.501587+05:30
\.


--
-- TOC entry 5393 (class 0 OID 28142)
-- Dependencies: 238
-- Data for Name: driver_location_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_location_history (id, driver_id, latitude, longitude, recorded_at) FROM stdin;
\.


--
-- TOC entry 5395 (class 0 OID 28146)
-- Dependencies: 240
-- Data for Name: driver_profile; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_profile (driver_id, tenant_id, driver_type, approval_status, rating, created_by, created_on, updated_by, updated_on, alternate_phone_number, allowed_vehicle_categories) FROM stdin;
4	1	INDEPENDENT	APPROVED	4.90	\N	2026-01-19 16:04:12.748309+05:30	\N	\N	\N	\N
6	1	INDEPENDENT	APPROVED	5.00	6	2026-01-20 15:54:01.245159+05:30	\N	2026-01-22 10:55:45.141912+05:30	\N	{"CAR,BIKE"}
7	1	INDEPENDENT	REJECTED	5.00	7	2026-01-19 18:24:41.475404+05:30	\N	2026-01-22 10:58:29.647204+05:30	\N	\N
14	1	INDEPENDENT	REJECTED	5.00	14	2026-01-21 18:53:57.947313+05:30	\N	2026-01-24 12:32:12.700064+05:30	+919876543210	\N
15	1	INDEPENDENT	APPROVED	5.00	15	2026-01-21 19:03:06.318396+05:30	\N	2026-01-24 12:34:16.259646+05:30	\N	{BIKE,AUTO}
18	1	INDEPENDENT	APPROVED	5.00	18	2026-01-25 23:04:44.060701+05:30	\N	2026-01-25 23:54:26.535492+05:30	\N	{AUTO,BIKE}
19	1	INDEPENDENT	APPROVED	5.00	19	2026-01-26 00:18:51.729838+05:30	\N	2026-01-26 00:19:38.659271+05:30	\N	{AUTO,CAR}
20	1	INDEPENDENT	APPROVED	5.00	20	2026-01-26 00:33:24.267883+05:30	\N	2026-01-26 00:33:50.316487+05:30	\N	{AUTO}
21	1	INDEPENDENT	APPROVED	5.00	21	2026-01-26 12:55:22.85735+05:30	\N	2026-01-26 13:20:59.561375+05:30	\N	{CAR,AUTO}
16	1	INDEPENDENT	APPROVED	5.00	16	2026-01-26 14:46:38.863393+05:30	\N	2026-01-26 14:46:55.989547+05:30	\N	{CAR}
22	1	INDEPENDENT	APPROVED	5.00	22	2026-01-26 19:29:31.394945+05:30	\N	2026-01-26 19:32:42.474021+05:30	\N	{AUTO,BIKE}
24	1	INDEPENDENT	PENDING	5.00	24	2026-01-26 23:33:47.696013+05:30	\N	\N	\N	\N
25	1	INDEPENDENT	PENDING	5.00	25	2026-01-26 23:57:06.210027+05:30	\N	\N	\N	\N
26	5	INDEPENDENT	APPROVED	5.00	26	2026-01-27 00:09:57.121722+05:30	\N	2026-01-27 00:25:22.008822+05:30	\N	{CAR,AUTO}
\.


--
-- TOC entry 5396 (class 0 OID 28153)
-- Dependencies: 241
-- Data for Name: driver_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_rating_summary (driver_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 5397 (class 0 OID 28156)
-- Dependencies: 242
-- Data for Name: driver_shift; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_shift (shift_id, driver_id, tenant_id, status, started_at, ended_at, last_latitude, last_longitude, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	1	ACTIVE	2026-01-19 16:22:19.462453+05:30	\N	12.970000	77.980000	\N	2026-01-19 16:22:19.462453+05:30	\N	\N
\.


--
-- TOC entry 5399 (class 0 OID 28163)
-- Dependencies: 244
-- Data for Name: driver_vehicle_assignment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_vehicle_assignment (assignment_id, driver_id, vehicle_id, start_time, end_time, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	2	2026-01-19 16:11:49.441969+05:30	\N	\N	2026-01-19 16:11:49.441969+05:30	\N	\N
\.


--
-- TOC entry 5401 (class 0 OID 28168)
-- Dependencies: 246
-- Data for Name: driver_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_wallet (driver_id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5402 (class 0 OID 28173)
-- Dependencies: 247
-- Data for Name: driver_work_availability; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_work_availability (id, driver_id, fleet_id, date, is_available, note, created_by, created_on, updated_by, updated_on) FROM stdin;
1	16	2	2026-01-26	t	string	16	2026-01-26 17:44:21.24052+05:30	16	2026-01-26 17:45:31.338971+05:30
\.


--
-- TOC entry 5404 (class 0 OID 28180)
-- Dependencies: 249
-- Data for Name: fare_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fare_config (fare_id, tenant_id, city_id, vehicle_category, base_fare, per_km, per_minute, minimum_fare, created_by, created_on, updated_by, updated_on) FROM stdin;
1	1	1	BIKE	30.00	12.00	1.00	50.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
2	2	1	AUTO	20.00	8.00	1.00	40.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
3	3	1	SEDAN	50.00	15.00	2.00	80.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
4	1	1	AUTO	30.00	10.00	2.00	50.00	\N	2026-01-19 16:27:28.702004+05:30	\N	\N
\.


--
-- TOC entry 5406 (class 0 OID 28187)
-- Dependencies: 251
-- Data for Name: fleet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet (fleet_id, tenant_id, owner_user_id, fleet_name, status, approval_status, created_by, created_on, updated_by, updated_on, fleet_type) FROM stdin;
1	1	6	Driver 6 Fleet	ACTIVE	APPROVED	3	2026-01-22 10:55:45.141912+05:30	\N	\N	INDIVIDUAL
4	1	18	Driver 18 Fleet	ACTIVE	APPROVED	3	2026-01-25 23:54:26.535492+05:30	\N	\N	INDIVIDUAL
5	1	19	Driver 19 Fleet	ACTIVE	APPROVED	3	2026-01-26 00:19:38.659271+05:30	\N	\N	INDIVIDUAL
6	1	20	Driver 20 Fleet	ACTIVE	APPROVED	3	2026-01-26 00:33:50.316487+05:30	\N	\N	INDIVIDUAL
7	1	21	Driver 21 Fleet	ACTIVE	APPROVED	3	2026-01-26 13:20:59.561375+05:30	\N	\N	INDIVIDUAL
2	1	15	Fleet0	ACTIVE	APPROVED	15	2026-01-22 12:03:29.712215+05:30	\N	2026-01-26 13:22:10.817636+05:30	BUSINESS
8	1	16	Driver 16 Fleet	ACTIVE	APPROVED	3	2026-01-26 14:46:55.989547+05:30	\N	\N	INDIVIDUAL
9	1	22	Driver 22 Fleet	ACTIVE	APPROVED	3	2026-01-26 19:32:42.474021+05:30	\N	\N	INDIVIDUAL
10	5	26	Driver 26 Fleet	ACTIVE	APPROVED	19	2026-01-27 00:25:22.008822+05:30	\N	\N	INDIVIDUAL
\.


--
-- TOC entry 5407 (class 0 OID 28194)
-- Dependencies: 252
-- Data for Name: fleet_city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_city (fleet_id, city_id, created_by, created_on, updated_by, updated_on) FROM stdin;
2	1	\N	2026-01-26 16:57:46.723304+05:30	\N	\N
\.


--
-- TOC entry 5408 (class 0 OID 28198)
-- Dependencies: 253
-- Data for Name: fleet_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_document (document_id, fleet_id, document_type, file_url, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on) FROM stdin;
1	2	Something	oollllkjhg	PENDING	\N	\N	15	2026-01-22 12:03:29.712215+05:30	\N	\N
\.


--
-- TOC entry 5410 (class 0 OID 28205)
-- Dependencies: 255
-- Data for Name: fleet_driver; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_driver (id, fleet_id, driver_id, start_date, end_date, created_by, created_on, updated_by, updated_on) FROM stdin;
1	2	16	2026-01-26 17:41:10.866561+05:30	\N	16	2026-01-26 17:41:10.81536+05:30	\N	\N
2	9	22	2026-01-26 19:32:42.515003+05:30	\N	3	2026-01-26 19:32:42.474021+05:30	\N	\N
3	10	26	2026-01-27 00:25:22.030748+05:30	\N	19	2026-01-27 00:25:22.008822+05:30	\N	\N
\.


--
-- TOC entry 5495 (class 0 OID 28657)
-- Dependencies: 340
-- Data for Name: fleet_driver_invite; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_driver_invite (invite_id, fleet_id, driver_id, status, invited_at, responded_at) FROM stdin;
1	2	16	ACCEPTED	2026-01-26 17:38:27.133575+05:30	2026-01-26 17:41:10.866561+05:30
\.


--
-- TOC entry 5413 (class 0 OID 28211)
-- Dependencies: 258
-- Data for Name: fleet_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_ledger (entry_id, fleet_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5415 (class 0 OID 28218)
-- Dependencies: 260
-- Data for Name: lost_item_report; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lost_item_report (report_id, trip_id, user_id, description, status, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5417 (class 0 OID 28225)
-- Dependencies: 262
-- Data for Name: lu_account_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_account_status (status_code) FROM stdin;
ACTIVE
INACTIVE
SUSPENDED
CLOSED
\.


--
-- TOC entry 5418 (class 0 OID 28230)
-- Dependencies: 263
-- Data for Name: lu_approval_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_approval_status (status_code) FROM stdin;
PENDING
APPROVED
REJECTED
\.


--
-- TOC entry 5419 (class 0 OID 28235)
-- Dependencies: 264
-- Data for Name: lu_coupon_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_coupon_type (type_code) FROM stdin;
FLAT
PERCENTAGE
\.


--
-- TOC entry 5420 (class 0 OID 28240)
-- Dependencies: 265
-- Data for Name: lu_driver_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_driver_type (type_code) FROM stdin;
INDEPENDENT
FLEET
\.


--
-- TOC entry 5421 (class 0 OID 28245)
-- Dependencies: 266
-- Data for Name: lu_fleet_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_fleet_type (fleet_type_code, description) FROM stdin;
INDIVIDUAL	Single driver owned fleet
BUSINESS	Company or aggregator fleet
\.


--
-- TOC entry 5422 (class 0 OID 28250)
-- Dependencies: 267
-- Data for Name: lu_fuel_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_fuel_type (fuel_code, description) FROM stdin;
PETROL	Petrol
DIESEL	Diesel
CNG	Compressed Natural Gas
EV	Electric Vehicle
\.


--
-- TOC entry 5423 (class 0 OID 28253)
-- Dependencies: 268
-- Data for Name: lu_gender; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_gender (gender_code) FROM stdin;
MALE
FEMALE
OTHER
PREFER_NOT_TO_SAY
\.


--
-- TOC entry 5424 (class 0 OID 28258)
-- Dependencies: 269
-- Data for Name: lu_payment_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_payment_status (status_code) FROM stdin;
PENDING
SUCCESS
FAILED
REFUNDED
\.


--
-- TOC entry 5425 (class 0 OID 28263)
-- Dependencies: 270
-- Data for Name: lu_settlement_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_settlement_status (status_code) FROM stdin;
PENDING
COMPLETED
FAILED
\.


--
-- TOC entry 5426 (class 0 OID 28268)
-- Dependencies: 271
-- Data for Name: lu_support_ticket_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_support_ticket_status (status_code) FROM stdin;
OPEN
IN_PROGRESS
RESOLVED
CLOSED
\.


--
-- TOC entry 5427 (class 0 OID 28273)
-- Dependencies: 272
-- Data for Name: lu_tenant_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_tenant_role (role_code) FROM stdin;
RIDER
DRIVER
FLEET_OWNER
DISPATCHER
TENANT_ADMIN
PLATFORM_ADMIN
SUPPORT_AGENT
\.


--
-- TOC entry 5428 (class 0 OID 28278)
-- Dependencies: 273
-- Data for Name: lu_trip_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_trip_status (status_code) FROM stdin;
REQUESTED
ASSIGNED
PICKED_UP
COMPLETED
CANCELLED
\.


--
-- TOC entry 5429 (class 0 OID 28283)
-- Dependencies: 274
-- Data for Name: lu_vehicle_category; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_vehicle_category (category_code) FROM stdin;
BIKE
AUTO
SEDAN
SUV
LUXURY
\.


--
-- TOC entry 5430 (class 0 OID 28288)
-- Dependencies: 275
-- Data for Name: lu_vehicle_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_vehicle_status (status_code) FROM stdin;
ACTIVE
INACTIVE
BLOCKED
\.


--
-- TOC entry 5431 (class 0 OID 28293)
-- Dependencies: 276
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment (payment_id, trip_id, amount, currency, payment_mode, status, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5433 (class 0 OID 28300)
-- Dependencies: 278
-- Data for Name: platform_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.platform_ledger (entry_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5435 (class 0 OID 28307)
-- Dependencies: 280
-- Data for Name: platform_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.platform_wallet (id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5436 (class 0 OID 28313)
-- Dependencies: 281
-- Data for Name: pricing_time_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pricing_time_rule (rule_id, tenant_id, city_id, rule_type, start_time, end_time, multiplier, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5438 (class 0 OID 28318)
-- Dependencies: 283
-- Data for Name: refund; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.refund (refund_id, payment_id, amount, reason, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5440 (class 0 OID 28325)
-- Dependencies: 285
-- Data for Name: ride_request; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ride_request (request_id, rider_id, city_id, pickup_lat, pickup_lng, drop_lat, drop_lng, status, created_on) FROM stdin;
1	9	1	12.980000	77.890000	12.960000	77.850000	CONFIRMED	2026-01-19 16:44:14.0416+05:30
\.


--
-- TOC entry 5442 (class 0 OID 28332)
-- Dependencies: 287
-- Data for Name: rider_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rider_rating_summary (rider_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 5443 (class 0 OID 28335)
-- Dependencies: 288
-- Data for Name: sos_event; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sos_event (sos_id, trip_id, triggered_by, latitude, longitude, triggered_at, resolved_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5445 (class 0 OID 28340)
-- Dependencies: 290
-- Data for Name: support_ticket; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket (ticket_id, user_id, trip_id, sos_id, issue_type, severity, status, assigned_to, assigned_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5446 (class 0 OID 28346)
-- Dependencies: 291
-- Data for Name: support_ticket_assignment_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket_assignment_history (history_id, ticket_id, assigned_to, assigned_at, unassigned_at, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5448 (class 0 OID 28351)
-- Dependencies: 293
-- Data for Name: support_ticket_conversation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket_conversation (message_id, ticket_id, sender_id, message_text, sent_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5451 (class 0 OID 28359)
-- Dependencies: 296
-- Data for Name: surge_event; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.surge_event (surge_id, tenant_id, surge_zone_id, multiplier, demand_index, supply_index, started_at, ended_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5453 (class 0 OID 28364)
-- Dependencies: 298
-- Data for Name: surge_zone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.surge_zone (surge_zone_id, zone_id, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5455 (class 0 OID 28369)
-- Dependencies: 300
-- Data for Name: tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant (tenant_id, name, default_currency, default_timezone, status, created_by, created_on, updated_by, updated_on, tenant_code) FROM stdin;
1	RideSharing India	INR	Asia/Kolkata	ACTIVE	\N	2026-01-13 16:16:53.621268+05:30	\N	\N	TENANT_1
2	DemoTenantIndia	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 11:28:55.81198+05:30	\N	\N	TENANT_2
3	Quick Rides	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_3
4	City Taxi	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_4
5	Premuim Cabs	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_5
6	Rydo	INR	Asia/Kolkata	ACTIVE	\N	2026-01-24 11:59:13.06932+05:30	\N	2026-01-24 11:59:13.06932+05:30	RYDO
\.


--
-- TOC entry 5456 (class 0 OID 28375)
-- Dependencies: 301
-- Data for Name: tenant_admin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_admin (tenant_admin_id, tenant_id, user_id, is_primary, created_by, created_on, updated_by, updated_on) FROM stdin;
1	1	3	t	\N	2026-01-19 11:30:13.829753+05:30	\N	\N
2	2	17	t	\N	2026-01-25 00:42:17.306242+05:30	\N	2026-01-25 00:42:17.306242+05:30
3	5	19	t	\N	2026-01-27 00:14:29.684226+05:30	\N	\N
\.


--
-- TOC entry 5458 (class 0 OID 28381)
-- Dependencies: 303
-- Data for Name: tenant_city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_city (tenant_id, city_id, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5459 (class 0 OID 28385)
-- Dependencies: 304
-- Data for Name: tenant_country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_country (tenant_id, country_code, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5460 (class 0 OID 28389)
-- Dependencies: 305
-- Data for Name: tenant_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_document (tenant_document_id, tenant_id, document_type, file_name, file_url, file_hash, is_active, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5462 (class 0 OID 28397)
-- Dependencies: 307
-- Data for Name: tenant_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_ledger (entry_id, tenant_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 5464 (class 0 OID 28404)
-- Dependencies: 309
-- Data for Name: tenant_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_rating_summary (tenant_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 5465 (class 0 OID 28407)
-- Dependencies: 310
-- Data for Name: tenant_settlement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_settlement (settlement_id, tenant_id, amount, status, requested_at, processed_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5467 (class 0 OID 28414)
-- Dependencies: 312
-- Data for Name: tenant_tax_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_tax_rule (tax_id, tenant_id, country_code, tax_type, rate, effective_from, effective_to, created_by, created_on, is_active) FROM stdin;
\.


--
-- TOC entry 5470 (class 0 OID 28421)
-- Dependencies: 315
-- Data for Name: tenant_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_wallet (tenant_id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5471 (class 0 OID 28426)
-- Dependencies: 316
-- Data for Name: trip; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip (trip_id, tenant_id, rider_id, driver_id, vehicle_id, city_id, zone_id, pickup_lat, pickup_lng, drop_lat, drop_lng, status, requested_at, assigned_at, picked_up_at, completed_at, cancelled_at, fare_amount, driver_earning, platform_fee, payment_status, created_by, created_on, updated_by, updated_on) FROM stdin;
4	1	9	\N	\N	1	\N	12.980000	77.890000	12.960000	77.850000	REQUESTED	2026-01-19 16:45:16.478653+05:30	\N	\N	\N	\N	\N	\N	\N	\N	9	2026-01-19 16:45:16.466253+05:30	\N	\N
\.


--
-- TOC entry 5472 (class 0 OID 28433)
-- Dependencies: 317
-- Data for Name: trip_cancellation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_cancellation (cancel_id, trip_id, cancelled_by, reason, cancelled_at) FROM stdin;
\.


--
-- TOC entry 5474 (class 0 OID 28440)
-- Dependencies: 319
-- Data for Name: trip_fare_breakdown; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_fare_breakdown (id, trip_id, base_fare, distance_fare, time_fare, surge_amount, night_charge, tax_amount, discount_amount, final_fare, created_on) FROM stdin;
\.


--
-- TOC entry 5476 (class 0 OID 28445)
-- Dependencies: 321
-- Data for Name: trip_otp; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_otp (otp_id, trip_id, otp_code, expires_at, verified, created_on) FROM stdin;
\.


--
-- TOC entry 5478 (class 0 OID 28451)
-- Dependencies: 323
-- Data for Name: trip_rating; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_rating (rating_id, trip_id, rater_id, ratee_id, rating, comment, created_on) FROM stdin;
\.


--
-- TOC entry 5480 (class 0 OID 28459)
-- Dependencies: 325
-- Data for Name: trip_route_point; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_route_point (id, trip_id, latitude, longitude, recorded_at) FROM stdin;
\.


--
-- TOC entry 5483 (class 0 OID 28464)
-- Dependencies: 328
-- Data for Name: user_auth; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_auth (user_id, password_hash, is_locked, last_password_change, created_by, created_on, updated_by, updated_on) FROM stdin;
1	$2b$12$2IKvhs5bTeNn3WSnqOMlPO3jmkGegYpOO6PNiyt0w/Wvr6RdDxCaC	f	2026-01-14 12:33:14.329794+05:30	\N	2026-01-14 12:33:14.329794+05:30	\N	\N
2	$2b$12$WGa249S47eGao0tAtGcbeOKakTaXHA1ulmkv3BEd7Q.o8AOrgxluC	f	2026-01-14 13:33:36.195494+05:30	\N	2026-01-14 13:33:36.195494+05:30	\N	\N
3	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 11:57:06.945074+05:30	\N	2026-01-19 11:57:06.945074+05:30	\N	\N
4	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 11:57:49.967356+05:30	\N	2026-01-19 11:57:49.967356+05:30	\N	\N
6	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 12:01:25.752797+05:30	\N	2026-01-19 12:01:25.752797+05:30	\N	\N
7	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 12:02:01.848404+05:30	\N	2026-01-19 12:02:01.848404+05:30	\N	\N
8	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 12:02:12.068685+05:30	\N	2026-01-19 12:02:12.068685+05:30	\N	\N
9	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 12:02:27.433314+05:30	\N	2026-01-19 12:02:27.433314+05:30	\N	\N
10	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 12:04:03.097923+05:30	\N	2026-01-19 12:04:03.097923+05:30	\N	\N
11	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	2026-01-19 15:26:03.784735+05:30	\N	2026-01-19 15:26:03.784735+05:30	\N	\N
17	$2b$12$0BfWUKVKEGRExEKJaDQ.zuf3..0sqXtXOoZgwe7iLlFj7uNjaYMQS	f	\N	\N	2026-01-25 00:42:17.306242+05:30	\N	2026-01-25 00:42:17.306242+05:30
19	$2b$12$8ffBaRjjS2TDy2fI.Ai57.5MTYe.baeXRw8qF1PjRM2Ju4e8ykF5a	f	\N	\N	2026-01-27 00:20:51.453018+05:30	\N	\N
\.


--
-- TOC entry 5484 (class 0 OID 28470)
-- Dependencies: 329
-- Data for Name: user_kyc; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_kyc (kyc_id, user_id, document_type, document_number, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on, file_url) FROM stdin;
4	14	DRIVING_LICENSE	DL1234567890	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/license.pdf
5	14	AADHAAR	123456789012	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/aadhaar.pdf
6	14	PHOTO	PASSPORT_PHOTO	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/photo.jpg
7	15	DRIVING_LICENSE	DL1234567890	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-license-url
8	15	AADHAAR	123456789012	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-aadhaar-url
9	15	PHOTO	PASSPORT_PHOTO	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-photo-url
10	18	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	18	2026-01-25 23:04:44.060701+05:30	\N	\N	file://documents/18/driving_license
11	18	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	18	2026-01-25 23:04:44.060701+05:30	\N	\N	file://documents/18/aadhaar
12	18	PHOTO		PENDING	\N	\N	18	2026-01-25 23:04:44.060701+05:30	\N	\N	file://documents/18/driver_photo
13	19	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	19	2026-01-26 00:18:51.729838+05:30	\N	\N	uploads/driver_documents/19/driving_license_20260126_001851.pdf
14	19	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	19	2026-01-26 00:18:51.729838+05:30	\N	\N	uploads/driver_documents/19/aadhaar_20260126_001851.jpeg
15	19	PHOTO		PENDING	\N	\N	19	2026-01-26 00:18:51.729838+05:30	\N	\N	uploads/driver_documents/19/driver_photo_20260126_001851.jpg
16	19	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:18:51.877454+05:30	\N	\N	uploads/driver_documents/19/driving_license_20260126_001851.pdf
17	19	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:18:51.877454+05:30	\N	\N	uploads/driver_documents/19/driver_photo_20260126_001851.jpg
18	19	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:18:51.877454+05:30	\N	\N	uploads/driver_documents/19/aadhaar_20260126_001851.jpeg
22	20	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:33:24.411667+05:30	\N	\N	uploads/driver_documents/20/driving_license_20260126_003324.jpeg
23	20	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:33:24.411667+05:30	\N	\N	uploads/driver_documents/20/driver_photo_20260126_003324.jpeg
24	20	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 00:33:24.411667+05:30	\N	\N	uploads/driver_documents/20/aadhaar_20260126_003324.jpeg
28	21	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 12:55:22.900414+05:30	\N	\N	uploads/driver_documents/21/driving_license_20260126_125522.png
29	21	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 12:55:22.900414+05:30	\N	\N	uploads/driver_documents/21/driver_photo_20260126_125522.png
30	21	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 12:55:22.900414+05:30	\N	\N	uploads/driver_documents/21/aadhaar_20260126_125522.png
34	16	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 14:46:38.92884+05:30	\N	\N	uploads/driver_documents/16/driving_license_20260126_144638.png
35	16	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 14:46:38.92884+05:30	\N	\N	uploads/driver_documents/16/driver_photo_20260126_144638.png
36	16	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 14:46:38.92884+05:30	\N	\N	uploads/driver_documents/16/aadhaar_20260126_144638.png
40	22	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 19:29:31.506574+05:30	\N	\N	uploads/driver_documents/22/driving_license_20260126_192931.png
41	22	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 19:29:31.506574+05:30	\N	\N	uploads/driver_documents/22/driver_photo_20260126_192931.png
42	22	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 19:29:31.506574+05:30	\N	\N	uploads/driver_documents/22/aadhaar_20260126_192931.png
47	24	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:33:47.733585+05:30	\N	\N	uploads/driver_documents/24/driving_license_20260126_233347.png
48	24	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:33:47.733585+05:30	\N	\N	uploads/driver_documents/24/driver_photo_20260126_233347.png
49	24	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:33:47.733585+05:30	\N	\N	uploads/driver_documents/24/aadhaar_20260126_233347.png
50	24	PAN	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:33:47.733585+05:30	\N	\N	uploads/driver_documents/24/pan_20260126_233347.png
54	25	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:57:06.277126+05:30	\N	\N	uploads/driver_documents/25/driving_license_20260126_235706.png
55	25	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:57:06.277126+05:30	\N	\N	uploads/driver_documents/25/driver_photo_20260126_235706.png
56	25	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-26 23:57:06.277126+05:30	\N	\N	uploads/driver_documents/25/aadhaar_20260126_235706.png
60	26	DRIVING_LICENSE	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-27 00:09:57.529246+05:30	\N	\N	uploads/driver_documents/26/driving_license_20260127_000957.png
61	26	PROFILE_PHOTO	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-27 00:09:57.529246+05:30	\N	\N	uploads/driver_documents/26/driver_photo_20260127_000957.png
62	26	AADHAAR	PENDING_VERIFICATION	PENDING	\N	\N	\N	2026-01-27 00:09:57.529246+05:30	\N	\N	uploads/driver_documents/26/aadhaar_20260127_000957.png
\.


--
-- TOC entry 5486 (class 0 OID 28477)
-- Dependencies: 331
-- Data for Name: user_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_session (session_id, user_id, login_at, logout_at, ip_address, user_agent, created_by, created_on, updated_by, updated_on) FROM stdin;
a8657328-ce62-4ba3-9516-78865a5198f3	1	2026-01-14 07:06:29.078024+05:30	\N	\N	\N	\N	2026-01-14 12:36:28.778136+05:30	\N	\N
aaf93d8c-ecdd-4cc9-aa16-48a548a831e6	2	2026-01-14 08:06:58.515029+05:30	\N	\N	\N	\N	2026-01-14 13:36:58.215235+05:30	\N	\N
85a184a1-de4e-4cbe-bf6c-a3c0f8ffbaf3	9	2026-01-19 12:07:38.898383+05:30	\N	\N	\N	\N	2026-01-19 12:07:38.584682+05:30	\N	\N
b280cbea-1f38-4eb5-98b7-8c147d1cd5e7	6	2026-01-19 12:20:35.115831+05:30	\N	\N	\N	\N	2026-01-19 12:20:34.788223+05:30	\N	\N
a88564de-e33a-408d-acbc-0a28f30390f0	6	2026-01-19 12:20:37.981362+05:30	\N	\N	\N	\N	2026-01-19 12:20:37.702949+05:30	\N	\N
8a01e87b-dff5-4d66-92c7-62645b87a622	6	2026-01-19 12:24:38.288876+05:30	\N	\N	\N	\N	2026-01-19 12:24:37.974418+05:30	\N	\N
f97bcbbd-db60-426f-8ee2-42486ec6676b	6	2026-01-19 12:25:06.655867+05:30	\N	\N	\N	\N	2026-01-19 12:25:06.335557+05:30	\N	\N
18d314ab-a616-4659-b30e-b71193f15e72	6	2026-01-19 12:25:10.414812+05:30	\N	\N	\N	\N	2026-01-19 12:25:10.088667+05:30	\N	\N
f6242c6c-9f76-470e-ae5f-fde002fc82ce	6	2026-01-19 12:25:11.532426+05:30	\N	\N	\N	\N	2026-01-19 12:25:11.249577+05:30	\N	\N
301a962b-0437-4fa5-8a84-b3fb3f0903a0	9	2026-01-19 12:25:42.997869+05:30	\N	\N	\N	\N	2026-01-19 12:25:42.687015+05:30	\N	\N
d0045eb1-efa7-4cb8-974e-6a67db7e06f9	10	2026-01-19 12:26:23.285545+05:30	\N	\N	\N	\N	2026-01-19 12:26:22.987658+05:30	\N	\N
9c1dad49-ab0f-4bbd-b490-f271bbf431e6	10	2026-01-19 12:26:24.296895+05:30	\N	\N	\N	\N	2026-01-19 12:26:24.000025+05:30	\N	\N
aa96c846-5cf2-45ae-b564-5530f24039c7	3	2026-01-19 12:27:05.524324+05:30	\N	\N	\N	\N	2026-01-19 12:27:05.22078+05:30	\N	\N
027fb7f3-23fe-4383-839c-7859abd34f2f	9	2026-01-19 12:32:54.224652+05:30	\N	\N	\N	\N	2026-01-19 12:32:53.914586+05:30	\N	\N
848b9454-1883-4471-ab78-25a88db5a748	9	2026-01-19 12:54:52.090817+05:30	\N	\N	\N	\N	2026-01-19 12:54:51.769872+05:30	\N	\N
27ba6cd8-6764-4f09-a4e2-fa91f336902a	9	2026-01-19 13:20:05.235905+05:30	\N	\N	\N	\N	2026-01-19 13:20:04.879667+05:30	\N	\N
de7aa73e-ba6e-4fa2-8e5a-2a47d24b11bb	10	2026-01-19 15:12:28.517879+05:30	\N	\N	\N	\N	2026-01-19 15:12:28.102683+05:30	\N	\N
4dc5895e-69af-4ff8-a70f-8fe63788bfcf	9	2026-01-19 15:19:41.086478+05:30	\N	\N	\N	\N	2026-01-19 15:19:40.768306+05:30	\N	\N
e4ee6704-2ae0-4ddf-94ed-aec693878d8d	10	2026-01-19 15:20:25.180407+05:30	\N	\N	\N	\N	2026-01-19 15:20:24.857663+05:30	\N	\N
ffb1bf50-9749-4407-885d-976d395cccb9	11	2026-01-19 15:26:33.241468+05:30	\N	\N	\N	\N	2026-01-19 15:26:32.91848+05:30	\N	\N
db9e2596-4c12-4954-918a-147d471f0aa0	9	2026-01-19 15:43:07.155456+05:30	\N	\N	\N	\N	2026-01-19 15:43:06.833626+05:30	\N	\N
9785b021-7b6f-4d54-bfed-fb27dc17fd14	9	2026-01-19 15:54:27.134737+05:30	\N	\N	\N	\N	2026-01-19 15:54:26.813099+05:30	\N	\N
a8cd9c84-879e-4340-907e-abd1ceaf6117	9	2026-01-19 16:39:36.981247+05:30	\N	\N	\N	\N	2026-01-19 16:39:36.626808+05:30	\N	\N
86ff4c89-037f-47e2-891b-ae18211d7c01	9	2026-01-19 16:43:47.395543+05:30	\N	\N	\N	\N	2026-01-19 16:43:47.079796+05:30	\N	\N
05157201-5a07-4b3a-aaac-fcad6e5d4b1a	6	2026-01-19 16:48:57.621113+05:30	\N	\N	\N	\N	2026-01-19 16:48:57.296381+05:30	\N	\N
dfaeaa76-aff4-4677-8b74-99be09a57294	4	2026-01-19 16:50:37.40124+05:30	\N	\N	\N	\N	2026-01-19 16:50:37.104378+05:30	\N	\N
aba1bff1-d2c2-4fe8-9280-356bed6f8ffc	7	2026-01-19 18:08:41.300722+05:30	\N	\N	\N	\N	2026-01-19 18:08:40.97975+05:30	\N	\N
51d1650d-475d-4284-b559-94279403b862	7	2026-01-19 18:08:43.69101+05:30	\N	\N	\N	\N	2026-01-19 18:08:43.375458+05:30	\N	\N
1b4adfa5-3a49-47f9-a975-6b88e395a287	7	2026-01-19 18:08:59.023679+05:30	\N	\N	\N	\N	2026-01-19 18:08:58.737462+05:30	\N	\N
c5a88a8c-8c76-40bb-ad78-ce7f46500b6f	7	2026-01-19 18:23:47.365228+05:30	\N	\N	\N	\N	2026-01-19 18:23:47.041216+05:30	\N	\N
49d362f9-cb35-4a44-8527-f9c5a78f9376	8	2026-01-19 18:35:47.611246+05:30	\N	\N	\N	\N	2026-01-19 18:35:47.263288+05:30	\N	\N
721a7c03-e356-45e0-94b3-2b57aaf5d4ff	6	2026-01-20 15:53:52.360562+05:30	\N	\N	\N	\N	2026-01-20 15:53:52.052482+05:30	\N	\N
c143100d-2f7d-4244-9e0e-dbd1fc94982d	6	2026-01-21 12:14:09.712243+05:30	\N	\N	\N	\N	2026-01-21 12:14:09.397839+05:30	\N	\N
6b427d27-b8f9-4e3b-9861-6eb439d94846	6	2026-01-21 17:13:52.268439+05:30	\N	\N	\N	\N	2026-01-21 17:13:51.945383+05:30	\N	\N
ff1bdfbe-69de-4016-a8ca-76ced1a617db	9	2026-01-21 17:16:16.772493+05:30	\N	\N	\N	\N	2026-01-21 17:16:16.444393+05:30	\N	\N
c8245ff2-8d5b-4233-853d-0eca0748035c	3	2026-01-21 19:10:05.964088+05:30	\N	\N	\N	\N	2026-01-21 19:10:05.65152+05:30	\N	\N
fcabefd4-c2c5-475e-87cb-bfabaaa3a33b	1	2026-01-24 11:23:28.767717+05:30	\N	\N	\N	\N	2026-01-24 11:23:27.995371+05:30	\N	\N
8dad5283-3416-4988-86dc-f0cb9fa17bae	1	2026-01-24 11:28:35.694218+05:30	\N	\N	\N	\N	2026-01-24 11:28:35.119221+05:30	\N	\N
6fe9b21e-f85e-43d6-83b5-5eaaf43c16ab	1	2026-01-24 11:50:36.990297+05:30	\N	\N	\N	\N	2026-01-24 11:50:36.158759+05:30	\N	\N
2bc17612-22cb-48c7-920d-cf2e576655c1	1	2026-01-24 11:53:54.820703+05:30	\N	\N	\N	\N	2026-01-24 11:53:54.111691+05:30	\N	\N
3b522fbd-1369-4a16-8462-67d3f37ac4ba	3	2026-01-24 12:13:47.433304+05:30	2026-01-24 12:24:47.387911+05:30	\N	\N	\N	2026-01-24 12:13:46.71383+05:30	\N	2026-01-24 12:24:47.383203+05:30
01237769-bb99-4d3d-9cd1-9cc1ab951c64	1	2026-01-24 12:24:54.552646+05:30	\N	\N	\N	\N	2026-01-24 12:24:53.953262+05:30	\N	\N
982530b1-2a76-427d-98ad-0797b7380c03	3	2026-01-24 12:25:17.645569+05:30	2026-01-24 12:36:46.59867+05:30	\N	\N	\N	2026-01-24 12:25:17.073549+05:30	\N	2026-01-24 12:36:46.594095+05:30
ebc9407f-f87a-4fbc-be9a-a295f892d5d3	1	2026-01-24 12:36:52.741205+05:30	\N	\N	\N	\N	2026-01-24 12:36:52.08629+05:30	\N	\N
94fa9ccb-efcc-45b3-af5c-3b8d1f2e38e8	1	2026-01-24 12:37:37.336184+05:30	\N	\N	\N	\N	2026-01-24 12:37:36.754194+05:30	\N	\N
10523a39-f9ec-487d-8b0e-e19ea22a55f1	1	2026-01-24 13:00:17.423335+05:30	\N	\N	\N	\N	2026-01-24 13:00:16.710002+05:30	\N	\N
8c96cbe3-42d4-4fc6-acc1-e2958779a88c	3	2026-01-24 13:00:43.656802+05:30	\N	\N	\N	\N	2026-01-24 13:00:42.942087+05:30	\N	\N
daf40440-93ce-41d1-b68d-131f39a9b92f	3	2026-01-24 13:14:23.572951+05:30	2026-01-24 13:14:45.378105+05:30	\N	\N	\N	2026-01-24 13:14:22.681319+05:30	\N	2026-01-24 13:14:45.364115+05:30
04a438bb-c45a-4344-8eb3-dee9030fee40	1	2026-01-24 13:14:59.276662+05:30	\N	\N	\N	\N	2026-01-24 13:14:58.513546+05:30	\N	\N
ff71450e-ac7f-4233-bf81-dc655488eba3	1	2026-01-24 13:15:00.09358+05:30	\N	\N	\N	\N	2026-01-24 13:14:59.371509+05:30	\N	\N
23752695-981b-4a12-aa36-0a88164dbb47	1	2026-01-24 13:18:10.281312+05:30	\N	\N	\N	\N	2026-01-24 13:18:09.557905+05:30	\N	\N
1a0cd392-ce5b-4bca-8eab-8c59d140c730	1	2026-01-24 13:18:11.379041+05:30	\N	\N	\N	\N	2026-01-24 13:18:10.6665+05:30	\N	\N
ab268d3b-6257-4af1-96d5-fed09b2e3ed5	1	2026-01-24 13:19:29.733367+05:30	\N	\N	\N	\N	2026-01-24 13:19:28.991199+05:30	\N	\N
295c2f46-339e-4780-9c18-14132e71326d	1	2026-01-24 13:19:30.885221+05:30	\N	\N	\N	\N	2026-01-24 13:19:30.145106+05:30	\N	\N
7de371ac-5582-4411-82d5-2e59af2fc357	1	2026-01-24 13:19:44.878295+05:30	\N	\N	\N	\N	2026-01-24 13:19:44.159933+05:30	\N	\N
0ed00070-2f52-4e23-92c4-b732bc7de23c	1	2026-01-24 13:19:45.709221+05:30	\N	\N	\N	\N	2026-01-24 13:19:44.962839+05:30	\N	\N
cc86557e-71a4-405d-a9bd-5f5e14bca77d	3	2026-01-24 13:20:10.891017+05:30	\N	\N	\N	\N	2026-01-24 13:20:10.159233+05:30	\N	\N
ce1582ce-0a28-41ee-8b9e-131db555bc0b	1	2026-01-24 13:21:21.48009+05:30	\N	\N	\N	\N	2026-01-24 13:21:20.762811+05:30	\N	\N
ec4cccfc-a51d-46d9-954b-1587392319ca	1	2026-01-24 13:21:20.35835+05:30	2026-01-24 13:25:09.40871+05:30	\N	\N	\N	2026-01-24 13:21:19.623815+05:30	\N	2026-01-24 13:25:09.396931+05:30
b9d5b413-d77d-40df-9486-f450f0728bdf	3	2026-01-24 13:25:25.976235+05:30	\N	\N	\N	\N	2026-01-24 13:25:25.245713+05:30	\N	\N
d956530f-cabf-495e-b2ef-beb5db4ea6d3	3	2026-01-24 13:26:47.709834+05:30	\N	\N	\N	\N	2026-01-24 13:26:46.959665+05:30	\N	\N
acbb9c0b-d508-47c3-9228-4c9bfaa7e014	1	2026-01-24 13:27:10.642499+05:30	\N	\N	\N	\N	2026-01-24 13:27:09.903949+05:30	\N	\N
0339247c-6d51-4c09-b3b2-8f5143f1cd2c	1	2026-01-24 13:27:11.847276+05:30	\N	\N	\N	\N	2026-01-24 13:27:11.057032+05:30	\N	\N
f9aedc5e-79d8-4af4-a704-c1c5b824dfff	1	2026-01-24 18:24:08.092788+05:30	\N	\N	\N	\N	2026-01-24 18:24:07.332769+05:30	\N	\N
09992375-a17e-477d-b2fe-a007834a6bdb	1	2026-01-24 18:24:07.141627+05:30	2026-01-24 18:27:50.463573+05:30	\N	\N	\N	2026-01-24 18:24:06.327162+05:30	\N	2026-01-24 18:27:50.457997+05:30
e7c7aec9-bd28-4f40-9631-4cabbb13e3f1	3	2026-01-24 18:28:05.468629+05:30	\N	\N	\N	\N	2026-01-24 18:28:05.033764+05:30	\N	\N
be565bb4-a00d-4b7c-bf0c-c5b32b87c87e	1	2026-01-24 23:30:51.030955+05:30	\N	\N	\N	\N	2026-01-24 23:30:49.971109+05:30	\N	\N
b05bbfe1-c988-44cc-b5c3-da73e22c63a5	1	2026-01-24 23:30:51.929602+05:30	\N	\N	\N	\N	2026-01-24 23:30:51.19397+05:30	\N	\N
72074cff-7f35-44c0-a0e3-479e8518979b	3	2026-01-24 23:48:51.347288+05:30	\N	\N	\N	\N	2026-01-24 23:48:50.543214+05:30	\N	\N
f3cc57c1-d097-4504-821f-d39cf2052a20	1	2026-01-25 00:26:17.638737+05:30	\N	\N	\N	\N	2026-01-25 00:26:16.844798+05:30	\N	\N
218491d9-7e37-4731-8b5c-01ceda258af9	1	2026-01-25 00:26:18.471075+05:30	\N	\N	\N	\N	2026-01-25 00:26:17.759934+05:30	\N	\N
7f612065-f2bf-44af-9467-9fc81c16bbb7	17	2026-01-25 00:42:53.680831+05:30	\N	\N	\N	\N	2026-01-25 00:42:52.758449+05:30	\N	\N
fffacd11-516e-455f-9557-ae3fbfafee25	1	2026-01-25 00:43:16.178449+05:30	\N	\N	\N	\N	2026-01-25 00:43:15.438693+05:30	\N	\N
0cffceb4-7b9d-4277-918e-945b856342b3	1	2026-01-25 00:43:17.017092+05:30	\N	\N	\N	\N	2026-01-25 00:43:16.288893+05:30	\N	\N
c312fe70-f172-445a-914d-c2536de5c095	1	2026-01-25 08:44:56.973739+05:30	\N	\N	\N	\N	2026-01-25 08:44:56.212171+05:30	\N	\N
d367e98f-30e2-4c6b-a2bf-4756722a5602	1	2026-01-25 08:44:57.671916+05:30	\N	\N	\N	\N	2026-01-25 08:44:57.082724+05:30	\N	\N
f4fab60f-f9a3-4786-b0fa-883a65cd8dc4	3	2026-01-25 23:53:16.792654+05:30	\N	\N	\N	\N	2026-01-25 23:53:15.702654+05:30	\N	\N
313ff419-84fd-4f58-b525-9d885fac98ac	3	2026-01-26 12:56:12.065713+05:30	\N	\N	\N	\N	2026-01-26 12:56:11.061391+05:30	\N	\N
b5e54182-2093-4644-914d-d83343844d4e	3	2026-01-26 23:52:10.220544+05:30	\N	\N	\N	\N	2026-01-26 23:52:09.43686+05:30	\N	\N
ee781077-1abc-4610-8f97-3355d440b560	19	2026-01-27 00:23:31.748334+05:30	\N	\N	\N	\N	2026-01-27 00:23:30.916327+05:30	\N	\N
\.


--
-- TOC entry 5487 (class 0 OID 28484)
-- Dependencies: 332
-- Data for Name: vehicle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle (vehicle_id, tenant_id, fleet_id, category, status, registration_no, created_by, created_on, updated_by, updated_on, approval_status) FROM stdin;
2	1	\N	AUTO	ACTIVE	TS09AB0001	\N	2026-01-19 16:11:26.401901+05:30	\N	\N	PENDING
3	1	2	SEDAN	ACTIVE	KA01AB1234	15	2026-01-26 18:28:27.883219+05:30	\N	\N	PENDING
4	1	9	AUTO	ACTIVE	KA01BB1234	22	2026-01-26 19:38:10.852696+05:30	3	2026-01-26 22:29:26.508503+05:30	APPROVED
5	1	9	BIKE	ACTIVE	KA01BC1234	22	2026-01-26 20:24:24.348451+05:30	3	2026-01-26 22:43:24.401863+05:30	REJECTED
6	1	2	SEDAN	ACTIVE	AA01AB1234	15	2026-01-26 22:48:24.608365+05:30	3	2026-01-26 22:53:03.393986+05:30	REJECTED
\.


--
-- TOC entry 5488 (class 0 OID 28490)
-- Dependencies: 333
-- Data for Name: vehicle_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle_document (document_id, vehicle_id, document_type, file_url, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on) FROM stdin;
1	3	RC	https://storage.example.com/vehicle/rc_ka01ab1234.pdf	PENDING	\N	\N	15	2026-01-26 18:28:27.883219+05:30	\N	\N
2	3	INSURANCE	https://storage.example.com/vehicle/insurance_valid.pdf	PENDING	\N	\N	15	2026-01-26 18:28:27.883219+05:30	\N	\N
3	3	VEHICLE_PHOTO	https://storage.example.com/vehicle/photo_front.jpg	PENDING	\N	\N	15	2026-01-26 18:28:27.883219+05:30	\N	\N
4	3	PERMIT	https://storage.example.com/vehicle/permit.pdf	PENDING	\N	\N	15	2026-01-26 18:28:27.883219+05:30	\N	\N
5	4	RC	https://storage.example.com/vehicle/rc_ka01ab1234.pdf	PENDING	\N	\N	22	2026-01-26 19:38:10.852696+05:30	\N	\N
6	4	INSURANCE	https://storage.example.com/vehicle/insurance_valid.pdf	PENDING	\N	\N	22	2026-01-26 19:38:10.852696+05:30	\N	\N
7	4	VEHICLE_PHOTO	https://storage.example.com/vehicle/photo_front.jpg	PENDING	\N	\N	22	2026-01-26 19:38:10.852696+05:30	\N	\N
8	4	PERMIT	https://storage.example.com/vehicle/permit.pdf	PENDING	\N	\N	22	2026-01-26 19:38:10.852696+05:30	\N	\N
9	4	skll	kll	PENDING	\N	\N	22	2026-01-26 19:41:02.818531+05:30	\N	\N
10	4	VEHICLE_PHOTO	string	PENDING	\N	\N	22	2026-01-26 19:41:21.080073+05:30	\N	\N
11	5	RC	https://storage.example.com/vehicle/rc_ka01ab1234.pdf	PENDING	\N	\N	22	2026-01-26 20:24:24.348451+05:30	\N	\N
12	5	INSURANCE	https://storage.example.com/vehicle/insurance_valid.pdf	PENDING	\N	\N	22	2026-01-26 20:24:24.348451+05:30	\N	\N
13	5	VEHICLE_PHOTO	https://storage.example.com/vehicle/photo_front.jpg	PENDING	\N	\N	22	2026-01-26 20:24:24.348451+05:30	\N	\N
14	5	PERMIT	https://storage.example.com/vehicle/permit.pdf	PENDING	\N	\N	22	2026-01-26 20:24:24.348451+05:30	\N	\N
15	5	skll	kll	PENDING	\N	\N	22	2026-01-26 20:25:43.584047+05:30	\N	\N
16	5	VEHICLE_PHOTO	string	PENDING	\N	\N	22	2026-01-26 20:25:59.056243+05:30	\N	\N
17	6	RC	https://storage.example.com/vehicle/rc_ka01ab1234.pdf	PENDING	\N	\N	15	2026-01-26 22:48:24.608365+05:30	\N	\N
18	6	INSURANCE	https://storage.example.com/vehicle/insurance_valid.pdf	PENDING	\N	\N	15	2026-01-26 22:48:24.608365+05:30	\N	\N
19	6	VEHICLE_PHOTO	https://storage.example.com/vehicle/photo_front.jpg	PENDING	\N	\N	15	2026-01-26 22:48:24.608365+05:30	\N	\N
20	6	PERMIT	https://storage.example.com/vehicle/permit.pdf	PENDING	\N	\N	15	2026-01-26 22:48:24.608365+05:30	\N	\N
21	6	hello	something	PENDING	\N	\N	15	2026-01-26 22:49:27.510543+05:30	\N	\N
\.


--
-- TOC entry 5490 (class 0 OID 28497)
-- Dependencies: 335
-- Data for Name: vehicle_spec; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle_spec (vehicle_id, manufacturer, model_name, manufacture_year, fuel_type, seating_capacity, created_by, created_on, updated_by, updated_on) FROM stdin;
3	Honday	CAR54	2024	Diesel	3	15	2026-01-26 18:33:12.024185+05:30	\N	\N
4	someone	something	1234	Petrol	6	22	2026-01-26 19:39:20.510441+05:30	\N	\N
5	someone	something	1234	Petrol	6	22	2026-01-26 20:25:28.024119+05:30	\N	\N
6	Honday	CAR54	2024	Diesel	3	15	2026-01-26 22:49:11.846844+05:30	\N	\N
\.


--
-- TOC entry 5492 (class 0 OID 28502)
-- Dependencies: 337
-- Data for Name: zone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zone (zone_id, city_id, name, center_lat, center_lng, boundary, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 5548 (class 0 OID 0)
-- Dependencies: 218
-- Name: app_user_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_user_id_seq', 26, true);


--
-- TOC entry 5549 (class 0 OID 0)
-- Dependencies: 220
-- Name: city_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.city_city_id_seq', 1, true);


--
-- TOC entry 5550 (class 0 OID 0)
-- Dependencies: 223
-- Name: coupon_coupon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.coupon_coupon_id_seq', 1, false);


--
-- TOC entry 5551 (class 0 OID 0)
-- Dependencies: 225
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.coupon_redemption_redemption_id_seq', 1, false);


--
-- TOC entry 5552 (class 0 OID 0)
-- Dependencies: 228
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dispatch_attempt_attempt_id_seq', 1, true);


--
-- TOC entry 5553 (class 0 OID 0)
-- Dependencies: 230
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dispatcher_assignment_assignment_id_seq', 1, false);


--
-- TOC entry 5554 (class 0 OID 0)
-- Dependencies: 232
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_progress_id_seq', 1, false);


--
-- TOC entry 5555 (class 0 OID 0)
-- Dependencies: 234
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_reward_reward_id_seq', 1, false);


--
-- TOC entry 5556 (class 0 OID 0)
-- Dependencies: 236
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_scheme_scheme_id_seq', 1, false);


--
-- TOC entry 5557 (class 0 OID 0)
-- Dependencies: 239
-- Name: driver_location_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_location_history_id_seq', 1, false);


--
-- TOC entry 5558 (class 0 OID 0)
-- Dependencies: 243
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_shift_shift_id_seq', 1, true);


--
-- TOC entry 5559 (class 0 OID 0)
-- Dependencies: 245
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_vehicle_assignment_assignment_id_seq', 1, true);


--
-- TOC entry 5560 (class 0 OID 0)
-- Dependencies: 248
-- Name: driver_work_availability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_work_availability_id_seq', 1, true);


--
-- TOC entry 5561 (class 0 OID 0)
-- Dependencies: 250
-- Name: fare_config_fare_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fare_config_fare_id_seq', 4, true);


--
-- TOC entry 5562 (class 0 OID 0)
-- Dependencies: 254
-- Name: fleet_document_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_document_document_id_seq', 1, true);


--
-- TOC entry 5563 (class 0 OID 0)
-- Dependencies: 256
-- Name: fleet_driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_driver_id_seq', 3, true);


--
-- TOC entry 5564 (class 0 OID 0)
-- Dependencies: 339
-- Name: fleet_driver_invite_invite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_driver_invite_invite_id_seq', 1, true);


--
-- TOC entry 5565 (class 0 OID 0)
-- Dependencies: 257
-- Name: fleet_fleet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_fleet_id_seq', 10, true);


--
-- TOC entry 5566 (class 0 OID 0)
-- Dependencies: 259
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_ledger_entry_id_seq', 1, false);


--
-- TOC entry 5567 (class 0 OID 0)
-- Dependencies: 261
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lost_item_report_report_id_seq', 1, false);


--
-- TOC entry 5568 (class 0 OID 0)
-- Dependencies: 277
-- Name: payment_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_payment_id_seq', 1, false);


--
-- TOC entry 5569 (class 0 OID 0)
-- Dependencies: 279
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.platform_ledger_entry_id_seq', 1, false);


--
-- TOC entry 5570 (class 0 OID 0)
-- Dependencies: 282
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pricing_time_rule_rule_id_seq', 1, false);


--
-- TOC entry 5571 (class 0 OID 0)
-- Dependencies: 284
-- Name: refund_refund_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.refund_refund_id_seq', 1, false);


--
-- TOC entry 5572 (class 0 OID 0)
-- Dependencies: 286
-- Name: ride_request_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ride_request_request_id_seq', 1, true);


--
-- TOC entry 5573 (class 0 OID 0)
-- Dependencies: 289
-- Name: sos_event_sos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sos_event_sos_id_seq', 1, false);


--
-- TOC entry 5574 (class 0 OID 0)
-- Dependencies: 292
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_assignment_history_history_id_seq', 1, false);


--
-- TOC entry 5575 (class 0 OID 0)
-- Dependencies: 294
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_conversation_message_id_seq', 1, false);


--
-- TOC entry 5576 (class 0 OID 0)
-- Dependencies: 295
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_ticket_id_seq', 1, false);


--
-- TOC entry 5577 (class 0 OID 0)
-- Dependencies: 297
-- Name: surge_event_surge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.surge_event_surge_id_seq', 1, false);


--
-- TOC entry 5578 (class 0 OID 0)
-- Dependencies: 299
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.surge_zone_surge_zone_id_seq', 1, false);


--
-- TOC entry 5579 (class 0 OID 0)
-- Dependencies: 302
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_admin_tenant_admin_id_seq', 2, true);


--
-- TOC entry 5580 (class 0 OID 0)
-- Dependencies: 306
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_document_tenant_document_id_seq', 1, false);


--
-- TOC entry 5581 (class 0 OID 0)
-- Dependencies: 308
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_ledger_entry_id_seq', 1, false);


--
-- TOC entry 5582 (class 0 OID 0)
-- Dependencies: 311
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_settlement_settlement_id_seq', 1, false);


--
-- TOC entry 5583 (class 0 OID 0)
-- Dependencies: 313
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_tax_rule_tax_id_seq', 1, false);


--
-- TOC entry 5584 (class 0 OID 0)
-- Dependencies: 314
-- Name: tenant_tenant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_tenant_id_seq', 6, true);


--
-- TOC entry 5585 (class 0 OID 0)
-- Dependencies: 318
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_cancellation_cancel_id_seq', 1, false);


--
-- TOC entry 5586 (class 0 OID 0)
-- Dependencies: 320
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_fare_breakdown_id_seq', 1, false);


--
-- TOC entry 5587 (class 0 OID 0)
-- Dependencies: 322
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_otp_otp_id_seq', 1, false);


--
-- TOC entry 5588 (class 0 OID 0)
-- Dependencies: 324
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_rating_rating_id_seq', 1, false);


--
-- TOC entry 5589 (class 0 OID 0)
-- Dependencies: 326
-- Name: trip_route_point_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_route_point_id_seq', 1, false);


--
-- TOC entry 5590 (class 0 OID 0)
-- Dependencies: 327
-- Name: trip_trip_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_trip_id_seq', 4, true);


--
-- TOC entry 5591 (class 0 OID 0)
-- Dependencies: 330
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_kyc_kyc_id_seq', 62, true);


--
-- TOC entry 5592 (class 0 OID 0)
-- Dependencies: 334
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicle_document_document_id_seq', 21, true);


--
-- TOC entry 5593 (class 0 OID 0)
-- Dependencies: 336
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicle_vehicle_id_seq', 6, true);


--
-- TOC entry 5594 (class 0 OID 0)
-- Dependencies: 338
-- Name: zone_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zone_zone_id_seq', 1, false);


--
-- TOC entry 5216 (class 2606 OID 28655)
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 5222 (class 2606 OID 28668)
-- Name: fleet_driver_invite fleet_driver_invite_fleet_id_driver_id_status_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver_invite
    ADD CONSTRAINT fleet_driver_invite_fleet_id_driver_id_status_key UNIQUE (fleet_id, driver_id, status);


--
-- TOC entry 5224 (class 2606 OID 28666)
-- Name: fleet_driver_invite fleet_driver_invite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver_invite
    ADD CONSTRAINT fleet_driver_invite_pkey PRIMARY KEY (invite_id);


--
-- TOC entry 5218 (class 2606 OID 28635)
-- Name: fleet fleet_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet
    ADD CONSTRAINT fleet_pkey PRIMARY KEY (fleet_id);


--
-- TOC entry 5219 (class 1259 OID 28681)
-- Name: idx_vehicle_approval_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicle_approval_status ON public.vehicle USING btree (approval_status);


--
-- TOC entry 5220 (class 1259 OID 28682)
-- Name: idx_vehicle_tenant_approval; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicle_tenant_approval ON public.vehicle USING btree (tenant_id, approval_status);


--
-- TOC entry 5225 (class 2606 OID 28674)
-- Name: fleet_driver_invite fleet_driver_invite_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver_invite
    ADD CONSTRAINT fleet_driver_invite_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.app_user(user_id) ON DELETE CASCADE;


--
-- TOC entry 5226 (class 2606 OID 28669)
-- Name: fleet_driver_invite fleet_driver_invite_fleet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver_invite
    ADD CONSTRAINT fleet_driver_invite_fleet_id_fkey FOREIGN KEY (fleet_id) REFERENCES public.fleet(fleet_id) ON DELETE CASCADE;


-- Completed on 2026-01-27 09:16:04

--
-- PostgreSQL database dump complete
--

\unrestrict cDmxPLdvpaVPanmV06gzcRkkyapq3RNaCuFjlT8oOlpin13lm1fBZbIJRlJFzIs

