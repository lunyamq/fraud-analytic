#!/bin/bash

curl -L -o creditcardfraud.zip "https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud"
unzip -o creditcardfraud.zip
rm creditcardfraud.zip
