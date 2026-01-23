--
-- PostgreSQL database dump
--

\restrict 2avCkakS18Hn1e41GplYpRss4lVYiidsikrfO99WOPFZfJTf3vlv5xO10jESPe0

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

-- Started on 2026-01-23 20:06:48 IST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- TOC entry 229 (class 1259 OID 19357)
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
-- TOC entry 228 (class 1259 OID 19356)
-- Name: app_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_user_user_id_seq OWNER TO postgres;

--
-- TOC entry 4325 (class 0 OID 0)
-- Dependencies: 228
-- Name: app_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_user_id_seq OWNED BY public.app_user.user_id;


--
-- TOC entry 225 (class 1259 OID 19325)
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
-- TOC entry 224 (class 1259 OID 19324)
-- Name: city_city_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.city_city_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.city_city_id_seq OWNER TO postgres;

--
-- TOC entry 4326 (class 0 OID 0)
-- Dependencies: 224
-- Name: city_city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.city_city_id_seq OWNED BY public.city.city_id;


--
-- TOC entry 223 (class 1259 OID 19318)
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
-- TOC entry 308 (class 1259 OID 20536)
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
-- TOC entry 307 (class 1259 OID 20535)
-- Name: coupon_coupon_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coupon_coupon_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.coupon_coupon_id_seq OWNER TO postgres;

--
-- TOC entry 4327 (class 0 OID 0)
-- Dependencies: 307
-- Name: coupon_coupon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coupon_coupon_id_seq OWNED BY public.coupon.coupon_id;


--
-- TOC entry 311 (class 1259 OID 20584)
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
-- TOC entry 310 (class 1259 OID 20583)
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coupon_redemption_redemption_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.coupon_redemption_redemption_id_seq OWNER TO postgres;

--
-- TOC entry 4328 (class 0 OID 0)
-- Dependencies: 310
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coupon_redemption_redemption_id_seq OWNED BY public.coupon_redemption.redemption_id;


--
-- TOC entry 309 (class 1259 OID 20562)
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
-- TOC entry 266 (class 1259 OID 19983)
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
-- TOC entry 265 (class 1259 OID 19982)
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatch_attempt_attempt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatch_attempt_attempt_id_seq OWNER TO postgres;

--
-- TOC entry 4329 (class 0 OID 0)
-- Dependencies: 265
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatch_attempt_attempt_id_seq OWNED BY public.dispatch_attempt.attempt_id;


--
-- TOC entry 270 (class 1259 OID 20025)
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
-- TOC entry 269 (class 1259 OID 20024)
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatcher_assignment_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatcher_assignment_assignment_id_seq OWNER TO postgres;

--
-- TOC entry 4330 (class 0 OID 0)
-- Dependencies: 269
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatcher_assignment_assignment_id_seq OWNED BY public.dispatcher_assignment.assignment_id;


--
-- TOC entry 315 (class 1259 OID 20634)
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
-- TOC entry 314 (class 1259 OID 20633)
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_progress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_incentive_progress_id_seq OWNER TO postgres;

--
-- TOC entry 4331 (class 0 OID 0)
-- Dependencies: 314
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_progress_id_seq OWNED BY public.driver_incentive_progress.id;


--
-- TOC entry 317 (class 1259 OID 20656)
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
-- TOC entry 316 (class 1259 OID 20655)
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_reward_reward_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_incentive_reward_reward_id_seq OWNER TO postgres;

--
-- TOC entry 4332 (class 0 OID 0)
-- Dependencies: 316
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_reward_reward_id_seq OWNED BY public.driver_incentive_reward.reward_id;


--
-- TOC entry 313 (class 1259 OID 20609)
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
-- TOC entry 312 (class 1259 OID 20608)
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_incentive_scheme_scheme_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_incentive_scheme_scheme_id_seq OWNER TO postgres;

--
-- TOC entry 4333 (class 0 OID 0)
-- Dependencies: 312
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_incentive_scheme_scheme_id_seq OWNED BY public.driver_incentive_scheme.scheme_id;


--
-- TOC entry 252 (class 1259 OID 19783)
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
-- TOC entry 254 (class 1259 OID 19794)
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
-- TOC entry 253 (class 1259 OID 19793)
-- Name: driver_location_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_location_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_location_history_id_seq OWNER TO postgres;

--
-- TOC entry 4334 (class 0 OID 0)
-- Dependencies: 253
-- Name: driver_location_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_location_history_id_seq OWNED BY public.driver_location_history.id;


--
-- TOC entry 239 (class 1259 OID 19535)
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
-- TOC entry 304 (class 1259 OID 20505)
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
-- TOC entry 251 (class 1259 OID 19754)
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
-- TOC entry 250 (class 1259 OID 19753)
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_shift_shift_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_shift_shift_id_seq OWNER TO postgres;

--
-- TOC entry 4335 (class 0 OID 0)
-- Dependencies: 250
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_shift_shift_id_seq OWNED BY public.driver_shift.shift_id;


--
-- TOC entry 249 (class 1259 OID 19724)
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
-- TOC entry 248 (class 1259 OID 19723)
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_vehicle_assignment_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_vehicle_assignment_assignment_id_seq OWNER TO postgres;

--
-- TOC entry 4336 (class 0 OID 0)
-- Dependencies: 248
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_vehicle_assignment_assignment_id_seq OWNED BY public.driver_vehicle_assignment.assignment_id;


--
-- TOC entry 279 (class 1259 OID 20141)
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
-- TOC entry 330 (class 1259 OID 20902)
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
-- TOC entry 329 (class 1259 OID 20901)
-- Name: driver_work_availability_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_work_availability_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_work_availability_id_seq OWNER TO postgres;

--
-- TOC entry 4337 (class 0 OID 0)
-- Dependencies: 329
-- Name: driver_work_availability_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_work_availability_id_seq OWNED BY public.driver_work_availability.id;


--
-- TOC entry 256 (class 1259 OID 19806)
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
-- TOC entry 255 (class 1259 OID 19805)
-- Name: fare_config_fare_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fare_config_fare_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fare_config_fare_id_seq OWNER TO postgres;

--
-- TOC entry 4338 (class 0 OID 0)
-- Dependencies: 255
-- Name: fare_config_fare_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fare_config_fare_id_seq OWNED BY public.fare_config.fare_id;


--
-- TOC entry 241 (class 1259 OID 19575)
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
-- TOC entry 328 (class 1259 OID 20875)
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
-- TOC entry 324 (class 1259 OID 20799)
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
-- TOC entry 323 (class 1259 OID 20798)
-- Name: fleet_document_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_document_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fleet_document_document_id_seq OWNER TO postgres;

--
-- TOC entry 4339 (class 0 OID 0)
-- Dependencies: 323
-- Name: fleet_document_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_document_document_id_seq OWNED BY public.fleet_document.document_id;


--
-- TOC entry 243 (class 1259 OID 19617)
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
-- TOC entry 242 (class 1259 OID 19616)
-- Name: fleet_driver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_driver_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fleet_driver_id_seq OWNER TO postgres;

--
-- TOC entry 4340 (class 0 OID 0)
-- Dependencies: 242
-- Name: fleet_driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_driver_id_seq OWNED BY public.fleet_driver.id;


--
-- TOC entry 240 (class 1259 OID 19574)
-- Name: fleet_fleet_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_fleet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fleet_fleet_id_seq OWNER TO postgres;

--
-- TOC entry 4341 (class 0 OID 0)
-- Dependencies: 240
-- Name: fleet_fleet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_fleet_id_seq OWNED BY public.fleet.fleet_id;


