# Web-Based 3D Pictorial Maps with Data-Driven Procedural Placement

![showcase image](showcase.png)

This repository contains a tool for creating and displaying 3D Pictorial Maps
using Procedural techniques. It is divided in a Python script (backend) which
run Procedural Placement of assets using data as input. The data are ecotope
definitions in JSON format, and image files for height maps and density maps
for each ecotope. Then the frontend is a Javascript Web App that uses three.js.
The frontend also works using data as input which are: 3D models in glTF format,
placement information and surface information given in JSON format.

For a detailed explanation on the algorithm used, read the
[paper](docs/paper.pdf)

You can see the Web App [here](https://henryxz.github.io/pictorial-map)