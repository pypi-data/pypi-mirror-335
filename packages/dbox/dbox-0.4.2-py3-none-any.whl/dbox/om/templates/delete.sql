DELETE FROM {{ model.get_fqtn() }}
WHERE
  {{ model.pk_col() }} = %(pk)s
