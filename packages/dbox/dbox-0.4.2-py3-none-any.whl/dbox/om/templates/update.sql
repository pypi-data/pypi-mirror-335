update {{ model.get_fqtn() }}
set
{% for col in columns %}
   {{ col }} = %({{ col }})s{% if not loop.last %},{% endif %}
{% endfor %}

where {{pk_col}} = %(pk_col)s
