CREATE TABLE weather(
    dts TIMESTAMP NOT NULL PRIMARY KEY,
    temp NUMERIC,
    humid NUMERIC,
    baro NUMERIC,
    rain NUMERIC,
    windDir NUMERIC,
    windAvg NUMERIC,
    windMax NUMERIC,
    lightLvl NUMERIC,
    sysTemp NUMERIC
);