--
-- TOC entry 291 (class 1259 OID 20299)
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
-- TOC entry 290 (class 1259 OID 20298)
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fleet_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fleet_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 4342 (class 0 OID 0)
-- Dependencies: 290
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fleet_ledger_entry_id_seq OWNED BY public.fleet_ledger.entry_id;


--
-- TOC entry 301 (class 1259 OID 20450)
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
-- TOC entry 300 (class 1259 OID 20449)
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lost_item_report_report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lost_item_report_report_id_seq OWNER TO postgres;

--
-- TOC entry 4343 (class 0 OID 0)
-- Dependencies: 300
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lost_item_report_report_id_seq OWNED BY public.lost_item_report.report_id;


--
-- TOC entry 212 (class 1259 OID 19238)
-- Name: lu_account_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_account_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_account_status OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 19231)
-- Name: lu_approval_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_approval_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_approval_status OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 19294)
-- Name: lu_coupon_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_coupon_type (
    type_code text NOT NULL
);


ALTER TABLE public.lu_coupon_type OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 19245)
-- Name: lu_driver_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_driver_type (
    type_code text NOT NULL
);


ALTER TABLE public.lu_driver_type OWNER TO postgres;

--
-- TOC entry 325 (class 1259 OID 20833)
-- Name: lu_fleet_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_fleet_type (
    fleet_type_code text NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.lu_fleet_type OWNER TO postgres;

--
-- TOC entry 321 (class 1259 OID 20741)
-- Name: lu_fuel_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_fuel_type (
    fuel_code character varying(20) NOT NULL,
    description character varying(100) NOT NULL
);


ALTER TABLE public.lu_fuel_type OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 19224)
-- Name: lu_gender; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_gender (
    gender_code text NOT NULL
);


ALTER TABLE public.lu_gender OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 19273)
-- Name: lu_payment_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_payment_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_payment_status OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 19287)
-- Name: lu_settlement_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_settlement_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_settlement_status OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 19280)
-- Name: lu_support_ticket_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_support_ticket_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_support_ticket_status OWNER TO postgres;

--
-- TOC entry 209 (class 1259 OID 19217)
-- Name: lu_tenant_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_tenant_role (
    role_code text NOT NULL
);


ALTER TABLE public.lu_tenant_role OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 19266)
-- Name: lu_trip_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_trip_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_trip_status OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 19252)
-- Name: lu_vehicle_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_vehicle_category (
    category_code text NOT NULL
);


ALTER TABLE public.lu_vehicle_category OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 19259)
-- Name: lu_vehicle_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lu_vehicle_status (
    status_code text NOT NULL
);


ALTER TABLE public.lu_vehicle_status OWNER TO postgres;

--
-- TOC entry 278 (class 1259 OID 20112)
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
-- TOC entry 277 (class 1259 OID 20111)
-- Name: payment_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payment_payment_id_seq OWNER TO postgres;

--
-- TOC entry 4344 (class 0 OID 0)
-- Dependencies: 277
-- Name: payment_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_payment_id_seq OWNED BY public.payment.payment_id;


--
-- TOC entry 287 (class 1259 OID 20254)
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
-- TOC entry 286 (class 1259 OID 20253)
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.platform_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 4345 (class 0 OID 0)
-- Dependencies: 286
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_ledger_entry_id_seq OWNED BY public.platform_ledger.entry_id;


--
-- TOC entry 280 (class 1259 OID 20163)
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
-- TOC entry 258 (class 1259 OID 19843)
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
-- TOC entry 257 (class 1259 OID 19842)
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pricing_time_rule_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pricing_time_rule_rule_id_seq OWNER TO postgres;

--
-- TOC entry 4346 (class 0 OID 0)
-- Dependencies: 257
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pricing_time_rule_rule_id_seq OWNED BY public.pricing_time_rule.rule_id;


--
-- TOC entry 285 (class 1259 OID 20234)
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
-- TOC entry 284 (class 1259 OID 20233)
-- Name: refund_refund_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.refund_refund_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.refund_refund_id_seq OWNER TO postgres;

--
-- TOC entry 4347 (class 0 OID 0)
-- Dependencies: 284
-- Name: refund_refund_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.refund_refund_id_seq OWNED BY public.refund.refund_id;


--
-- TOC entry 320 (class 1259 OID 20689)
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
-- TOC entry 319 (class 1259 OID 20688)
-- Name: ride_request_request_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ride_request_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ride_request_request_id_seq OWNER TO postgres;

--
-- TOC entry 4348 (class 0 OID 0)
-- Dependencies: 319
-- Name: ride_request_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ride_request_request_id_seq OWNED BY public.ride_request.request_id;


--
-- TOC entry 305 (class 1259 OID 20515)
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
-- TOC entry 293 (class 1259 OID 20324)
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
-- TOC entry 292 (class 1259 OID 20323)
-- Name: sos_event_sos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sos_event_sos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sos_event_sos_id_seq OWNER TO postgres;

--
-- TOC entry 4349 (class 0 OID 0)
-- Dependencies: 292
-- Name: sos_event_sos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sos_event_sos_id_seq OWNED BY public.sos_event.sos_id;


--
-- TOC entry 295 (class 1259 OID 20352)
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
-- TOC entry 299 (class 1259 OID 20427)
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
-- TOC entry 298 (class 1259 OID 20426)
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_assignment_history_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_ticket_assignment_history_history_id_seq OWNER TO postgres;

--
-- TOC entry 4350 (class 0 OID 0)
-- Dependencies: 298
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_assignment_history_history_id_seq OWNED BY public.support_ticket_assignment_history.history_id;


--
-- TOC entry 297 (class 1259 OID 20397)
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
-- TOC entry 296 (class 1259 OID 20396)
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_conversation_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_ticket_conversation_message_id_seq OWNER TO postgres;

--
-- TOC entry 4351 (class 0 OID 0)
-- Dependencies: 296
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_conversation_message_id_seq OWNED BY public.support_ticket_conversation.message_id;


--
-- TOC entry 294 (class 1259 OID 20351)
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.support_ticket_ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_ticket_ticket_id_seq OWNER TO postgres;

--
-- TOC entry 4352 (class 0 OID 0)
-- Dependencies: 294
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.support_ticket_ticket_id_seq OWNED BY public.support_ticket.ticket_id;


--
-- TOC entry 262 (class 1259 OID 19894)
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
-- TOC entry 261 (class 1259 OID 19893)
-- Name: surge_event_surge_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.surge_event_surge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.surge_event_surge_id_seq OWNER TO postgres;

--
-- TOC entry 4353 (class 0 OID 0)
-- Dependencies: 261
-- Name: surge_event_surge_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.surge_event_surge_id_seq OWNED BY public.surge_event.surge_id;


--
-- TOC entry 260 (class 1259 OID 19871)
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
-- TOC entry 259 (class 1259 OID 19870)
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.surge_zone_surge_zone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.surge_zone_surge_zone_id_seq OWNER TO postgres;

--
-- TOC entry 4354 (class 0 OID 0)
-- Dependencies: 259
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.surge_zone_surge_zone_id_seq OWNED BY public.surge_zone.surge_zone_id;


--
-- TOC entry 222 (class 1259 OID 19302)
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
-- TOC entry 234 (class 1259 OID 19430)
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
-- TOC entry 233 (class 1259 OID 19429)
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_admin_tenant_admin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_admin_tenant_admin_id_seq OWNER TO postgres;

