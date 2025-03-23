insert into {{ model.get_fqtn() }} ({{columns | join(', ')}})
values ({% for c in columns %} %({{c}})s{% if not loop.last %},{% endif %}{% endfor %})
returning {{pk_col}};
