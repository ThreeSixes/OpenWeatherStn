#!/bin/bash
mkdir db
sqlite3 db/weather.db -init createWeather.sql
chmod 666 db/weather.db
