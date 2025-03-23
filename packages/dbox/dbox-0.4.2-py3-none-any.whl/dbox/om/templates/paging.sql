select *
from {{ input_block.sql_target() }}
{% if order_by %}
order by {{ order_by | join(', ') }}
{% endif %}
{% if limit %}
limit {{ limit }}
{% endif %}
{% if offset %}
offset {{ offset }}
{% endif %}
