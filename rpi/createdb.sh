#!/bin/bash
mkdir db
sqlite3 db/weather.db '.read createWeather.sql'
chmod 777 db
chmod 666 db/weather.db
