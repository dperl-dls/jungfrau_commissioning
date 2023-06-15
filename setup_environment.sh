module unload controls_dev 
module load python/3.10
if [ -d "./.venv" ]
then
rm -rf .venv
fi
mkdir .venv
module load python/3.10
python -m venv .venv
# Use local ipython configs for this project
sed -i "43i export IPYTHONDIR" .venv/bin/activate
sed -i "43i IPYTHONDIR=$PWD/.venv/ipython/" .venv/bin/activate
sed -i "30i \ \ \ \ unset IPYTHONDIR" .venv/bin/activate

source .venv/bin/activate

pip install -e .[dev]
# Ensure we use a local version of dodal, nexgen, artemis
if [ ! -d "../dodal" ]; then
  git clone git@github.com:DiamondLightSource/dodal.git ../dodal
fi
pip uninstall -y dodal
pip install -e ../dodal[dev]

if [ ! -d "../python-artemis" ]; then
  git clone git@github.com:DiamondLightSource/python-artemis.git ../python-artemis
fi
pip uninstall -y python-artemis
pip install -e ../python-artemis[dev]

if [ ! -d "../nexgen" ]; then
  git clone git@github.com:dials/nexgen.git ../nexgen
fi
pip uninstall -y nexgen
pip install -e ../nexgen[dev]

mkdir .venv/ipython
ipython profile create jungfrau
