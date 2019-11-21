# When dreams come true: HDL workflow in Python

In this repository is the material presented at [SiFive Tech symposium BsAs 2019](https://sifivetechsymposium.com/agenda-buenos-aires/).

# How to use it?

```console
pip3 install -r requirements.txt
python3 -m adder.adder generate # Generate Verilog
python3 -m pytest adder # Run test 
python3 -m pytest -s adder # Run test with live stdout
```