--
-- TOC entry 4355 (class 0 OID 0)
-- Dependencies: 233
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_admin_tenant_admin_id_seq OWNED BY public.tenant_admin.tenant_admin_id;


--
-- TOC entry 236 (class 1259 OID 19486)
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
-- TOC entry 235 (class 1259 OID 19460)
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
-- TOC entry 327 (class 1259 OID 20851)
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
-- TOC entry 326 (class 1259 OID 20850)
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_document_tenant_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_document_tenant_document_id_seq OWNER TO postgres;

--
-- TOC entry 4356 (class 0 OID 0)
-- Dependencies: 326
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_document_tenant_document_id_seq OWNED BY public.tenant_document.tenant_document_id;


--
-- TOC entry 289 (class 1259 OID 20274)
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
-- TOC entry 288 (class 1259 OID 20273)
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_ledger_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_ledger_entry_id_seq OWNER TO postgres;

--
-- TOC entry 4357 (class 0 OID 0)
-- Dependencies: 288
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_ledger_entry_id_seq OWNED BY public.tenant_ledger.entry_id;


--
-- TOC entry 306 (class 1259 OID 20525)
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
-- TOC entry 283 (class 1259 OID 20204)
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
-- TOC entry 282 (class 1259 OID 20203)
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_settlement_settlement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_settlement_settlement_id_seq OWNER TO postgres;

--
-- TOC entry 4358 (class 0 OID 0)
-- Dependencies: 282
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_settlement_settlement_id_seq OWNED BY public.tenant_settlement.settlement_id;


--
-- TOC entry 238 (class 1259 OID 19513)
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
-- TOC entry 237 (class 1259 OID 19512)
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_tax_rule_tax_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_tax_rule_tax_id_seq OWNER TO postgres;

--
-- TOC entry 4359 (class 0 OID 0)
-- Dependencies: 237
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_tax_rule_tax_id_seq OWNED BY public.tenant_tax_rule.tax_id;


--
-- TOC entry 221 (class 1259 OID 19301)
-- Name: tenant_tenant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_tenant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_tenant_id_seq OWNER TO postgres;

--
-- TOC entry 4360 (class 0 OID 0)
-- Dependencies: 221
-- Name: tenant_tenant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_tenant_id_seq OWNED BY public.tenant.tenant_id;


--
-- TOC entry 281 (class 1259 OID 20181)
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
-- TOC entry 264 (class 1259 OID 19922)
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
-- TOC entry 272 (class 1259 OID 20065)
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
-- TOC entry 271 (class 1259 OID 20064)
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_cancellation_cancel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_cancellation_cancel_id_seq OWNER TO postgres;

--
-- TOC entry 4361 (class 0 OID 0)
-- Dependencies: 271
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_cancellation_cancel_id_seq OWNED BY public.trip_cancellation.cancel_id;


--
-- TOC entry 276 (class 1259 OID 20099)
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
-- TOC entry 275 (class 1259 OID 20098)
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_fare_breakdown_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_fare_breakdown_id_seq OWNER TO postgres;

--
-- TOC entry 4362 (class 0 OID 0)
-- Dependencies: 275
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_fare_breakdown_id_seq OWNED BY public.trip_fare_breakdown.id;


--
-- TOC entry 274 (class 1259 OID 20085)
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
-- TOC entry 273 (class 1259 OID 20084)
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_otp_otp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_otp_otp_id_seq OWNER TO postgres;

--
-- TOC entry 4363 (class 0 OID 0)
-- Dependencies: 273
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_otp_otp_id_seq OWNED BY public.trip_otp.otp_id;


--
-- TOC entry 303 (class 1259 OID 20480)
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
-- TOC entry 302 (class 1259 OID 20479)
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_rating_rating_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_rating_rating_id_seq OWNER TO postgres;

--
-- TOC entry 4364 (class 0 OID 0)
-- Dependencies: 302
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_rating_rating_id_seq OWNED BY public.trip_rating.rating_id;


--
-- TOC entry 268 (class 1259 OID 20013)
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
-- TOC entry 267 (class 1259 OID 20012)
-- Name: trip_route_point_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_route_point_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_route_point_id_seq OWNER TO postgres;

--
-- TOC entry 4365 (class 0 OID 0)
-- Dependencies: 267
-- Name: trip_route_point_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_route_point_id_seq OWNED BY public.trip_route_point.id;


--
-- TOC entry 263 (class 1259 OID 19921)
-- Name: trip_trip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_trip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_trip_id_seq OWNER TO postgres;

--
-- TOC entry 4366 (class 0 OID 0)
-- Dependencies: 263
-- Name: trip_trip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_trip_id_seq OWNED BY public.trip.trip_id;


--
-- TOC entry 318 (class 1259 OID 20675)
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
-- TOC entry 232 (class 1259 OID 19410)
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
-- TOC entry 231 (class 1259 OID 19409)
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_kyc_kyc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_kyc_kyc_id_seq OWNER TO postgres;

--
-- TOC entry 4367 (class 0 OID 0)
-- Dependencies: 231
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_kyc_kyc_id_seq OWNED BY public.user_kyc.kyc_id;


--
-- TOC entry 230 (class 1259 OID 19395)
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
-- TOC entry 245 (class 1259 OID 19647)
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
    updated_on timestamp with time zone
);


ALTER TABLE public.vehicle OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 19689)
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
-- TOC entry 246 (class 1259 OID 19688)
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_document_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_document_document_id_seq OWNER TO postgres;

--
-- TOC entry 4368 (class 0 OID 0)
-- Dependencies: 246
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_document_document_id_seq OWNED BY public.vehicle_document.document_id;


--
-- TOC entry 322 (class 1259 OID 20772)
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
-- TOC entry 244 (class 1259 OID 19646)
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_vehicle_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_vehicle_id_seq OWNER TO postgres;

--
-- TOC entry 4369 (class 0 OID 0)
-- Dependencies: 244
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_vehicle_id_seq OWNED BY public.vehicle.vehicle_id;


--
-- TOC entry 227 (class 1259 OID 19340)
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
-- TOC entry 226 (class 1259 OID 19339)
-- Name: zone_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zone_zone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zone_zone_id_seq OWNER TO postgres;

--
-- TOC entry 4370 (class 0 OID 0)
-- Dependencies: 226
-- Name: zone_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zone_zone_id_seq OWNED BY public.zone.zone_id;


--
-- TOC entry 3557 (class 2604 OID 19360)
-- Name: app_user user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN user_id SET DEFAULT nextval('public.app_user_user_id_seq'::regclass);


--
-- TOC entry 3553 (class 2604 OID 19328)
-- Name: city city_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.city ALTER COLUMN city_id SET DEFAULT nextval('public.city_city_id_seq'::regclass);


--
-- TOC entry 3642 (class 2604 OID 20539)
-- Name: coupon coupon_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coupon ALTER COLUMN coupon_id SET DEFAULT nextval('public.coupon_coupon_id_seq'::regclass);


--
-- TOC entry 3645 (class 2604 OID 20587)
-- Name: coupon_redemption redemption_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coupon_redemption ALTER COLUMN redemption_id SET DEFAULT nextval('public.coupon_redemption_redemption_id_seq'::regclass);


--
-- TOC entry 3598 (class 2604 OID 19986)
-- Name: dispatch_attempt attempt_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_attempt ALTER COLUMN attempt_id SET DEFAULT nextval('public.dispatch_attempt_attempt_id_seq'::regclass);


