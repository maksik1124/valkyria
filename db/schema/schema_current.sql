--
-- PostgreSQL database dump
--

\restrict Q77FFTCysdYgQGzV1kBF8RswNIS4K85I9iTwyfWphHW7XWrZjBMBSUUk7LgmSgh

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: valkyria_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO valkyria_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: competitions; Type: TABLE; Schema: public; Owner: valkyria_user
--

CREATE TABLE public.competitions (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    date date NOT NULL,
    "time" time without time zone,
    place character varying(128)
);


ALTER TABLE public.competitions OWNER TO valkyria_user;

--
-- Name: competitions_id_seq; Type: SEQUENCE; Schema: public; Owner: valkyria_user
--

CREATE SEQUENCE public.competitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competitions_id_seq OWNER TO valkyria_user;

--
-- Name: competitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: valkyria_user
--

ALTER SEQUENCE public.competitions_id_seq OWNED BY public.competitions.id;


--
-- Name: horses; Type: TABLE; Schema: public; Owner: valkyria_user
--

CREATE TABLE public.horses (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    sex character varying(10),
    age integer,
    owner_id integer NOT NULL
);


ALTER TABLE public.horses OWNER TO valkyria_user;

--
-- Name: horses_id_seq; Type: SEQUENCE; Schema: public; Owner: valkyria_user
--

CREATE SEQUENCE public.horses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.horses_id_seq OWNER TO valkyria_user;

--
-- Name: horses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: valkyria_user
--

ALTER SEQUENCE public.horses_id_seq OWNED BY public.horses.id;


--
-- Name: results; Type: TABLE; Schema: public; Owner: valkyria_user
--

CREATE TABLE public.results (
    id integer NOT NULL,
    competition_id integer NOT NULL,
    horse_id integer NOT NULL,
    jockey_id integer NOT NULL,
    place integer,
    race_time character varying(32)
);


ALTER TABLE public.results OWNER TO valkyria_user;

--
-- Name: results_id_seq; Type: SEQUENCE; Schema: public; Owner: valkyria_user
--

CREATE SEQUENCE public.results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.results_id_seq OWNER TO valkyria_user;

--
-- Name: results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: valkyria_user
--

ALTER SEQUENCE public.results_id_seq OWNED BY public.results.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: valkyria_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    full_name character varying(128) NOT NULL,
    password_hash character varying(512) NOT NULL,
    role character varying(20) NOT NULL,
    age integer,
    address character varying(255),
    rating double precision,
    contact_info character varying(255),
    email character varying(120)
);


ALTER TABLE public.users OWNER TO valkyria_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: valkyria_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO valkyria_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: valkyria_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: competitions id; Type: DEFAULT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.competitions ALTER COLUMN id SET DEFAULT nextval('public.competitions_id_seq'::regclass);


--
-- Name: horses id; Type: DEFAULT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.horses ALTER COLUMN id SET DEFAULT nextval('public.horses_id_seq'::regclass);


--
-- Name: results id; Type: DEFAULT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.results ALTER COLUMN id SET DEFAULT nextval('public.results_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: competitions competitions_pkey; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT competitions_pkey PRIMARY KEY (id);


--
-- Name: horses horses_pkey; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.horses
    ADD CONSTRAINT horses_pkey PRIMARY KEY (id);


--
-- Name: results results_pkey; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: horses horses_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.horses
    ADD CONSTRAINT horses_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: results results_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.competitions(id);


--
-- Name: results results_horse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_horse_id_fkey FOREIGN KEY (horse_id) REFERENCES public.horses(id);


--
-- Name: results results_jockey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: valkyria_user
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_jockey_id_fkey FOREIGN KEY (jockey_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict Q77FFTCysdYgQGzV1kBF8RswNIS4K85I9iTwyfWphHW7XWrZjBMBSUUk7LgmSgh

