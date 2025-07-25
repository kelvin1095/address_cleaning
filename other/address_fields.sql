\COPY
    (SELECT address_detail.address_detail_pid,
            MD5(concat_ws('|', street_locality.street_name, street_type_aut.code, street_suffix_aut.name, locality.locality_name, postcode)) AS street_key,
            flat_type_aut.code AS flat_type_code,
            flat_type_aut.name AS flat_type_name,
            address_detail.flat_number_prefix,
            address_detail.flat_number,
            address_detail.flat_number_suffix,
            level_type_aut.code AS level_type_code,
            level_type_aut.name AS level_type_name,
            address_detail.level_number_prefix,
            address_detail.level_number,
            address_detail.level_number_suffix,
            address_detail.number_first_prefix,
            address_detail.number_first,
            address_detail.number_first_suffix,
            address_detail.number_last_prefix,
            address_detail.number_last,
            address_detail.number_last_suffix,
            street_locality.street_name,
            street_type_aut.name AS street_type_code,
            street_type_aut.code AS street_type_name,
            street_suffix_aut.code as street_suffix_code,
            street_suffix_aut.name as street_suffix_name,
            locality.locality_name,
            'NSW' AS state,
            address_detail.postcode,
            'AUSTRALIA' AS country
     FROM address_detail
     LEFT JOIN street_locality ON street_locality.street_locality_pid = address_detail.street_locality_pid
     LEFT JOIN locality ON locality.locality_pid = address_detail.locality_pid
     LEFT JOIN level_type_aut ON level_type_aut.code = address_detail.level_type_code
     LEFT JOIN flat_type_aut ON flat_type_aut.code = address_detail.flat_type_code
     LEFT JOIN street_suffix_aut ON street_suffix_aut.code = street_locality.street_suffix_code
     LEFT JOIN street_type_aut ON street_type_aut.code = street_locality.street_type_code) TO 'address_fields.csv'
DELIMITER ',' CSV HEADER;