--
-- TOC entry 3601 (class 2604 OID 20028)
-- Name: dispatcher_assignment assignment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatcher_assignment ALTER COLUMN assignment_id SET DEFAULT nextval('public.dispatcher_assignment_assignment_id_seq'::regclass);


--
-- TOC entry 3649 (class 2604 OID 20637)
-- Name: driver_incentive_progress id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_progress ALTER COLUMN id SET DEFAULT nextval('public.driver_incentive_progress_id_seq'::regclass);


--
-- TOC entry 3653 (class 2604 OID 20659)
-- Name: driver_incentive_reward reward_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_reward ALTER COLUMN reward_id SET DEFAULT nextval('public.driver_incentive_reward_reward_id_seq'::regclass);


--
-- TOC entry 3647 (class 2604 OID 20612)
-- Name: driver_incentive_scheme scheme_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_incentive_scheme ALTER COLUMN scheme_id SET DEFAULT nextval('public.driver_incentive_scheme_scheme_id_seq'::regclass);


--
-- TOC entry 3586 (class 2604 OID 19797)
-- Name: driver_location_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_location_history ALTER COLUMN id SET DEFAULT nextval('public.driver_location_history_id_seq'::regclass);


--
-- TOC entry 3584 (class 2604 OID 19757)
-- Name: driver_shift shift_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_shift ALTER COLUMN shift_id SET DEFAULT nextval('public.driver_shift_shift_id_seq'::regclass);


--
-- TOC entry 3582 (class 2604 OID 19727)
-- Name: driver_vehicle_assignment assignment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_vehicle_assignment ALTER COLUMN assignment_id SET DEFAULT nextval('public.driver_vehicle_assignment_assignment_id_seq'::regclass);


--
-- TOC entry 3666 (class 2604 OID 20905)
-- Name: driver_work_availability id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver_work_availability ALTER COLUMN id SET DEFAULT nextval('public.driver_work_availability_id_seq'::regclass);


--
-- TOC entry 3587 (class 2604 OID 19809)
-- Name: fare_config fare_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fare_config ALTER COLUMN fare_id SET DEFAULT nextval('public.fare_config_fare_id_seq'::regclass);


--
-- TOC entry 3573 (class 2604 OID 19578)
-- Name: fleet fleet_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet ALTER COLUMN fleet_id SET DEFAULT nextval('public.fleet_fleet_id_seq'::regclass);


--
-- TOC entry 3660 (class 2604 OID 20802)
-- Name: fleet_document document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_document ALTER COLUMN document_id SET DEFAULT nextval('public.fleet_document_document_id_seq'::regclass);


--
-- TOC entry 3576 (class 2604 OID 19620)
-- Name: fleet_driver id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_driver ALTER COLUMN id SET DEFAULT nextval('public.fleet_driver_id_seq'::regclass);


--
-- TOC entry 3627 (class 2604 OID 20302)
-- Name: fleet_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fleet_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.fleet_ledger_entry_id_seq'::regclass);


--
-- TOC entry 3638 (class 2604 OID 20453)
-- Name: lost_item_report report_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lost_item_report ALTER COLUMN report_id SET DEFAULT nextval('public.lost_item_report_report_id_seq'::regclass);


--
-- TOC entry 3610 (class 2604 OID 20115)
-- Name: payment payment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment ALTER COLUMN payment_id SET DEFAULT nextval('public.payment_payment_id_seq'::regclass);


--
-- TOC entry 3623 (class 2604 OID 20257)
-- Name: platform_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.platform_ledger_entry_id_seq'::regclass);


--
-- TOC entry 3589 (class 2604 OID 19846)
-- Name: pricing_time_rule rule_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pricing_time_rule ALTER COLUMN rule_id SET DEFAULT nextval('public.pricing_time_rule_rule_id_seq'::regclass);


--
-- TOC entry 3621 (class 2604 OID 20237)
-- Name: refund refund_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refund ALTER COLUMN refund_id SET DEFAULT nextval('public.refund_refund_id_seq'::regclass);


--
-- TOC entry 3657 (class 2604 OID 20692)
-- Name: ride_request request_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ride_request ALTER COLUMN request_id SET DEFAULT nextval('public.ride_request_request_id_seq'::regclass);


--
-- TOC entry 3629 (class 2604 OID 20327)
-- Name: sos_event sos_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sos_event ALTER COLUMN sos_id SET DEFAULT nextval('public.sos_event_sos_id_seq'::regclass);


--
-- TOC entry 3631 (class 2604 OID 20355)
-- Name: support_ticket ticket_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket ALTER COLUMN ticket_id SET DEFAULT nextval('public.support_ticket_ticket_id_seq'::regclass);


--
-- TOC entry 3635 (class 2604 OID 20430)
-- Name: support_ticket_assignment_history history_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket_assignment_history ALTER COLUMN history_id SET DEFAULT nextval('public.support_ticket_assignment_history_history_id_seq'::regclass);


--
-- TOC entry 3633 (class 2604 OID 20400)
-- Name: support_ticket_conversation message_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_ticket_conversation ALTER COLUMN message_id SET DEFAULT nextval('public.support_ticket_conversation_message_id_seq'::regclass);


--
-- TOC entry 3593 (class 2604 OID 19897)
-- Name: surge_event surge_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surge_event ALTER COLUMN surge_id SET DEFAULT nextval('public.surge_event_surge_id_seq'::regclass);


--
-- TOC entry 3591 (class 2604 OID 19874)
-- Name: surge_zone surge_zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surge_zone ALTER COLUMN surge_zone_id SET DEFAULT nextval('public.surge_zone_surge_zone_id_seq'::regclass);


--
-- TOC entry 3550 (class 2604 OID 19305)
-- Name: tenant tenant_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant ALTER COLUMN tenant_id SET DEFAULT nextval('public.tenant_tenant_id_seq'::regclass);


--
-- TOC entry 3563 (class 2604 OID 19433)
-- Name: tenant_admin tenant_admin_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_admin ALTER COLUMN tenant_admin_id SET DEFAULT nextval('public.tenant_admin_tenant_admin_id_seq'::regclass);


--
-- TOC entry 3662 (class 2604 OID 20854)
-- Name: tenant_document tenant_document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_document ALTER COLUMN tenant_document_id SET DEFAULT nextval('public.tenant_document_tenant_document_id_seq'::regclass);


--
-- TOC entry 3625 (class 2604 OID 20277)
-- Name: tenant_ledger entry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_ledger ALTER COLUMN entry_id SET DEFAULT nextval('public.tenant_ledger_entry_id_seq'::regclass);


--
-- TOC entry 3619 (class 2604 OID 20207)
-- Name: tenant_settlement settlement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_settlement ALTER COLUMN settlement_id SET DEFAULT nextval('public.tenant_settlement_settlement_id_seq'::regclass);


--
-- TOC entry 3568 (class 2604 OID 19516)
-- Name: tenant_tax_rule tax_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_tax_rule ALTER COLUMN tax_id SET DEFAULT nextval('public.tenant_tax_rule_tax_id_seq'::regclass);


--
-- TOC entry 3595 (class 2604 OID 19925)
-- Name: trip trip_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip ALTER COLUMN trip_id SET DEFAULT nextval('public.trip_trip_id_seq'::regclass);


--
-- TOC entry 3603 (class 2604 OID 20068)
-- Name: trip_cancellation cancel_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_cancellation ALTER COLUMN cancel_id SET DEFAULT nextval('public.trip_cancellation_cancel_id_seq'::regclass);


