<img align="right" width="140" height="140" src="https://www.naterscreations.com/imputegap/logo_imputegab.png" >
<br /> <br />

# Welcome to ImputeGAP

ImputeGAP is a comprehensive Python library for imputation of missing values in time series data. It implements user-friendly APIs to easily visualize, analyze, and repair your own time series datasets. The library supports a diverse range of imputation methods and modular missing data simulation catering to datasets with varying characteristics. ImputeGAP includes extensive customization options, such as automated hyperparameter tuning, benchmarking, explainability, downstream evaluation, and compatibility with popular time series frameworks.

In detail, the package provides:
Access to commonly used datasets in time series research (Datasets).

  - Access to commonly used datasets in time series research ([Datasets](https://imputegap.readthedocs.io/en/latest/datasets.html)).
  - Automated preprocessing with built-in methods for normalizing time series ([PreProcessing](https://imputegap.readthedocs.io/en/latest/preprocessing.html)).
  - Configurable contamination module that simulates real-world missingness patterns ([Patterns](https://imputegap.readthedocs.io/en/latest/patterns.html)).
  - Parameterizable state-of-the-art time series imputation algorithms ([Algorithms](https://imputegap.readthedocs.io/en/latest/algorithms.html)).
  - Benchmarking to foster reproducibility in time series imputation ([Benchmark](https://imputegap.readthedocs.io/en/latest/benchmark.html)).
  - Modular tools to analyze the behavior of imputation algorithms and assess their impact on key downstream tasks in time series analysis ([Downstream](https://imputegap.readthedocs.io/en/latest/downstream.html)).
  - Fine-grained analysis of the impact of time series features on imputation results ([Explainer](https://imputegap.readthedocs.io/en/latest/explainer.html)).
  - Plug-and-play integration of new datasets and algorithms in various languages such as Python, C++, Matlab, Java, and R.

<br>

![Python](https://img.shields.io/badge/Python-v3.12-blue) 
![Release](https://img.shields.io/badge/Release-v1.0.6-brightgreen) 
![License](https://img.shields.io/badge/License-GPLv3-blue?style=flat&logo=gnu)
![Coverage](https://img.shields.io/badge/Coverage-93%25-brightgreen)
![PyPI](https://img.shields.io/pypi/v/imputegap?label=PyPI&color=blue)
![Language](https://img.shields.io/badge/Language-English-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-informational)
[![Docs](https://img.shields.io/badge/Docs-available-brightgreen?style=flat&logo=readthedocs)](https://exascaleinfolab.github.io/ImputeGAP/generation/build/html/index.html)

<br>

- **Documentation**: [https://imputegap.readthedocs.io/en/latest/](https://imputegap.readthedocs.io/en/latest/)
- **PyPI**: [https://pypi.org/project/imputegap/](https://pypi.org/project/imputegap/)
- **Datasets**: [Repository](https://github.com/eXascaleInfolab/ImputeGAP/tree/main/imputegap/dataset)
- ---



# List of available imputation algorithms
| **Family**         | **Algorithm**             | **Venue -- Year**            |
|--------------------|---------------------------|------------------------------|
| Deep Learning      | BITGraph [[32]](#ref32)   | ICLR -- 2024                 |
| Deep Learning      | BayOTIDE [[30]](#ref30)   | PMLR -- 2024                 |
| Deep Learning      | MPIN [[25]](#ref25)       | PVLDB -- 2024                |
| Deep Learning      | MissNet [[27]](#ref27)    | KDD -- 2024                  |
| Deep Learning      | PriSTI [[26]](#ref26)     | ICDE -- 2023                 |
| Deep Learning      | GRIN [[29]](#ref29)       | ICLR -- 2022                 |
| Deep Learning      | HKMF-T [[31]](#ref31)     | TKDE -- 2021                 |
| Deep Learning      | DeepMVI [[24]](#ref24)    | PVLDB -- 2021                |
| Deep Learning      | MRNN [[22]](#ref22)       | IEEE Trans on BE -- 2019     |
| Deep Learning      | BRITS [[23]](#ref23)      | NeurIPS -- 2018              |
| Deep Learning      | GAIN [[28]](#ref28)       | ICML -- 2018                 |
| Matrix Completion  | CDRec [[1]](#ref1)        | KAIS -- 2020                 |
| Matrix Completion  | TRMF [[8]](#ref8)         | NeurIPS -- 2016              |
| Matrix Completion  | GROUSE [[3]](#ref3)       | PMLR -- 2016                 |
| Matrix Completion  | ROSL [[4]](#ref4)         | CVPR -- 2014                 |
| Matrix Completion  | SoftImpute [[6]](#ref6)   | JMLR -- 2010                 |
| Matrix Completion  | SVT [[7]](#ref7)          | SIAM J. OPTIM -- 2010        |
| Matrix Completion  | SPIRIT [[5]](#ref5)       | VLDB -- 2005                 |
| Matrix Completion  | IterativeSVD [[2]](#ref2) | BIOINFORMATICS -- 2001       |
| Pattern Search     | TKCM [[11]](#ref11)       | EDBT -- 2017                 |
| Pattern Search     | ST-MVL [[9]](#ref9)       | IJCAI -- 2016                |
| Pattern Search     | DynaMMo [[10]](#ref10)    | KDD -- 2009                  |
| Machine Learning   | IIM [[12]](#ref12)        | ICDE -- 2019                 |
| Machine Learning   | XGBI [[13]](#ref13)       | KDD -- 2016                  |
| Machine Learning   | Mice [[14]](#ref14)       | Statistical Software -- 2011 |
| Machine Learning   | MissForest [[15]](#ref15) | BioInformatics -- 2011       |
| Statistics         | KNNImpute                 | -                            |
| Statistics         | Interpolation             | -                            |
| Statistics         | Min Impute                | -                            |
| Statistics         | Zero Impute               | -                            |
| Statistics         | Mean Impute               | -                            |
| Statistics         | Mean Impute By Series     | -                            |

---

### **Quick Navigation**

- **Deployment**  
  - [System Requirements](#system-requirements)  
  - [Installation](#installation)  

- **Code Snippets**  
  - [Data Preprocessing](#loading-and-preprocessing)  
  - [Contamination](#contamination)  
  - [Imputation](#imputation)  
  - [Auto-ML](#parameterization)  
  - [Explainer](#explainer)  
  - [Downstream Evaluation](#downstream)
  - [Benchmark](#benchmark)  

- **Contribute**  
  - [Integration Guide](#integration)  

- **Additional Information**  
  - [References](#references)  
  - [Core Contributors](#core-contributors)  



---

## System Requirements

ImputeGAP is compatible with Python>=3.10 (except 3.13) and Unix-compatible environment.

<i>To create and set up an environment with Python 3.12, please refer to the [installation guide](https://github.com/eXascaleInfolab/ImputeGAP/tree/main/procedure/installation).</i>

---


## Installation



To install the latest version of ImputeGAP from PyPI, run the following command:

```bash
pip install imputegap
``` 

Alternatively, you can install the library from source:

```bash
git init
git clone https://github.com/eXascaleInfolab/ImputeGAP
cd ./ImputeGAP
pip install -e .
```


---
## Loading and Preprocessing

ImputeGAP comes with several time series datasets. The list of datasets is described [here](https://imputegap.readthedocs.io/en/latest/datasets.html).

As an example, we start by using eeg-alcohol, a standard dataset composed of individuals with a genetic predisposition to alcoholism. The dataset contains measurements from 64 electrodes placed on subject’s scalps, sampled at 256 Hz (3.9-ms epoch) for 1 second. The dimensions of the dataset are 64 series, each containing 256 values.


### Example Loading
You can find this example in the file [`runner_loading.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_loading.py).

```python
from imputegap.recovery.manager import TimeSeries
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()
print(f"ImputeGAP datasets : {ts.datasets}")

# load and normalize the dataset from file or from the code
ts.load_series(utils.search_path("eeg-alcohol"))
ts.normalize(normalizer="z_score")

# plot and print a subset of time series
ts.plot(input_data=ts.data, nbr_series=9, nbr_val=100, save_path="./imputegap_assets")
ts.print(nbr_series=9, nbr_val=100)
```

---

## Contamination
We now describe how to simulate missing values in the loaded dataset. ImputeGAP implements eight different missingness patterns.


For more details, please refer to the documentation in this [page](https://imputegap.readthedocs.io/en/latest/patterns.html).
<br></br>

### Example Contamination
You can find this example in the file [`runner_contamination.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_contamination.py).


As example, we show how to contaminate the eeg-alcohol dataset with the MCAR pattern:

```python
from imputegap.recovery.manager import TimeSeries
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()
print(f"Missingness patterns : {ts.patterns}")

# load and normalize the dataset
ts.load_series(utils.search_path("eeg-alcohol"))
ts.normalize(normalizer="z_score")

# contaminate the time series with MCAR pattern
ts_m = ts.Contamination.mcar(ts.data, rate_dataset=0.2, rate_series=0.4, block_size=10, seed=True)

# [OPTIONAL] plot the contaminated time series
ts.plot(ts.data, ts_m, nbr_series=9, subplot=True, save_path="./imputegap_assets")
```

---

## Imputation

In this section, we will illustrate how to impute the contaminated time series. Our library implements five families of imputation algorithms. Statistical, Machine Learning, Matrix Completion, Deep Learning, and Pattern Search Methods.
The list of algorithms and their optimizers is described [here](https://imputegap.readthedocs.io/en/latest/algorithms.html).

### Example Imputation
You can find this example in the file [`runner_imputation.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_imputation.py).

Imputation can be performed using either default values or user-defined values. To specify the parameters, please use a dictionary in the following format:

```python
params = {"param_1": 42.1, "param_2": "some_string", "params_3": True}
```

Let's illustrate the imputation using the CDRec Algorithm from the Matrix Completion family.

```python
from imputegap.recovery.imputation import Imputation
from imputegap.recovery.manager import TimeSeries
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()
print(f"Imputation algorithms : {ts.algorithms}")

# load and normalize the dataset
ts.load_series(utils.search_path("eeg-alcohol"))
ts.normalize(normalizer="z_score")

# contaminate the time series
ts_m = ts.Contamination.mcar(ts.data)

# impute the contaminated series
imputer = Imputation.MatrixCompletion.CDRec(ts_m)
imputer.impute()

# compute and print the imputation metrics
imputer.score(ts.data, imputer.recov_data)
ts.print_results(imputer.metrics)

# plot the recovered time series
ts.plot(input_data=ts.data, incomp_data=ts_m, recov_data=imputer.recov_data, nbr_series=9, subplot=True,
        save_path="./imputegap_assets")
```

---


## Parameterization
The Optimizer component manages algorithm configuration and hyperparameter tuning. To invoke the tuning process, users need to specify the optimization option during the Impute call by selecting the appropriate input for the algorithm. The parameters are defined by providing a dictionary containing the ground truth, the chosen optimizer, and the optimizer's options. Several search algorithms are available, including those provided by [Ray Tune](https://docs.ray.io/en/latest/tune/index.html>).

### Example Auto-ML
You can find this example in the file [`runner_optimization.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_optimization.py).

Let's illustrate the imputation using the CDRec Algorithm and Ray-Tune AutoML:

```python
from imputegap.recovery.imputation import Imputation
from imputegap.recovery.manager import TimeSeries
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()
print(f"AutoML Optimizers : {ts.optimizers}")

# load and normalize the dataset
ts.load_series(utils.search_path("eeg-alcohol"))
ts.normalize(normalizer="z_score")

# contaminate and impute the time series
ts_m = ts.Contamination.mcar(ts.data)
imputer = Imputation.MatrixCompletion.CDRec(ts_m)

# use Ray Tune to fine tune the imputation algorithm
imputer.impute(user_def=False, params={"input_data": ts.data, "optimizer": "ray_tune"})

# compute and print the imputation metrics
imputer.score(ts.data, imputer.recov_data)
ts.print_results(imputer.metrics)

# plot the recovered time series
ts.plot(input_data=ts.data, incomp_data=ts_m, recov_data=imputer.recov_data, nbr_series=9, subplot=True,
        save_path="./imputegap_assets", display=True)

# save hyperparameters
utils.save_optimization(optimal_params=imputer.parameters, algorithm=imputer.algorithm, dataset="eeg-alcohol",
                        optimizer="ray_tune")
```

---


## Explainer

ImputeGAP provides insights into the algorithm’s behavior by identifying the features that impact the most the imputation results. It trains a regression model to predict imputation results across various methods and uses SHapley Additive exPlanations ([SHAP](https://shap.readthedocs.io/en/latest/)) to reveal how different time series features influence the model’s predictions.
The documentation for the explainer is described [here](https://imputegap.readthedocs.io/en/latest/explainer.html).


### Example Explainer
You can find this example in the file [`runner_explainer.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_explainer.py).

Let’s illustrate the explainer using the CDRec Algorithm and MCAR missingness pattern:


```python
from imputegap.recovery.manager import TimeSeries
from imputegap.recovery.explainer import Explainer
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()

# load and normalize the dataset
ts.load_series(utils.search_path("eeg-alcohol"))
ts.normalize(normalizer="z_score")

# configure the explanation
shap_values, shap_details = Explainer.shap_explainer(input_data=ts.data, 
                                                     extractor="pycatch", 
                                                     pattern="mcar", 
                                                     file_name=ts.name,
                                                     algorithm="CDRec")

# print the impact of each feature
Explainer.print(shap_values, shap_details)
```

---


## Downstream
ImputeGAP includes a dedicated module for systematically evaluating the impact of data imputation on downstream tasks. Currently, forecasting is the primary supported task, with plans to expand to additional applications in the future. The example below demonstrates how to define the forecasting task and specify Prophet as the predictive model
The documentation for the downstream evaluation is described [here](https://imputegap.readthedocs.io/en/latest/downstream.html).

Below is an example of how to call the downstream process for the model Prophet by defining a dictionary for the evaluator and selecting the model:


### Example Downstream
You can find this example in the file [`runner_downstream.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_downstream.py).

Below is an example of how to call the downstream process for the model Prophet by defining a dictionary for the evaluator and selecting the model:

```python
from imputegap.recovery.imputation import Imputation
from imputegap.recovery.manager import TimeSeries
from imputegap.tools import utils

# initialize the time series object
ts = TimeSeries()
print(f"ImputeGAP downstream models for forcasting : {ts.downstream_models}")

# load and normalize the dataset
ts.load_series(utils.search_path("forecast-economy"))
ts.normalize(normalizer="min_max")

# contaminate the time series
ts_m = ts.Contamination.aligned(ts.data, rate_series=0.8)

# define and impute the contaminated series
imputer = Imputation.MatrixCompletion.CDRec(ts_m)
imputer.impute()

# compute and print the downstream results
downstream_config = {"task": "forecast", "model": "hw-add"}
imputer.score(ts.data, imputer.recov_data, downstream=downstream_config)
ts.print_results(imputer.downstream_metrics, algorithm=imputer.algorithm)
```



---


## Benchmark

ImputeGAP can serve as a common test-bed for comparing the effectiveness and efficiency of time series imputation algorithms[[33]](#ref33) . Users have full control over the benchmark by customizing various parameters, including the list of datasets to evaluate, the algorithms to compare, the choice of optimizer to fine-tune the algorithms on the chosen datasets, the missingness patterns, and the range of missing rates.
The documentation for the benchmark is described [here](https://imputegap.readthedocs.io/en/latest/benchmark.html).


### Example Benchmark
You can find this example in the file [`runner_benchmark.py`](https://github.com/eXascaleInfolab/ImputeGAP/blob/main/imputegap/runner_benchmark.py).

The benchmarking module can be utilized as follows:

```python
from imputegap.recovery.benchmark import Benchmark

save_dir = "./analysis"
nbr_run = 2

datasets = ["eeg-alcohol", "eeg-reading"]

optimizer = {"optimizer": "ray_tune", "options": {"n_calls": 1, "max_concurrent_trials": 1}}
optimizers = [optimizer]

algorithms = ["MeanImpute", "CDRec", "STMVL", "IIM", "MRNN"]

patterns = ["mcar"]

range = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]

# launch the evaluation
list_results, sum_scores = Benchmark().eval(algorithms=algorithms, datasets=datasets, patterns=patterns, x_axis=range, optimizers=optimizers, save_dir=save_dir, runs=nbr_run)
```

---

## Integration
To add your own imputation algorithm in Python or C++, please refer to the detailed [integration guide](https://github.com/eXascaleInfolab/ImputeGAP/tree/main/procedure/integration).


---


## Articles


Mourad Khayati, Alberto Lerner, Zakhar Tymchenko, Philippe Cudre-Mauroux: Mind the Gap: An Experimental Evaluation of Imputation of Missing Values Techniques in Time Series. Proc. VLDB Endow. 13(5): 768-782 (2020)

Mourad Khayati, Quentin Nater, Jacques Pasquier: ImputeVIS: An Interactive Evaluator to Benchmark Imputation Techniques for Time Series Data. Proc. VLDB Endow. 17(12): 4329-4332 (2024)

---





## Citing

If you use ImputeGAP in your research, please cite the paper:

```
@article{nater2025imputegap,
  title = {ImputeGAP: A Comprehensive Library for Time Series Imputation},
  author = {Nater, Quentin and Khayati, Mourad and Pasquier, Jacques},
  year = {2025},
  eprint = {2503.15250},
  archiveprefix = {arXiv},
  primaryclass = {cs.LG},
  url = {https://arxiv.org/abs/2503.15250}
}
```
---

## Core Contributors

<table align="center">
  <tr>
    <td align="center">
      <a href="https://exascale.info/members/quentin-nater/">
        <img src="https://www.naterscreations.com/d/quentin_nater.png" alt="Quentin Nater - ImputeGAP" width="100" height="100" />
      </a>
    </td>
    <td align="center">
      <a href="https://exascale.info/members/mourad-khayati/">
        <img src="https://www.naterscreations.com/d/mourad_khayati.png" alt="Mourad Khayati - ImputeGAP" width="100" height="100"  />
      </a>
    </td>
  </tr>
  <tr>
    <td align="center">
      Quentin Nater  
    </td>
    <td align="center">
      Mourad Khayati
    </td>
  </tr>
</table>



---


## References

<a name="ref1"></a>
[1]: Mourad Khayati, Philippe Cudré-Mauroux, Michael H. Böhlen: Scalable recovery of missing blocks in time series with high and low cross-correlations. Knowl. Inf. Syst. 62(6): 2257-2280 (2020)

<a name="ref2"></a>
[2]: Olga G. Troyanskaya, Michael N. Cantor, Gavin Sherlock, Patrick O. Brown, Trevor Hastie, Robert Tibshirani, David Botstein, Russ B. Altman: Missing value estimation methods for DNA microarrays. Bioinform. 17(6): 520-525 (2001)

<a name="ref3"></a>
[3]: Dejiao Zhang, Laura Balzano: Global Convergence of a Grassmannian Gradient Descent Algorithm for Subspace Estimation. AISTATS 2016: 1460-1468

<a name="ref4"></a>
[4]: Xianbiao Shu, Fatih Porikli, Narendra Ahuja: Robust Orthonormal Subspace Learning: Efficient Recovery of Corrupted Low-Rank Matrices. CVPR 2014: 3874-3881

<a name="ref5"></a>
[5]: Spiros Papadimitriou, Jimeng Sun, Christos Faloutsos: Streaming Pattern Discovery in Multiple Time-Series. VLDB 2005: 697-708

<a name="ref6"></a>
[6]: Rahul Mazumder, Trevor Hastie, Robert Tibshirani: Spectral Regularization Algorithms for Learning Large Incomplete Matrices. J. Mach. Learn. Res. 11: 2287-2322 (2010)

<a name="ref7"></a>
[7]: Jian-Feng Cai, Emmanuel J. Candès, Zuowei Shen: A Singular Value Thresholding Algorithm for Matrix Completion. SIAM J. Optim. 20(4): 1956-1982 (2010)

<a name="ref8"></a>
[8]: Hsiang-Fu Yu, Nikhil Rao, Inderjit S. Dhillon: Temporal Regularized Matrix Factorization for High-dimensional Time Series Prediction. NIPS 2016: 847-855

<a name="ref9"></a>
[9]: Xiuwen Yi, Yu Zheng, Junbo Zhang, Tianrui Li: ST-MVL: Filling Missing Values in Geo-Sensory Time Series Data. IJCAI 2016: 2704-2710

<a name="ref10"></a>
[10]: Lei Li, James McCann, Nancy S. Pollard, Christos Faloutsos: DynaMMo: mining and summarization of coevolving sequences with missing values. 507-516

<a name="ref11"></a>
[11]: Kevin Wellenzohn, Michael H. Böhlen, Anton Dignös, Johann Gamper, Hannes Mitterer: Continuous Imputation of Missing Values in Streams of Pattern-Determining Time Series. EDBT 2017: 330-341

<a name="ref12"></a>
[12]: Aoqian Zhang, Shaoxu Song, Yu Sun, Jianmin Wang: Learning Individual Models for Imputation (Technical Report). CoRR abs/2004.03436 (2020)

<a name="ref13"></a>
[13]: Tianqi Chen, Carlos Guestrin: XGBoost: A Scalable Tree Boosting System. KDD 2016: 785-794

<a name="ref14"></a>
[14]: Royston Patrick , White Ian R.: Multiple Imputation by Chained Equations (MICE): Implementation in Stata. Journal of Statistical Software 2010: 45(4), 1–20.

<a name="ref15"></a>
[15]: Daniel J. Stekhoven, Peter Bühlmann: MissForest - non-parametric missing value imputation for mixed-type data. Bioinform. 28(1): 112-118 (2012)

<a name="ref22"></a>
[22]: Jinsung Yoon, William R. Zame, Mihaela van der Schaar: Estimating Missing Data in Temporal Data Streams Using Multi-Directional Recurrent Neural Networks. IEEE Trans. Biomed. Eng. 66(5): 1477-1490 (2019)

<a name="ref23"></a>
[23]: Wei Cao, Dong Wang, Jian Li, Hao Zhou, Lei Li, Yitan Li: BRITS: Bidirectional Recurrent Imputation for Time Series. NeurIPS 2018: 6776-6786

<a name="ref24"></a>
[24]: Parikshit Bansal, Prathamesh Deshpande, Sunita Sarawagi: Missing Value Imputation on Multidimensional Time Series. Proc. VLDB Endow. 14(11): 2533-2545 (2021)

<a name="ref25"></a>
[25]: Xiao Li, Huan Li, Hua Lu, Christian S. Jensen, Varun Pandey, Volker Markl: Missing Value Imputation for Multi-attribute Sensor Data Streams via Message Propagation (Extended Version). CoRR abs/2311.07344 (2023)

<a name="ref26"></a>
[26]: Mingzhe Liu, Han Huang, Hao Feng, Leilei Sun, Bowen Du, Yanjie Fu: PriSTI: A Conditional Diffusion Framework for Spatiotemporal Imputation. ICDE 2023: 1927-1939

<a name="ref27"></a>
[27]: Kohei Obata, Koki Kawabata, Yasuko Matsubara, Yasushi Sakurai: Mining of Switching Sparse Networks for Missing Value Imputation in Multivariate Time Series. KDD 2024: 2296-2306

<a name="ref28"></a>
[28]: Jinsung Yoon, James Jordon, Mihaela van der Schaar: GAIN: Missing Data Imputation using Generative Adversarial Nets. ICML 2018: 5675-5684

<a name="ref29"></a>
[29]: Andrea Cini, Ivan Marisca, Cesare Alippi: Multivariate Time Series Imputation by Graph Neural Networks. CoRR abs/2108.00298 (2021)

<a name="ref30"></a>
[30]: Shikai Fang, Qingsong Wen, Yingtao Luo, Shandian Zhe, Liang Sun: BayOTIDE: Bayesian Online Multivariate Time Series Imputation with Functional Decomposition. ICML 2024

<a name="ref31"></a>
[31]: Liang Wang, Simeng Wu, Tianheng Wu, Xianping Tao, Jian Lu: HKMF-T: Recover From Blackouts in Tagged Time Series With Hankel Matrix Factorization. IEEE Trans. Knowl. Data Eng. 33(11): 3582-3593 (2021)

<a name="ref32"></a>
[32]: Xiaodan Chen, Xiucheng Li, Bo Liu, Zhijun Li: Biased Temporal Convolution Graph Network for Time Series Forecasting with Missing Values. ICLR 2024

<a name="ref33"></a>
[33] Mourad Khayati, Alberto Lerner, Zakhar Tymchenko, Philippe Cudré-Mauroux:
Mind the Gap: An Experimental Evaluation of Imputation of Missing Values Techniques in Time Series. Proc. VLDB Endow. 13(5): 768-782 (2020)

<a name="ref33"></a>
[34] Mourad Khayati, Quentin Nater, Jacques Pasquier: ImputeVIS: An Interactive Evaluator to Benchmark Imputation Techniques for Time Series Data. Proc. VLDB Endow. 17(12): 4329-4332 (2024)