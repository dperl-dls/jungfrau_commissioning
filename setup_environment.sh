module load python/3.10
python -m venv .venv
sed -i "43i export IPYTHONPATH" .venv/bin/activate
sed -i "43i IPYTHONPATH=$PWD/.venv/ipython/" .venv/bin/activate
sed -i "30i \ \ \ \ unset IPYTHONPATH" .venv/bin/activate
source .venv/bin/activate
pip install -e .[dev]