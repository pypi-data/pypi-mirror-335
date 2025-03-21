# virgo-gui

Prototype for the virgo control room gui

## Installation via package

Currently available on [pypi](https://pypi.org/project/virgui/)

Recommend to use in a fresh conda/python environment, you might mess up existing environments.

If using conda

```bash
conda create -n virgui-test python=3.12
conda activate virgui-test
```

Then

```bash
pip install virgui
virgui
```

Will start up the program. Keep an eye out for the terminal, this is where any errors will appear.

For updating:

```bash
pip install -U virgui
```

## Development install

Recommended to use in a fresh conda/python environment, you might mess up existing environments.

If using conda

```bash
conda create -n virgui-test python=3.12
conda activate virgui-test
```

```bash
# ssh
git clone git@gitlab.com:ifosim/finesse/virgo-gui.git
# or https
# git clone https://gitlab.com/ifosim/finesse/virgo-gui.git
cd virgo-gui
pip install -e .
```

For updating:

```bash
git pull
```

## Usage

Currently there is only one layout available, a simple cavity.

Click on the different components to see the parameter values (no editing so far)

In the 'calculate' tab, you should be able to run an Xaxis and see the plot.

Currently I hardcoded in three powerdetectors.

![layout screen](layout.png)

![calculate screen](calculate.png)
