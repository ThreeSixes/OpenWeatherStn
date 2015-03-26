#!/bin/bash
mkdir db
sqlite3 db/weather.db '.read createWeather.sql'
chmod 755 db
chmod 644 db/weather.db
