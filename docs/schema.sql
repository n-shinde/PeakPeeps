Coupons Table:

create table
  public.coupons (
    id integer generated by default as identity,
    name text not null,
    valid boolean null,
    constraint Coupons_pkey primary key (id)
  ) tablespace pg_default;

Friendship Table:

create table
  public.friendship (
    id integer generated by default as identity,
    friend_id integer not null,
    date_added timestamp without time zone null,
    context text null,
    constraint Friendship_pkey primary key (id),
    constraint friendship_id_fkey foreign key (id) references "user" (id)
  ) tablespace pg_default;

Review Table:

create table
  public.review (
    id integer generated by default as identity,
    author_name text not null,
    description text null,
    rating integer null,
    route_id integer null,
    constraint Review_pkey primary key (id),
    constraint review_route_id_fkey foreign key (route_id) references route (id)
  ) tablespace pg_default;


Route Table:

create table
  public.route (
    id integer generated by default as identity,
    name text not null,
    date_added timestamp with time zone null default now(),
    location text null,
    length_in_miles real null,
    difficulty integer null,
    activities text null,
    user_id integer null,
    coords real[] null,
    constraint Route_pkey primary key (id)
  ) tablespace pg_default;

User Table:

create table
  public.user (
    id integer generated by default as identity,
    username text not null,
    date_joined time without time zone null default now(),
    num_followers integer null default 0,
    banned boolean null default false,
    peep_coins integer null default 0,
    constraint User_pkey primary key (id),
    constraint User_username_key unique (username)
  ) tablespace pg_default;
  
  
INSERT INTO user (username)
VALUES ("Biker_Dave")
