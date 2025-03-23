UPDATE {{ model.get_fqtn() }}
SET deleted_at = NOW();
WHERE
  {{ model.pk_col() }} = %(pk)s
