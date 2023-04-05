
# Benchmarking with Pytest

The purpose of Benchmarking with pytest is to provide a scaling pipeline which can assist in rapid detection of performance degradation in HeAT via a CI/CD system. The basis of this
project is based on the three related pilars to performance measurement. The first is that 
a given benchmark can be represented in a function call, This function call can then be tested
against various forms of datasets as parametes using a mature python testing library called pytest.
![Overview project](https://raw.githubusercontent.com/tewodros18/rep/master/image1.png)

## CI overview

The  `benchmarking-test` workflow calls the script `pytest-benchmarks/run_benchmarks.sh`. so manually triggering
the script is also possible. 





## run_benchmarks.sh

```python
#calls benchmark for all the pytest encapsulated workloads in folder
pytest --benchmark-json

#Support for passing working directory as flags is being added for manual activation 

run_benchmarks -d 'dirto/localdata-repository'
```

## aggregate.py

```python
#responsible for parsing generated results and create/update aggregate.
#json of the specified benchmark 

python aggregate.py

```

## buildlist.py

```python
#responsible for collecting results location and their names for ginkgo performance explorer

./build-list . > list.json


```
## Exploring results in GPE

After the successful completion of the CI, generated results can be found in the public repository [Heat-data](https://github.com/tewodros18/heat-data)

To visualize the data go to [Ginkgo Performance Explorer](https://ginkgo-project.github.io/gpe/)

```bash
  https://ginkgo-project.github.io/gpe/
```

Copy URL to data repository and put in section one of explorer and select benchmark file

```bash
  https://raw.githubusercontent.com/tewodros18/heat-data/main/data
```
![step](https://raw.githubusercontent.com/tewodros18/rep/master/step1.PNG)

Copy URL to plot repository and put in section two of explorer

```bash
  https://raw.githubusercontent.com/tewodros18/heat-data/main/plots
```
![step](https://raw.githubusercontent.com/tewodros18/rep/master/step2.PNG)
