select *
from {{ input_block.sql_target() }}
{% if conditions %}
where
  {{+ conditions | join('\n  and ') }}
{% endif %}