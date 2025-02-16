--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

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
-- Name: authors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.authors (
    author_id integer NOT NULL,
    name character varying(50) NOT NULL,
    surname character varying(50) NOT NULL
);


ALTER TABLE public.authors OWNER TO postgres;

--
-- Name: authors_author_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.authors_author_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.authors_author_id_seq OWNER TO postgres;

--
-- Name: authors_author_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.authors_author_id_seq OWNED BY public.authors.author_id;


--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    isbn13 character varying(20) NOT NULL,
    title character varying(255) NOT NULL,
    author_id integer NOT NULL,
    genres text[] NOT NULL,
    year_of_original_publication integer NOT NULL,
    year_of_publication integer NOT NULL,
    isbn10 character varying(20),
    publisher character varying(255) NOT NULL,
    num_of_pages integer NOT NULL,
    language character varying(50) NOT NULL,
    series character varying(255)
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: authors author_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors ALTER COLUMN author_id SET DEFAULT nextval('public.authors_author_id_seq'::regclass);


--
-- Data for Name: authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.authors (author_id, name, surname) FROM stdin;
1	George	Orwell
2	J.K.	Rowling
3	J.R.R.	Tolkien
4	Harper	Lee
5	Gabriel	Garcia Marquez
6	F. Scott	Fitzgerald
7	Alexandre	Dumas Pere
8	Mark	Twain
9	Fyodor	Dostoevsky
10	Mary	Shelley
\.


--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.books (isbn13, title, author_id, genres, year_of_original_publication, year_of_publication, isbn10, publisher, num_of_pages, language, series) FROM stdin;
9780451524935	1984	1	{Dystopian,"Political Fiction","Science Fiction","Social Commentary"}	1949	1961	0451524934	Signet Classic	314	English	\N
9780747532699	Harry Potter and the Philosopher's Stone	2	{Fantasy,"Young Adult",Adventure}	1997	1997	0747532699	Bloomsbury	223	English	Harry Potter
9780547928210	The Lord of the Rings: The Fellowship of the Ring	3	{Fantasy,Epic,Adventure}	1954	2012	0547928211	William Morrow Paperbacks	423	English	The Lord of the Rings
9780060935467	To Kill a Mockingbird	4	{"Southern Gothic",Coming-of-Age,"Historical Fiction"}	1960	2002	0060935464	Harper Perennial Modern Classics	281	English	\N
9780060883287	One Hundred Years of Solitude	5	{"Magical Realism","Literary Fiction","Historical Fiction"}	1967	2006	0060883286	Harper Perennial Modern Classics	417	English	\N
9780743273565	The Great Gatsby	6	{Modernist,Tragedy,"Social Criticism"}	1925	2004	0743273567	Scribner	180	English	\N
9780140449266	The Count of Monte Cristo	7	{Adventure,"Historical Fiction",Romance,Revenge}	1844	2003	0140449264	Penguin Classics	1276	English	\N
9780143107323	The Adventures of Huckleberry Finn	8	{Adventure,Coming-of-Age,Satire,Realism}	1884	2014	0143107321	Penguin Classics	366	English	\N
9780143058144	Crime and Punishment	9	{"Psychological Fiction","Philosophical Novel",Crime}	1866	2005	0143058142	Penguin Audio	430	English	\N
9780486282114	Frankenstein	10	{"Gothic Fiction","Science Fiction",Horror}	1818	1994	0486282112	Dover Publications	280	English	\N
\.


--
-- Name: authors_author_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.authors_author_id_seq', 10, true);


--
-- Name: authors authors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pkey PRIMARY KEY (author_id);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (isbn13);


--
-- Name: books fk_author; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT fk_author FOREIGN KEY (author_id) REFERENCES public.authors(author_id);


--
-- PostgreSQL database dump complete
--

