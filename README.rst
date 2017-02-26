Infrastructure Planning
=======================
Here is an updated infrastructure planning system based on `our earlier work <https://github.com/SEL-Columbia/networkplanner>`_.


Install
-------
The system depends on several numerical and spatial packages. You can use the following scripts to install these packages. ::

    git clone https://github.com/crosscompute/crosscompute-environments-ansible
    cd crosscompute-environments-ansible
    bash setup.sh

Additional required modules must be installed manually. Note that you may need to edit ``requirements.txt`` to exclude certain packages.::

    source ~/.virtualenvs/crosscompute/bin/activate

    git clone https://github.com/sel-columbia/networker
    pushd networker
    vim requirements.txt
        numpy
        scipy
        networkx
        decorator
        cython
        nose
        funcsigs
        pandas
        enum34
        pytz
        rtree
        jsonschema
        pyproj
        six
        # gdal
    pip install -e .
    popd

    git clone https://github.com/sel-columbia/sequencer
    pushd sequencer
    vim requirements.txt
        scipy
        # dateutil
        decorator
        fiona
        # freetype
        # gdal
        matplotlib
        networkx
        numexpr
        pandas
        pyparsing
        pytz
        numpy
    pip install -e .
    popd

    git clone https://github.com/sel-columbia/infrastructure-planning
    pushd infrastructure-planning
    pip install -e .
    popd


Use
---
Run example scenario. ::

    bash scripts/estimate_electricity_cost_by_technology_from_population.sh

Serve notebook. ::

    source ~/.virtualenvs/crosscompute/bin/activate
    crosscompute serve compute_levelized_cost_per_kwh_consumed.ipynb

Start server. ::

    bash scripts/serve.sh