--
-- TOC entry 3608 (class 2604 OID 20102)
-- Name: trip_fare_breakdown id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_fare_breakdown ALTER COLUMN id SET DEFAULT nextval('public.trip_fare_breakdown_id_seq'::regclass);


--
-- TOC entry 3605 (class 2604 OID 20088)
-- Name: trip_otp otp_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_otp ALTER COLUMN otp_id SET DEFAULT nextval('public.trip_otp_otp_id_seq'::regclass);


--
-- TOC entry 3639 (class 2604 OID 20483)
-- Name: trip_rating rating_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_rating ALTER COLUMN rating_id SET DEFAULT nextval('public.trip_rating_rating_id_seq'::regclass);


--
-- TOC entry 3600 (class 2604 OID 20016)
-- Name: trip_route_point id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip_route_point ALTER COLUMN id SET DEFAULT nextval('public.trip_route_point_id_seq'::regclass);


--
-- TOC entry 3561 (class 2604 OID 19413)
-- Name: user_kyc kyc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_kyc ALTER COLUMN kyc_id SET DEFAULT nextval('public.user_kyc_kyc_id_seq'::regclass);


--
-- TOC entry 3578 (class 2604 OID 19650)
-- Name: vehicle vehicle_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN vehicle_id SET DEFAULT nextval('public.vehicle_vehicle_id_seq'::regclass);


--
-- TOC entry 3580 (class 2604 OID 19692)
-- Name: vehicle_document document_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_document ALTER COLUMN document_id SET DEFAULT nextval('public.vehicle_document_document_id_seq'::regclass);


--
-- TOC entry 3555 (class 2604 OID 19343)
-- Name: zone zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone ALTER COLUMN zone_id SET DEFAULT nextval('public.zone_zone_id_seq'::regclass);


--
-- TOC entry 4218 (class 0 OID 19357)
-- Dependencies: 229
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
\.


--
-- TOC entry 4214 (class 0 OID 19325)
-- Dependencies: 225
-- Data for Name: city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.city (city_id, country_code, name, timezone, currency, created_by, created_on, updated_by, updated_on) FROM stdin;
1	IN	Hyderabad	Asia/Kolkata	INR	\N	2026-01-13 16:16:53.621268+05:30	\N	\N
\.


--
-- TOC entry 4212 (class 0 OID 19318)
-- Dependencies: 223
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.country (country_code, name, phone_code, default_timezone, default_currency, created_by, created_on, updated_by, updated_on) FROM stdin;
IN	India	+91	Asia/Kolkata	INR	\N	2026-01-13 16:15:27.367924+05:30	\N	\N
\.


