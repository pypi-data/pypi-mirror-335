select count(1) as count
from {{ input_block.sql_target() }}
