#!/bin/bash

protoc --python_out=androidtv_remote/proto/ --pyi_out=androidtv_remote/proto/ pairing.proto
protoc --python_out=androidtv_remote/proto/ --pyi_out=androidtv_remote/proto/ remote.proto