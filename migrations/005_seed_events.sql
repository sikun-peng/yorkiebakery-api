-- Snapshot seed for current events and RSVPs.

COPY public.event (id, title, description, event_datetime, location, event_type, image_url, is_public, is_active, created_at) FROM stdin;
b88f2faa-ccd5-495f-bec9-12f7c8ac55e9	Old Event	What is this for?	1900-01-01 01:01:00	Somewhere	\N	\N	t	t	2025-11-23 06:00:47.753055
5ad2596b-b420-4ead-be21-b23d62837eab	Oscar's Piano Recital	When is it ever gonna happen?	2099-12-31 23:59:00	Yorkie Bakery, Round Rock, TX	\N	https://d2pdj881wm30p5.cloudfront.net/events/09df106b-9e9e-4695-a3e1-44a676189a40_concert.jpg	t	t	2025-11-23 05:55:45.41254
63a08de7-2d73-48d6-9e21-b7570112030a	Yorkie Bakery Grand Opening	Yah 	6789-12-31 23:59:00	Buc-ee's, TX	\N	https://d2pdj881wm30p5.cloudfront.net/events/d4491f5e-af55-49e8-8ba0-0e5ea368f5b9_logo5.jpg	t	t	2025-11-23 05:59:11.677796
\.

COPY public.event_rsvp (id, event_id, name, email, message, created_at) FROM stdin;
711a14f7-5509-412e-aa0d-f890902e5d10	63a08de7-2d73-48d6-9e21-b7570112030a	Oscar	sikun.peng1990@yahoo.com	Reserve	2025-11-23 06:41:53.371923
08a36e3a-d75d-494e-9141-75d70d5bb8d3	5ad2596b-b420-4ead-be21-b23d62837eab	SIKUN PENG	sikun.peng1990@gmail.com	hi	2025-11-27 06:24:21.039363
\.
