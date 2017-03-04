drop table if exists articles;
create table entries (
  id integer primary key autoincrement,
  slug text not null,
  summary text not null,
  author text,
  published date not null,
  location text,
);

drop table if exists categories;
create table categories(
  id integer primary key autoincrement,
  slug text not null,
  published date not null,
  category text not null,
  FOREIGN KEY (slug) REFERENCES entries(slug)
);