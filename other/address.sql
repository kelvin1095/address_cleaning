-- address_detail.legal_parcel_id,
-- flat_type_aut.code,
-- level_type_aut.code,
-- street_type_aut.name,
-- street_suffix_aut.code

SELECT address_detail.address_detail_pid,
       CONCAT_WS(' ', flat_type_aut.name, CASE
                                              WHEN address_detail.flat_number_prefix IS NULL
                                                   AND address_detail.flat_number IS NULL
                                                   AND address_detail.flat_number_suffix IS NULL THEN NULL
                                              ELSE CONCAT_WS('', address_detail.flat_number_prefix, address_detail.flat_number, address_detail.flat_number_suffix)
                                          END, level_type_aut.name, CASE
                                                                        WHEN address_detail.level_number_prefix IS NULL
                                                                             AND address_detail.level_number IS NULL
                                                                             AND address_detail.level_number_suffix IS NULL THEN NULL
                                                                        ELSE CONCAT_WS('', address_detail.level_number_prefix, address_detail.level_number, address_detail.level_number_suffix)
                                                                    END) AS address_line_1,
       CONCAT_WS(' ', CONCAT_WS('-', CASE
                                         WHEN address_detail.number_first_prefix IS NULL
                                              AND address_detail.number_first IS NULL
                                              AND address_detail.number_first_suffix IS NULL THEN NULL
                                         ELSE CONCAT_WS('', address_detail.number_first_prefix, address_detail.number_first, address_detail.number_first_suffix)
                                     END, CASE
                                              WHEN address_detail.number_last_prefix IS NULL
                                                   AND address_detail.number_last IS NULL
                                                   AND address_detail.number_last_suffix IS NULL THEN NULL
                                              ELSE CONCAT_WS('', address_detail.number_last_prefix, address_detail.number_last, address_detail.number_last_suffix)
                                          END), street_locality.street_name, street_type_aut.code, street_suffix_aut.name) AS address_line_2,
       CONCAT_WS(' ', locality.locality_name, 'NSW', address_detail.postcode) AS address_line_3,
       'AUSTRALIA' AS country
FROM address_detail
LEFT JOIN street_locality ON street_locality.street_locality_pid = address_detail.street_locality_pid
LEFT JOIN locality ON locality.locality_pid = address_detail.locality_pid
LEFT JOIN level_type_aut ON level_type_aut.code = address_detail.level_type_code
LEFT JOIN flat_type_aut ON flat_type_aut.code = address_detail.flat_type_code
LEFT JOIN street_suffix_aut ON street_suffix_aut.code = street_locality.street_suffix_code
LEFT JOIN street_type_aut ON street_type_aut.code = street_locality.street_type_code
ORDER BY random()
LIMIT 1000;