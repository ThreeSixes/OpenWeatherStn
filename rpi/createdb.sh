#!/bin/bash
mkdir db
sqlite3 db/weather.db '.read createWeather.sql'
