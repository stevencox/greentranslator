# Green Team Biomedical Data Translator

This package provides an interface for interacting with Green team services:
- Clinical
- Environmental
- Medical-BioChemical

## Questions

1. Among pediatric patients with an 'asthma-like phenotype', is exposure to PM2.5 and ozone correlated with responsiveness to treatment medication?
2. What protein (gene) targets and biological pathways are activated or inhibited by PM2.5 and ozone exposure?
3. What pediatric medications are available that act on the protein (gene) targets and biological pathways that are activated or inhibited by PM2.5 and ozone exposure?
4. Which medications are currently prescribed to pediatric patients with an asthma-like phenotype who are responsive to treatment despite high PM2.5 and ozone exposures?
5. What is the protein (gene) target and biological pathway of medications currently prescribed to patients with an asthma-like phenotype who are responsive to treatment despite high PM2.5 and ozone exposures?
6. What if PM2.5 and ozone exposures are high in pediatric patients with an asthma-like phenotype and good clinical outcomes? What differentiates these patients from those who have high environmental exposures and poor clinical outcomes? 

## Approach

We have a smartAPI for the Exposures service and another is under active development for the Clinical service.

We're determining which operations on the Medical BioChemical data should be sourced from existing services like [mygene.info](http://mygene.info/v3/api) vs sourced from data sets like chem2bio2rdf or some existing smartAPI. Depending on the outcome, we may create a third smartAPI for medical-biochemical knowledge or source the data externally.

### Installation

For ease of use at the Hackathon, we're providing a simple Python library interface to Green team services. It can be installed and tested like this:
   ```
   pip --no-cache install greentranslator
   python -m unittest greentranslator.api
   ```
   
After this, Jupyter can be added like this:

```
pip install jupyter
```
And run with 
```
jupyter notebook --ip=0.0.0.0
```

The current notebook exercises existing services to gather building blocks for executing the queries above.
