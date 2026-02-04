# Conceptual Design of Green Propulsive Systems Using Reinforcement Learning

**Abstract**: Hybrid-electric powertrains offer a solution to significantly reduce aircraft emissions in flight. This study presents a method for automatically generating hybrid-electric architectures and optimizing two different objective functions by evaluating the control parameters of each unique architecture using reinforcement learning. Two ATR 72-600 configurations serve as reference aircraft, and three technology levels are considered. When maximizing the ratio of effective radiative forcing to payload mass, the results indicate that the optimal design is sensitive to both aircraft configuration and technology level; however, architectures fully powered by hydrogen fuel cells are preferred when feasible. When maximizing payload and applying the Flightpath 2050 sustainability goals as constraints, the optimal architecture shifts to one in which conventional jet fuel and hydrogen are combusted in a gas turbine to power the primary propulsive line, while the majority of the power is delivered by the fuel cells to an auxiliary propulsive line. Compared with a conventional architecture, this design reduces CO2 and NOx emissions by up to 74% and 86%, respectively, while reducing payload mass by only 24%.

---------------------------------------------------------------
### Installation
Create a virtual environment and use

```commandline
pip install -r requirements.txt
```
to install the required packages. <br /> <br />
To run on GPU instead of CPU use:

```commandline
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```
or visit https://pytorch.org/get-started/locally/ for more information.


### Training initialization

Hyperparameters and number of steps can be changed in the function SACtraining() in Training.py. <br />

Then run initialize_training() and specify the runs, aircraft configuration, objective function, technology level, directory). <br />
If no training directory exists yet, it will be automatically created.

### Saving training data

Run saving_data() in Saving_data.py to save the training data in a .json file which can be used for plotting. <br />
Again specify the aircraft configuration and the objective function, the to be evaluated models, the directory, technology level, number of samples (1 is deterministic evaluation), deterministic or stochastic evaluation, if random samples should be generated, and if the data should be saved. <br />

The highest reward of each model for each unique architecture will also be printed. <br />
Printing variables such as:

```commandline
self.actions
self.x
self.ENERGY_SOURCE_DATA
self.COMPONENT_DATA
payload
self.erf
self.co2_emissions
self.nox_emissions
```
provides more insights into each sampled design.
### Plotting

Run any function in Plotting.py to generate the graphs in the article.