--
-- TOC entry 4297 (class 0 OID 20536)
-- Dependencies: 308
-- Data for Name: coupon; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon (coupon_id, code, coupon_type, value, start_date, end_date, max_uses, per_user_limit, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4300 (class 0 OID 20584)
-- Dependencies: 311
-- Data for Name: coupon_redemption; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon_redemption (redemption_id, coupon_id, user_id, trip_id, redeemed_at, created_on) FROM stdin;
\.


--
-- TOC entry 4298 (class 0 OID 20562)
-- Dependencies: 309
-- Data for Name: coupon_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coupon_tenant (coupon_id, tenant_id, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4255 (class 0 OID 19983)
-- Dependencies: 266
-- Data for Name: dispatch_attempt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dispatch_attempt (attempt_id, trip_id, driver_id, sent_at, responded_at, response, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	4	2026-01-19 16:45:16.498276+05:30	\N	SENT	9	2026-01-19 16:45:16.466253+05:30	\N	\N
\.


--
-- TOC entry 4259 (class 0 OID 20025)
-- Dependencies: 270
-- Data for Name: dispatcher_assignment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dispatcher_assignment (assignment_id, dispatcher_id, tenant_id, city_id, zone_id, start_time, end_time, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4304 (class 0 OID 20634)
-- Dependencies: 315
-- Data for Name: driver_incentive_progress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_progress (id, scheme_id, driver_id, progress_value, achieved, updated_on) FROM stdin;
\.


--
-- TOC entry 4306 (class 0 OID 20656)
-- Dependencies: 317
-- Data for Name: driver_incentive_reward; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_reward (reward_id, scheme_id, driver_id, amount, paid, created_on) FROM stdin;
\.


--
-- TOC entry 4302 (class 0 OID 20609)
-- Dependencies: 313
-- Data for Name: driver_incentive_scheme; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_incentive_scheme (scheme_id, tenant_id, name, description, start_date, end_date, criteria, reward_amount, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4241 (class 0 OID 19783)
-- Dependencies: 252
-- Data for Name: driver_location; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_location (driver_id, latitude, longitude, last_updated) FROM stdin;
4	12.970000	77.980000	2026-01-19 16:27:05.501587+05:30
\.


--
-- TOC entry 4243 (class 0 OID 19794)
-- Dependencies: 254
-- Data for Name: driver_location_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_location_history (id, driver_id, latitude, longitude, recorded_at) FROM stdin;
\.


--
-- TOC entry 4228 (class 0 OID 19535)
-- Dependencies: 239
-- Data for Name: driver_profile; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_profile (driver_id, tenant_id, driver_type, approval_status, rating, created_by, created_on, updated_by, updated_on, alternate_phone_number, allowed_vehicle_categories) FROM stdin;
4	1	INDEPENDENT	APPROVED	4.90	\N	2026-01-19 16:04:12.748309+05:30	\N	\N	\N	\N
14	1	INDEPENDENT	PENDING	5.00	14	2026-01-21 18:53:57.947313+05:30	\N	\N	+919876543210	\N
15	1	INDEPENDENT	PENDING	5.00	15	2026-01-21 19:03:06.318396+05:30	\N	\N	\N	\N
6	1	INDEPENDENT	APPROVED	5.00	6	2026-01-20 15:54:01.245159+05:30	\N	2026-01-22 10:55:45.141912+05:30	\N	{"CAR,BIKE"}
7	1	INDEPENDENT	REJECTED	5.00	7	2026-01-19 18:24:41.475404+05:30	\N	2026-01-22 10:58:29.647204+05:30	\N	\N
\.


--
-- TOC entry 4293 (class 0 OID 20505)
-- Dependencies: 304
-- Data for Name: driver_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_rating_summary (driver_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 4240 (class 0 OID 19754)
-- Dependencies: 251
-- Data for Name: driver_shift; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_shift (shift_id, driver_id, tenant_id, status, started_at, ended_at, last_latitude, last_longitude, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	1	ACTIVE	2026-01-19 16:22:19.462453+05:30	\N	12.970000	77.980000	\N	2026-01-19 16:22:19.462453+05:30	\N	\N
\.


--
-- TOC entry 4238 (class 0 OID 19724)
-- Dependencies: 249
-- Data for Name: driver_vehicle_assignment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_vehicle_assignment (assignment_id, driver_id, vehicle_id, start_time, end_time, created_by, created_on, updated_by, updated_on) FROM stdin;
1	4	2	2026-01-19 16:11:49.441969+05:30	\N	\N	2026-01-19 16:11:49.441969+05:30	\N	\N
\.


--
-- TOC entry 4268 (class 0 OID 20141)
-- Dependencies: 279
-- Data for Name: driver_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_wallet (driver_id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4319 (class 0 OID 20902)
-- Dependencies: 330
-- Data for Name: driver_work_availability; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver_work_availability (id, driver_id, fleet_id, date, is_available, note, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4245 (class 0 OID 19806)
-- Dependencies: 256
-- Data for Name: fare_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fare_config (fare_id, tenant_id, city_id, vehicle_category, base_fare, per_km, per_minute, minimum_fare, created_by, created_on, updated_by, updated_on) FROM stdin;
1	1	1	BIKE	30.00	12.00	1.00	50.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
2	2	1	AUTO	20.00	8.00	1.00	40.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
3	3	1	SEDAN	50.00	15.00	2.00	80.00	\N	2026-01-19 14:56:13.479616+05:30	\N	\N
4	1	1	AUTO	30.00	10.00	2.00	50.00	\N	2026-01-19 16:27:28.702004+05:30	\N	\N
\.


--
-- TOC entry 4230 (class 0 OID 19575)
-- Dependencies: 241
-- Data for Name: fleet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet (fleet_id, tenant_id, owner_user_id, fleet_name, status, approval_status, created_by, created_on, updated_by, updated_on, fleet_type) FROM stdin;
1	1	6	Driver 6 Fleet	ACTIVE	APPROVED	3	2026-01-22 10:55:45.141912+05:30	\N	\N	INDIVIDUAL
2	1	15	Fleet0	ACTIVE	PENDING	15	2026-01-22 12:03:29.712215+05:30	\N	\N	BUSINESS
\.


--
-- TOC entry 4317 (class 0 OID 20875)
-- Dependencies: 328
-- Data for Name: fleet_city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_city (fleet_id, city_id, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4313 (class 0 OID 20799)
-- Dependencies: 324
-- Data for Name: fleet_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_document (document_id, fleet_id, document_type, file_url, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on) FROM stdin;
1	2	Something	oollllkjhg	PENDING	\N	\N	15	2026-01-22 12:03:29.712215+05:30	\N	\N
\.


--
-- TOC entry 4232 (class 0 OID 19617)
-- Dependencies: 243
-- Data for Name: fleet_driver; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_driver (id, fleet_id, driver_id, start_date, end_date, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4280 (class 0 OID 20299)
-- Dependencies: 291
-- Data for Name: fleet_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fleet_ledger (entry_id, fleet_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4290 (class 0 OID 20450)
-- Dependencies: 301
-- Data for Name: lost_item_report; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lost_item_report (report_id, trip_id, user_id, description, status, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4201 (class 0 OID 19238)
-- Dependencies: 212
-- Data for Name: lu_account_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_account_status (status_code) FROM stdin;
ACTIVE
INACTIVE
SUSPENDED
CLOSED
\.


--
-- TOC entry 4200 (class 0 OID 19231)
-- Dependencies: 211
-- Data for Name: lu_approval_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_approval_status (status_code) FROM stdin;
PENDING
APPROVED
REJECTED
\.


--
-- TOC entry 4209 (class 0 OID 19294)
-- Dependencies: 220
-- Data for Name: lu_coupon_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_coupon_type (type_code) FROM stdin;
FLAT
PERCENTAGE
\.


--
-- TOC entry 4202 (class 0 OID 19245)
-- Dependencies: 213
-- Data for Name: lu_driver_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_driver_type (type_code) FROM stdin;
INDEPENDENT
FLEET
\.


--
-- TOC entry 4314 (class 0 OID 20833)
-- Dependencies: 325
-- Data for Name: lu_fleet_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_fleet_type (fleet_type_code, description) FROM stdin;
INDIVIDUAL	Single driver owned fleet
BUSINESS	Company or aggregator fleet
\.


--
-- TOC entry 4310 (class 0 OID 20741)
-- Dependencies: 321
-- Data for Name: lu_fuel_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_fuel_type (fuel_code, description) FROM stdin;
PETROL	Petrol
DIESEL	Diesel
CNG	Compressed Natural Gas
EV	Electric Vehicle
\.


--
-- TOC entry 4199 (class 0 OID 19224)
-- Dependencies: 210
-- Data for Name: lu_gender; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_gender (gender_code) FROM stdin;
MALE
FEMALE
OTHER
PREFER_NOT_TO_SAY
\.


--
-- TOC entry 4206 (class 0 OID 19273)
-- Dependencies: 217
-- Data for Name: lu_payment_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_payment_status (status_code) FROM stdin;
PENDING
SUCCESS
FAILED
REFUNDED
\.


--
-- TOC entry 4208 (class 0 OID 19287)
-- Dependencies: 219
-- Data for Name: lu_settlement_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_settlement_status (status_code) FROM stdin;
PENDING
COMPLETED
FAILED
\.


--
-- TOC entry 4207 (class 0 OID 19280)
-- Dependencies: 218
-- Data for Name: lu_support_ticket_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_support_ticket_status (status_code) FROM stdin;
OPEN
IN_PROGRESS
RESOLVED
CLOSED
\.


--
-- TOC entry 4198 (class 0 OID 19217)
-- Dependencies: 209
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
-- TOC entry 4205 (class 0 OID 19266)
-- Dependencies: 216
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
-- TOC entry 4203 (class 0 OID 19252)
-- Dependencies: 214
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
-- TOC entry 4204 (class 0 OID 19259)
-- Dependencies: 215
-- Data for Name: lu_vehicle_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lu_vehicle_status (status_code) FROM stdin;
ACTIVE
INACTIVE
BLOCKED
\.


--
-- TOC entry 4267 (class 0 OID 20112)
-- Dependencies: 278
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment (payment_id, trip_id, amount, currency, payment_mode, status, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4276 (class 0 OID 20254)
-- Dependencies: 287
-- Data for Name: platform_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.platform_ledger (entry_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4269 (class 0 OID 20163)
-- Dependencies: 280
-- Data for Name: platform_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.platform_wallet (id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4247 (class 0 OID 19843)
-- Dependencies: 258
-- Data for Name: pricing_time_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pricing_time_rule (rule_id, tenant_id, city_id, rule_type, start_time, end_time, multiplier, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4274 (class 0 OID 20234)
-- Dependencies: 285
-- Data for Name: refund; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.refund (refund_id, payment_id, amount, reason, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4309 (class 0 OID 20689)
-- Dependencies: 320
-- Data for Name: ride_request; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ride_request (request_id, rider_id, city_id, pickup_lat, pickup_lng, drop_lat, drop_lng, status, created_on) FROM stdin;
1	9	1	12.980000	77.890000	12.960000	77.850000	CONFIRMED	2026-01-19 16:44:14.0416+05:30
\.


--
-- TOC entry 4294 (class 0 OID 20515)
-- Dependencies: 305
-- Data for Name: rider_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rider_rating_summary (rider_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 4282 (class 0 OID 20324)
-- Dependencies: 293
-- Data for Name: sos_event; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sos_event (sos_id, trip_id, triggered_by, latitude, longitude, triggered_at, resolved_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4284 (class 0 OID 20352)
-- Dependencies: 295
-- Data for Name: support_ticket; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket (ticket_id, user_id, trip_id, sos_id, issue_type, severity, status, assigned_to, assigned_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4288 (class 0 OID 20427)
-- Dependencies: 299
-- Data for Name: support_ticket_assignment_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket_assignment_history (history_id, ticket_id, assigned_to, assigned_at, unassigned_at, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4286 (class 0 OID 20397)
-- Dependencies: 297
-- Data for Name: support_ticket_conversation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_ticket_conversation (message_id, ticket_id, sender_id, message_text, sent_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4251 (class 0 OID 19894)
-- Dependencies: 262
-- Data for Name: surge_event; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.surge_event (surge_id, tenant_id, surge_zone_id, multiplier, demand_index, supply_index, started_at, ended_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4249 (class 0 OID 19871)
-- Dependencies: 260
-- Data for Name: surge_zone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.surge_zone (surge_zone_id, zone_id, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4211 (class 0 OID 19302)
-- Dependencies: 222
-- Data for Name: tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant (tenant_id, name, default_currency, default_timezone, status, created_by, created_on, updated_by, updated_on, tenant_code) FROM stdin;
1	RideSharing India	INR	Asia/Kolkata	ACTIVE	\N	2026-01-13 16:16:53.621268+05:30	\N	\N	TENANT_1
2	DemoTenantIndia	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 11:28:55.81198+05:30	\N	\N	TENANT_2
3	Quick Rides	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_3
4	City Taxi	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_4
5	Premuim Cabs	INR	Asia/Kolkata	ACTIVE	\N	2026-01-19 14:48:06.810646+05:30	\N	\N	TENANT_5
\.


--
-- TOC entry 4223 (class 0 OID 19430)
-- Dependencies: 234
-- Data for Name: tenant_admin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_admin (tenant_admin_id, tenant_id, user_id, is_primary, created_by, created_on, updated_by, updated_on) FROM stdin;
1	1	3	t	\N	2026-01-19 11:30:13.829753+05:30	\N	\N
\.


--
-- TOC entry 4225 (class 0 OID 19486)
-- Dependencies: 236
-- Data for Name: tenant_city; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_city (tenant_id, city_id, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4224 (class 0 OID 19460)
-- Dependencies: 235
-- Data for Name: tenant_country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_country (tenant_id, country_code, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4316 (class 0 OID 20851)
-- Dependencies: 327
-- Data for Name: tenant_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_document (tenant_document_id, tenant_id, document_type, file_name, file_url, file_hash, is_active, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4278 (class 0 OID 20274)
-- Dependencies: 289
-- Data for Name: tenant_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_ledger (entry_id, tenant_id, trip_id, amount, entry_type, created_by, created_on) FROM stdin;
\.


--
-- TOC entry 4295 (class 0 OID 20525)
-- Dependencies: 306
-- Data for Name: tenant_rating_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_rating_summary (tenant_id, avg_rating, total_ratings, updated_on) FROM stdin;
\.


--
-- TOC entry 4272 (class 0 OID 20204)
-- Dependencies: 283
-- Data for Name: tenant_settlement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_settlement (settlement_id, tenant_id, amount, status, requested_at, processed_at, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4227 (class 0 OID 19513)
-- Dependencies: 238
-- Data for Name: tenant_tax_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_tax_rule (tax_id, tenant_id, country_code, tax_type, rate, effective_from, effective_to, created_by, created_on, is_active) FROM stdin;
\.


--
-- TOC entry 4270 (class 0 OID 20181)
-- Dependencies: 281
-- Data for Name: tenant_wallet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_wallet (tenant_id, balance, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4253 (class 0 OID 19922)
-- Dependencies: 264
-- Data for Name: trip; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip (trip_id, tenant_id, rider_id, driver_id, vehicle_id, city_id, zone_id, pickup_lat, pickup_lng, drop_lat, drop_lng, status, requested_at, assigned_at, picked_up_at, completed_at, cancelled_at, fare_amount, driver_earning, platform_fee, payment_status, created_by, created_on, updated_by, updated_on) FROM stdin;
4	1	9	\N	\N	1	\N	12.980000	77.890000	12.960000	77.850000	REQUESTED	2026-01-19 16:45:16.478653+05:30	\N	\N	\N	\N	\N	\N	\N	\N	9	2026-01-19 16:45:16.466253+05:30	\N	\N
\.


--
-- TOC entry 4261 (class 0 OID 20065)
-- Dependencies: 272
-- Data for Name: trip_cancellation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_cancellation (cancel_id, trip_id, cancelled_by, reason, cancelled_at) FROM stdin;
\.


--
-- TOC entry 4265 (class 0 OID 20099)
-- Dependencies: 276
-- Data for Name: trip_fare_breakdown; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_fare_breakdown (id, trip_id, base_fare, distance_fare, time_fare, surge_amount, night_charge, tax_amount, discount_amount, final_fare, created_on) FROM stdin;
\.


--
-- TOC entry 4263 (class 0 OID 20085)
-- Dependencies: 274
-- Data for Name: trip_otp; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_otp (otp_id, trip_id, otp_code, expires_at, verified, created_on) FROM stdin;
\.


--
-- TOC entry 4292 (class 0 OID 20480)
-- Dependencies: 303
-- Data for Name: trip_rating; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_rating (rating_id, trip_id, rater_id, ratee_id, rating, comment, created_on) FROM stdin;
\.


--
-- TOC entry 4257 (class 0 OID 20013)
-- Dependencies: 268
-- Data for Name: trip_route_point; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip_route_point (id, trip_id, latitude, longitude, recorded_at) FROM stdin;
\.


--
-- TOC entry 4307 (class 0 OID 20675)
-- Dependencies: 318
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
\.


--
-- TOC entry 4221 (class 0 OID 19410)
-- Dependencies: 232
-- Data for Name: user_kyc; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_kyc (kyc_id, user_id, document_type, document_number, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on, file_url) FROM stdin;
4	14	DRIVING_LICENSE	DL1234567890	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/license.pdf
5	14	AADHAAR	123456789012	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/aadhaar.pdf
6	14	PHOTO	PASSPORT_PHOTO	PENDING	\N	\N	14	2026-01-21 18:53:57.947313+05:30	\N	\N	https://example.com/documents/photo.jpg
7	15	DRIVING_LICENSE	DL1234567890	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-license-url
8	15	AADHAAR	123456789012	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-aadhaar-url
9	15	PHOTO	PASSPORT_PHOTO	PENDING	\N	\N	15	2026-01-21 19:03:06.318396+05:30	\N	\N	dummy-photo-url
\.


--
-- TOC entry 4219 (class 0 OID 19395)
-- Dependencies: 230
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
\.


--
-- TOC entry 4234 (class 0 OID 19647)
-- Dependencies: 245
-- Data for Name: vehicle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle (vehicle_id, tenant_id, fleet_id, category, status, registration_no, created_by, created_on, updated_by, updated_on) FROM stdin;
2	1	\N	AUTO	ACTIVE	TS09AB0001	\N	2026-01-19 16:11:26.401901+05:30	\N	\N
\.


--
-- TOC entry 4236 (class 0 OID 19689)
-- Dependencies: 247
-- Data for Name: vehicle_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle_document (document_id, vehicle_id, document_type, file_url, verification_status, verified_by, verified_on, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4311 (class 0 OID 20772)
-- Dependencies: 322
-- Data for Name: vehicle_spec; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle_spec (vehicle_id, manufacturer, model_name, manufacture_year, fuel_type, seating_capacity, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4216 (class 0 OID 19340)
-- Dependencies: 227
-- Data for Name: zone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zone (zone_id, city_id, name, center_lat, center_lng, boundary, created_by, created_on, updated_by, updated_on) FROM stdin;
\.


--
-- TOC entry 4371 (class 0 OID 0)
-- Dependencies: 228
-- Name: app_user_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_user_id_seq', 15, true);


--
-- TOC entry 4372 (class 0 OID 0)
-- Dependencies: 224
-- Name: city_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.city_city_id_seq', 1, true);


--
-- TOC entry 4373 (class 0 OID 0)
-- Dependencies: 307
-- Name: coupon_coupon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.coupon_coupon_id_seq', 1, false);


--
-- TOC entry 4374 (class 0 OID 0)
-- Dependencies: 310
-- Name: coupon_redemption_redemption_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.coupon_redemption_redemption_id_seq', 1, false);


--
-- TOC entry 4375 (class 0 OID 0)
-- Dependencies: 265
-- Name: dispatch_attempt_attempt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dispatch_attempt_attempt_id_seq', 1, true);


--
-- TOC entry 4376 (class 0 OID 0)
-- Dependencies: 269
-- Name: dispatcher_assignment_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dispatcher_assignment_assignment_id_seq', 1, false);


--
-- TOC entry 4377 (class 0 OID 0)
-- Dependencies: 314
-- Name: driver_incentive_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_progress_id_seq', 1, false);


--
-- TOC entry 4378 (class 0 OID 0)
-- Dependencies: 316
-- Name: driver_incentive_reward_reward_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_reward_reward_id_seq', 1, false);


--
-- TOC entry 4379 (class 0 OID 0)
-- Dependencies: 312
-- Name: driver_incentive_scheme_scheme_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_incentive_scheme_scheme_id_seq', 1, false);


--
-- TOC entry 4380 (class 0 OID 0)
-- Dependencies: 253
-- Name: driver_location_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_location_history_id_seq', 1, false);


--
-- TOC entry 4381 (class 0 OID 0)
-- Dependencies: 250
-- Name: driver_shift_shift_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_shift_shift_id_seq', 1, true);


--
-- TOC entry 4382 (class 0 OID 0)
-- Dependencies: 248
-- Name: driver_vehicle_assignment_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_vehicle_assignment_assignment_id_seq', 1, true);


--
-- TOC entry 4383 (class 0 OID 0)
-- Dependencies: 329
-- Name: driver_work_availability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_work_availability_id_seq', 1, false);


--
-- TOC entry 4384 (class 0 OID 0)
-- Dependencies: 255
-- Name: fare_config_fare_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fare_config_fare_id_seq', 4, true);


--
-- TOC entry 4385 (class 0 OID 0)
-- Dependencies: 323
-- Name: fleet_document_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_document_document_id_seq', 1, true);


--
-- TOC entry 4386 (class 0 OID 0)
-- Dependencies: 242
-- Name: fleet_driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_driver_id_seq', 1, false);


--
-- TOC entry 4387 (class 0 OID 0)
-- Dependencies: 240
-- Name: fleet_fleet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_fleet_id_seq', 2, true);


--
-- TOC entry 4388 (class 0 OID 0)
-- Dependencies: 290
-- Name: fleet_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fleet_ledger_entry_id_seq', 1, false);


--
-- TOC entry 4389 (class 0 OID 0)
-- Dependencies: 300
-- Name: lost_item_report_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lost_item_report_report_id_seq', 1, false);


--
-- TOC entry 4390 (class 0 OID 0)
-- Dependencies: 277
-- Name: payment_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_payment_id_seq', 1, false);


--
-- TOC entry 4391 (class 0 OID 0)
-- Dependencies: 286
-- Name: platform_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.platform_ledger_entry_id_seq', 1, false);


--
-- TOC entry 4392 (class 0 OID 0)
-- Dependencies: 257
-- Name: pricing_time_rule_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pricing_time_rule_rule_id_seq', 1, false);


--
-- TOC entry 4393 (class 0 OID 0)
-- Dependencies: 284
-- Name: refund_refund_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.refund_refund_id_seq', 1, false);


--
-- TOC entry 4394 (class 0 OID 0)
-- Dependencies: 319
-- Name: ride_request_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ride_request_request_id_seq', 1, true);


--
-- TOC entry 4395 (class 0 OID 0)
-- Dependencies: 292
-- Name: sos_event_sos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sos_event_sos_id_seq', 1, false);


--
-- TOC entry 4396 (class 0 OID 0)
-- Dependencies: 298
-- Name: support_ticket_assignment_history_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_assignment_history_history_id_seq', 1, false);


--
-- TOC entry 4397 (class 0 OID 0)
-- Dependencies: 296
-- Name: support_ticket_conversation_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_conversation_message_id_seq', 1, false);


--
-- TOC entry 4398 (class 0 OID 0)
-- Dependencies: 294
-- Name: support_ticket_ticket_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.support_ticket_ticket_id_seq', 1, false);


--
-- TOC entry 4399 (class 0 OID 0)
-- Dependencies: 261
-- Name: surge_event_surge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.surge_event_surge_id_seq', 1, false);


--
-- TOC entry 4400 (class 0 OID 0)
-- Dependencies: 259
-- Name: surge_zone_surge_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.surge_zone_surge_zone_id_seq', 1, false);


--
-- TOC entry 4401 (class 0 OID 0)
-- Dependencies: 233
-- Name: tenant_admin_tenant_admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_admin_tenant_admin_id_seq', 1, true);


--
-- TOC entry 4402 (class 0 OID 0)
-- Dependencies: 326
-- Name: tenant_document_tenant_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_document_tenant_document_id_seq', 1, false);


--
-- TOC entry 4403 (class 0 OID 0)
-- Dependencies: 288
-- Name: tenant_ledger_entry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_ledger_entry_id_seq', 1, false);


--
-- TOC entry 4404 (class 0 OID 0)
-- Dependencies: 282
-- Name: tenant_settlement_settlement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_settlement_settlement_id_seq', 1, false);


--
-- TOC entry 4405 (class 0 OID 0)
-- Dependencies: 237
-- Name: tenant_tax_rule_tax_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_tax_rule_tax_id_seq', 1, false);


--
-- TOC entry 4406 (class 0 OID 0)
-- Dependencies: 221
-- Name: tenant_tenant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_tenant_id_seq', 5, true);


--
-- TOC entry 4407 (class 0 OID 0)
-- Dependencies: 271
-- Name: trip_cancellation_cancel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_cancellation_cancel_id_seq', 1, false);


--
-- TOC entry 4408 (class 0 OID 0)
-- Dependencies: 275
-- Name: trip_fare_breakdown_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_fare_breakdown_id_seq', 1, false);


--
-- TOC entry 4409 (class 0 OID 0)
-- Dependencies: 273
-- Name: trip_otp_otp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_otp_otp_id_seq', 1, false);


--
-- TOC entry 4410 (class 0 OID 0)
-- Dependencies: 302
-- Name: trip_rating_rating_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_rating_rating_id_seq', 1, false);


--
-- TOC entry 4411 (class 0 OID 0)
-- Dependencies: 267
-- Name: trip_route_point_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_route_point_id_seq', 1, false);


--
-- TOC entry 4412 (class 0 OID 0)
-- Dependencies: 263
-- Name: trip_trip_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_trip_id_seq', 4, true);


--
-- TOC entry 4413 (class 0 OID 0)
-- Dependencies: 231
-- Name: user_kyc_kyc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_kyc_kyc_id_seq', 9, true);


--
-- TOC entry 4414 (class 0 OID 0)
-- Dependencies: 246
-- Name: vehicle_document_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicle_document_document_id_seq', 1, false);


--
-- TOC entry 4415 (class 0 OID 0)
-- Dependencies: 244
-- Name: vehicle_vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicle_vehicle_id_seq', 2, true);


--
-- TOC entry 4416 (class 0 OID 0)
-- Dependencies: 226
-- Name: zone_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zone_zone_id_seq', 1, false);


-- Completed on 2026-01-23 20:06:48 IST

--
-- PostgreSQL database dump complete
--

\unrestrict 2avCkakS18Hn1e41GplYpRss4lVYiidsikrfO99WOPFZfJTf3vlv5xO10jESPe0

