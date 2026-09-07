SELECT sum(lo_extendedprice * lo_discount) FROM lineorder, dwdate WHERE lo_orderdate = d_datekey and d_year = 1993 and lo_discount >= 1 and lo_discount <= 3 and lo_quantity < 25;
SELECT sum(lo_extendedprice * lo_discount) FROM lineorder, dwdate WHERE lo_orderdate = d_datekey and d_yearmonthnum = 199401 and lo_discount >= 4 and lo_discount <= 6 and lo_quantity >= 26 and lo_quantity <= 35;
SELECT sum(lo_extendedprice * lo_discount) FROM lineorder, dwdate WHERE lo_orderdate = d_datekey and d_year = 1994 and lo_discount >= 5 and lo_discount <= 7 and lo_quantity >= 36 and lo_quantity <= 40;
