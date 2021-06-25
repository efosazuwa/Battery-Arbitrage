# Battery Arbitrage
## Use Colab

<a href="https://colab.research.google.com/drive/1zZWuUgP-zF0yl_ySi4abJbjNTEEID0rm?usp=sharing"><img align="left" src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" title="Open in Google Colaboratory"></a>  
</br>
Using Google Colab is probably the easiest and most straight forward to see all of my work on this particular use case. If you click on the link above you'll want to upload the relevant data to the copy of the notebook you will open. The csv i used can be found in the following file path from this repository:  

    'data/20170801damlbmp_zone_csv/20170801damlbmp_zone.csv'  

## Running Locally

You will want to start up a new virtual enviornment and run:

    pip install -r requirements.txt  

This should be the minimally necessary packages to run the python file or the notebook.  

To run the notebook just go to the command line and enter the command.

    jupyter notebook Battery_Arbitrage.ipynb  

The function in the arbitrage_model.py is useful for testing many different types of configurations. Within the file is a function called 'battery_arbitrage' that takes the parameters:
- max charge
- max discharge
- battery capacity
- round trip efficiency
- daily discharge limit  

With these parameters it builds a battery charging profile and outputs a tuple of results that are detailed in the functions docstring.
## Insights/Results
![Image of Yaktocat](img/plot.png)
This is the charge profile created with the use case as follows:
- max charge = max discharge = 200 KW
- battery capacity = 200 KWh
- round trip efficiency = .85
- daily discharge limit = 200KWh  
The LBMP comes from the New York Independent System Operator(NYISO) and this specific case use the 24 day ahead spot price from 08/01/2017  

We can see that the battery chooses the three lowest lmbp's to charge and then holds its charge until the lmbp reaches it's highest point to sell.

An interesting point is that the less than 100% efficiency of the battery storage results in the battery charging for more than the two time steps it should be necessary to charge.

Overall this is a straight forward play example that reaches an optimal solution to maximize profit.
## Next Steps
Some additional parameters that could be added to the model to make it more realistic are:
- ramp rate
- separate buy and sell price
- pair with forecasting for a longer arbitrage horizon
- multiple batteries
    - network effects
