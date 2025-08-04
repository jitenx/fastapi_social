CREATE TABLE
  public.posts (
    id serial NOT NULL primary key,
    title character varying(255) NOT NULL,
    content character varying(255) NOT NULL,
    published boolean DEFAULT True,
    created_at timestamp without time zone NOT NULL DEFAULT now()
  );