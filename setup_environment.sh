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
sed -i "43i export IPYTHONPATH" .venv/bin/activate
sed -i "43i IPYTHONPATH=$PWD/.venv/ipython/" .venv/bin/activate
sed -i "30i \ \ \ \ unset IPYTHONPATH" .venv/bin/activate

source .venv/bin/activate
pip install -e .[dev]
# Ensure we use a local version of dodal
if [ ! -d "../dodal" ]; then
  git clone git@github.com:DiamondLightSource/dodal.git ../dodal
fi
pip uninstall -y dodal
pip install -e ../dodal[dev]