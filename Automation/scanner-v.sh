#!/bin/bash
echo "following the white rabbit.."
sleep 2
python3 client.py -w win -v true && python3 client.py -w osx -v true && python3 client.py -w linux -v true && python3 client.py -w linuxtw -v true
