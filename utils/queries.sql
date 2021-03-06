-- company
select to_char(reversion_revision.date_created, 'YYYY-MM'), username, count(*)
from users_user
join reversion_revision on users_user.id=user_id
join reversion_version on reversion_revision.id = reversion_version.revision_id
where reversion_version.content_type_id=16
group by to_char(reversion_revision.date_created, 'YYYY-MM'), username
order by 1 desc, 3 desc;

-- product
select to_char(reversion_revision.date_created, 'YYYY-MM'), username, count(*)
from users_user
join reversion_revision on users_user.id=user_id
join reversion_version on reversion_revision.id = reversion_version.revision_id
where reversion_version.content_type_id=15
group by to_char(reversion_revision.date_created, 'YYYY-MM'), username
order by 1 desc, 3 desc;

-- report
select to_char(report_report.resolved_at, 'YYYY-MM'), username, count(*)
from users_user
join report_report on users_user.id=report_report.resolved_by_id
group by to_char(report_report.resolved_at, 'YYYY-MM'), username
order by 1 desc, 3 desc;

-- requery ilim
select to_char(ilim_queried_at, 'YYYY-MM-DD'), count(*)
from product_product
group by to_char(ilim_queried_at, 'YYYY-MM-DD')
order by 1 desc;

select name from company_company where "plCapital"=0 and "plNotGlobEnt"=100;

-- look for escaped characters in database
select name, official_name, common_name, address
from company_company
where name like '%&%;%' or
official_name like '%&%;%' or
common_name like '%&%;%' OR
address like '%&%;%'
;

update product_product set query_count = (select count(*) from pola_query where pola_query.product_id=product_product.id);

SELECT "company_company"."id", "company_company"."name", SUM("product_product"."query_count") AS "query_count"
FROM "company_company" JOIN "product_product" ON ( "company_company"."id" = "product_product"."company_id" )
WHERE "company_company"."verified" = false
GROUP BY "company_company"."id", "company_company"."name"
ORDER BY "query_count" DESC LIMIT 10;

update product_product
set query_count = count(query_count.id)
from pola_query
where pola_query.product_id = product_product.id;


select code,query_count,name from product_product where query_count>0 and company_id is null and code like '590%'
order by query_count desc;

select count(*) from company_company;
select count(*) from pola_query;
select count(*) from pola_stats;
select count(*) from product_product;
select count(*) from report_attachment;
select count(*) from report_report;
select count(*) from reversion_revision;
select count(*) from reversion_version;


select to_char(date_created, 'YYYY-MM'), count(*)
from reversion_revision
group by to_char(date_created, 'YYYY-MM')
order by 1 desc;


select to_char(date_created, 'YYYY-MM'), user_id, content_type_id, count(*)
from reversion_version
left outer join reversion_revision on reversion_revision.id = reversion_version.revision_id
group by to_char(reversion_revision.date_created, 'YYYY-MM'), user_id, content_type_id
order by 1 desc, 2 desc, 3 desc;

select user_id, content_type_id, comment, count(*)
from reversion_version
full join reversion_revision on reversion_revision.id = reversion_version.revision_id
group by user_id, content_type_id, comment
order by 4 desc limit 20;


select comment
from reversion_version
join reversion_revision on reversion_revision.id = reversion_version.revision_id
where content_type_id=16 and object_id_int=711
order by date_created desc limit 10;

select count(*) from reversion_revision
where id not in (select revision_id from reversion_version);


select name, query_count from company_company where "plCapital">50 and ("plWorkers"=100 or "plRnD"=100)
order by query_count desc limit 20;

SELECT relname,n_live_tup
  FROM pg_stat_user_tables where n_Live_tup>250
  ORDER BY n_live_tup DESC;

select sum(n_live_tup) from pg_stat_user_tables;

select product_id,count(*) from report_report
 join report_attachment on report_attachment.report_id = report_report.id
group by product_id order by count(*) desc;
