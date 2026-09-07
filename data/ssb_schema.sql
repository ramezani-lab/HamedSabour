CREATE TABLE customer (
    c_custkey       INTEGER NOT NULL,
    c_name          VARCHAR(25) NOT NULL,
    c_address       VARCHAR(25) NOT NULL,
    c_city          CHAR(10) NOT NULL,
    c_nation        CHAR(15) NOT NULL,
    c_region        CHAR(12) NOT NULL,
    c_phone         CHAR(15) NOT NULL,
    c_mktsegment    CHAR(10) NOT NULL,
    PRIMARY KEY (c_custkey)
);

CREATE TABLE supplier (
    s_suppkey       INTEGER NOT NULL,
    s_name          CHAR(25) NOT NULL,
    s_address       VARCHAR(25) NOT NULL,
    s_city          CHAR(10) NOT NULL,
    s_nation        CHAR(15) NOT NULL,
    s_region        CHAR(12) NOT NULL,
    s_phone         CHAR(15) NOT NULL,
    PRIMARY KEY (s_suppkey)
);

CREATE TABLE part (
    p_partkey       INTEGER NOT NULL,
    p_name          VARCHAR(22) NOT NULL,
    p_mfgr          CHAR(6) NOT NULL,
    p_category      CHAR(7) NOT NULL,
    p_brand1        CHAR(9) NOT NULL,
    p_color         VARCHAR(11) NOT NULL,
    p_type          VARCHAR(25) NOT NULL,
    p_size          INTEGER NOT NULL,
    p_container     CHAR(10) NOT NULL,
    PRIMARY KEY (p_partkey)
);

CREATE TABLE dwdate (
    d_datekey            INTEGER NOT NULL,
    d_date               CHAR(18) NOT NULL,
    d_dayofweek          CHAR(9) NOT NULL,
    d_month              CHAR(9) NOT NULL,
    d_year               INTEGER NOT NULL,
    d_yearmonthnum       INTEGER NOT NULL,
    d_yearmonth          CHAR(7) NOT NULL,
    d_daynuminweek       INTEGER NOT NULL,
    d_daynuminmonth      INTEGER NOT NULL,
    d_daynuminyear       INTEGER NOT NULL,
    d_monthnuminyear     INTEGER NOT NULL,
    d_weeknuminyear      INTEGER NOT NULL,
    d_sellingseason      VARCHAR(12) NOT NULL,
    d_lastdayinweekfl    CHAR(1) NOT NULL,
    d_lastdayinmonthfl   CHAR(1) NOT NULL,
    d_holidayfl          CHAR(1) NOT NULL,
    d_weekdayfl          CHAR(1) NOT NULL,
    PRIMARY KEY (d_datekey)
);

CREATE TABLE lineorder (
    lo_orderkey         BIGINT NOT NULL,
    lo_linenumber       INTEGER NOT NULL,
    lo_custkey          INTEGER NOT NULL,
    lo_partkey          INTEGER NOT NULL,
    lo_suppkey          INTEGER NOT NULL,
    lo_orderdate        INTEGER NOT NULL,
    lo_orderpriority    CHAR(15) NOT NULL,
    lo_shippriority     CHAR(1) NOT NULL,
    lo_quantity         INTEGER NOT NULL,
    lo_extendedprice    INTEGER NOT NULL,
    lo_ordtotalprice    INTEGER NOT NULL,
    lo_discount         INTEGER NOT NULL,
    lo_revenue          INTEGER NOT NULL,
    lo_supplycost       INTEGER NOT NULL,
    lo_tax              INTEGER NOT NULL,
    lo_commitdate       INTEGER NOT NULL,
    lo_shipmode         CHAR(10) NOT NULL,
    PRIMARY KEY (lo_orderkey, lo_linenumber)
);
